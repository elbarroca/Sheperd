import { NextResponse } from "next/server";

const API_BASE = (process.env.RESEARCH_API_BASE_URL ?? "http://127.0.0.1:8787").replace(/\/$/u, "");

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ run_id: string }> },
): Promise<Response> {
  const { run_id: runId } = await params;
  try {
    const response = await fetch(
      `${API_BASE}/api/reports/weekly/${encodeURIComponent(runId)}/markdown`,
      { cache: "no-store" },
    );
    if (!response.ok) {
      return NextResponse.json(
        { error: `Research API returned ${response.status}` },
        { status: response.status },
      );
    }
    const markdown = await response.text();
    return new Response(markdown, {
      status: 200,
      headers: {
        "Content-Type": "text/markdown; charset=utf-8",
        "Content-Disposition": `inline; filename="${runId.replace(/[^a-zA-Z0-9_-]/gu, "_")}.md"`,
        "Cache-Control": "no-store",
      },
    });
  } catch {
    return NextResponse.json(
      { error: "Research API is unavailable" },
      { status: 503 },
    );
  }
}
