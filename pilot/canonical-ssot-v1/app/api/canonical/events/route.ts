import { NextResponse } from "next/server";
import { persistCanonicalEvent, listInMemoryEvents } from "@/src/server/eventRepository";
import { toErrorPayload } from "@/src/canonical/errors";
import type { CanonicalNormalized } from "@/src/canonical/types";

export async function GET() {
  return NextResponse.json({
    ok: true,
    data: listInMemoryEvents()
  });
}

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as { payload: CanonicalNormalized; source?: string };
    const row = await persistCanonicalEvent(body.payload, body.source ?? "canonical-web");

    return NextResponse.json({ ok: true, row });
  } catch (error) {
    return NextResponse.json({ ok: false, error: toErrorPayload(error) }, { status: 400 });
  }
}
