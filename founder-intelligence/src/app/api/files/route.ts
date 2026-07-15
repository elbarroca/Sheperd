import { type NextRequest, NextResponse } from "next/server";
import { getKnowledgeFile } from "@/lib/knowledge";

const MAX_PATH_LENGTH = 300;

export async function GET(request: NextRequest): Promise<NextResponse> {
  const path = request.nextUrl.searchParams.get("path")?.trim() ?? "";
  if (path.length === 0 || path.length > MAX_PATH_LENGTH) {
    return NextResponse.json(
      { error: "A valid source path is required." },
      { status: 400, headers: { "Cache-Control": "no-store" } },
    );
  }

  const file = getKnowledgeFile(path);
  if (!file) {
    return NextResponse.json(
      { error: "That source is not part of the admitted knowledge corpus." },
      { status: 404, headers: { "Cache-Control": "no-store" } },
    );
  }

  return NextResponse.json(
    { file },
    { headers: { "Cache-Control": "private, no-store" } },
  );
}
