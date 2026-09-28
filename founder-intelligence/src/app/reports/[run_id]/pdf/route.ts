import { createHmac } from "node:crypto";
import { NextResponse } from "next/server";

const API_BASE = (process.env.RESEARCH_API_BASE_URL ?? "http://127.0.0.1:8787").replace(
  /\/$/u,
  "",
);

export const dynamic = "force-dynamic";

export async function GET(
  request: Request,
  { params }: { params: Promise<{ run_id: string }> },
): Promise<Response> {
  const { run_id: runId } = await params;
  const secret = process.env.REPORT_LINK_SIGNING_SECRET;
  if (!secret) {
    return NextResponse.json(
      { status: "unavailable", error_code: "pdf_delivery_not_configured" },
      { status: 503 },
    );
  }
  const configuredTtl = Number(process.env.REPORT_URL_TTL_SECONDS ?? "604800");
  const ttl = Number.isFinite(configuredTtl) && configuredTtl > 0
    ? Math.floor(configuredTtl)
    : 604800;
  const expires = Math.floor(Date.now() / 1000) + ttl;
  const signature = createHmac("sha256", secret)
    .update(`${runId}:${expires}`)
    .digest("hex");
  const archiveScope = new URL(request.url).searchParams.get("archive_scope");
  const archiveQuery = archiveScope === "archived" || archiveScope === "all"
    ? `&archive_scope=${archiveScope}`
    : "";
  try {
    const response = await fetch(
      `${API_BASE}/api/reports/weekly/${encodeURIComponent(runId)}/pdf?expires=${expires}&signature=${signature}${archiveQuery}`,
      { cache: "no-store" },
    );
    const headers = new Headers();
    headers.set(
      "Content-Type",
      response.headers.get("content-type") ?? "application/pdf",
    );
    headers.set("Cache-Control", "private, no-store");
    const contentDisposition = response.headers.get("content-disposition");
    if (contentDisposition) headers.set("Content-Disposition", contentDisposition);
    const etag = response.headers.get("etag");
    if (etag) headers.set("ETag", etag);
    return new Response(response.body, {
      status: response.status,
      headers,
    });
  } catch {
    return NextResponse.json(
      { status: "unavailable", error_code: "research_api_unavailable" },
      { status: 503 },
    );
  }
}
