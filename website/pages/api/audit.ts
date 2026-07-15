import type { NextApiRequest, NextApiResponse } from "next";
import { Resend } from "resend";

import { createAuditEmailText, parseAuditRequest } from "@/lib/audit-request";

interface ApiResponse {
  ok: boolean;
  message?: string;
}

interface DeliveryConfiguration {
  apiKey: string;
  fromEmail: string;
  toEmail: string;
}

export const config = {
  api: {
    bodyParser: {
      sizeLimit: "16kb",
    },
  },
};

function getDeliveryConfiguration(): DeliveryConfiguration | null {
  const apiKey = process.env.RESEND_API_KEY?.trim();
  const fromEmail = process.env.SHEPERD_AUDIT_FROM_EMAIL?.trim();
  const toEmail = process.env.SHEPERD_AUDIT_TO_EMAIL?.trim();

  if (
    process.env.FORM_DELIVERY_ENABLED !== "true" ||
    !apiKey ||
    !fromEmail ||
    !toEmail
  ) {
    return null;
  }

  return { apiKey, fromEmail, toEmail };
}

export default async function auditHandler(
  request: NextApiRequest,
  response: NextApiResponse<ApiResponse>,
) {
  if (request.method !== "POST") {
    response.setHeader("Allow", "POST");
    response.status(405).json({ ok: false, message: "Method not allowed." });
    return;
  }

  if (request.headers["x-sheperd-form"] !== "audit-request") {
    response.status(403).json({ ok: false, message: "Invalid form request." });
    return;
  }

  const delivery = getDeliveryConfiguration();
  if (!delivery) {
    response.status(503).json({
      ok: false,
      message: "Audit delivery is not configured.",
    });
    return;
  }

  const rawBody: unknown = request.body;
  const parsed = parseAuditRequest(rawBody);
  if (!parsed.success) {
    response.status(400).json({ ok: false, message: parsed.message });
    return;
  }

  if (parsed.data.website) {
    response.status(202).json({ ok: true });
    return;
  }

  try {
    const resend = new Resend(delivery.apiKey);
    const result = await resend.emails.send(
      {
        from: delivery.fromEmail,
        to: [delivery.toEmail],
        replyTo: parsed.data.workEmail,
        subject: `Free container invoice audit — ${parsed.data.company}`,
        text: createAuditEmailText(parsed.data),
      },
      { idempotencyKey: `sheperd-audit-${parsed.data.submissionId}` },
    );

    if (result.error) {
      response.status(502).json({
        ok: false,
        message: "The audit request could not be delivered.",
      });
      return;
    }

    response.status(200).json({ ok: true });
  } catch {
    response.status(502).json({
      ok: false,
      message: "The audit request could not be delivered.",
    });
  }
}
