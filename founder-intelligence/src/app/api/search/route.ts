import { type NextRequest, NextResponse } from "next/server";
import { searchKnowledge } from "@/lib/knowledge";

export async function GET(request: NextRequest): Promise<NextResponse> {
  const query = request.nextUrl.searchParams.get("q")?.trim() ?? "";
  if (query.length < 2 || query.length > 160) {
    return NextResponse.json(
      { error: "Query must contain between 2 and 160 characters." },
      { status: 400, headers: { "Cache-Control": "no-store" } },
    );
  }
  return NextResponse.json(
    { query, results: searchKnowledge(query) },
    { headers: { "Cache-Control": "private, no-store" } },
  );
}
