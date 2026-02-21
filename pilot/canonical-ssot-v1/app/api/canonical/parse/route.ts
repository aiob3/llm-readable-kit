import { NextResponse } from "next/server";
import { parseCanonicalDsl } from "@/src/canonical/parser";
import { normalizeCanonicalRecord } from "@/src/canonical/normalize";
import { validateCanonicalJson } from "@/src/canonical/validator";
import { toErrorPayload } from "@/src/canonical/errors";

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as { dsl: string };
    const parsed = parseCanonicalDsl(body.dsl);
    const normalized = normalizeCanonicalRecord(parsed);
    validateCanonicalJson(normalized);

    return NextResponse.json({ ok: true, normalized });
  } catch (error) {
    return NextResponse.json({ ok: false, error: toErrorPayload(error) }, { status: 400 });
  }
}
