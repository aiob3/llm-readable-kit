"use client";

import { useMemo, useState } from "react";
import { CanonicalInputForm } from "@/src/features/canonical-input/components/CanonicalInputForm";
import { CanonicalReviewCard } from "@/src/features/canonical-review/components/CanonicalReviewCard";
import { CanonicalIAMCard } from "@/src/features/canonical-iam/components/CanonicalIAMCard";
import { CanonicalTimeline } from "@/src/features/canonical-timeline/components/CanonicalTimeline";
import { SAMPLE_DSL } from "@/src/features/canonical-input/sample";
import type { CanonicalContextV1 } from "@/src/shared/schema/generated-types";
import { ERROR_HELP } from "@/src/shared/validation/error-map";

interface ApiError {
  code: string;
  message: string;
}

interface TimelineRow {
  id: number;
  idempotency_key: string;
  payload_hash: string;
  created_at: string;
  source: string;
}

export default function HomePage() {
  const [dsl, setDsl] = useState("");
  const [payload, setPayload] = useState<CanonicalContextV1 | null>(null);
  const [timeline, setTimeline] = useState<TimelineRow[]>([]);
  const [error, setError] = useState<ApiError | null>(null);
  const [loading, setLoading] = useState(false);

  const errorText = useMemo(() => {
    if (!error) {
      return null;
    }
    const help = ERROR_HELP[error.code] ?? "Sem classificação específica para este erro.";
    return `${error.code}: ${error.message} — ${help}`;
  }, [error]);

  async function refreshTimeline() {
    const response = await fetch("/api/canonical/events");
    const body = (await response.json()) as { ok: boolean; data: TimelineRow[] };
    if (body.ok) {
      setTimeline(body.data);
    }
  }

  async function handleParse() {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/canonical/parse", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ dsl })
      });

      const body = (await response.json()) as {
        ok: boolean;
        normalized?: CanonicalContextV1;
        error?: ApiError;
      };

      if (!body.ok || !body.normalized) {
        setPayload(null);
        setError(body.error ?? { code: "E_UNKNOWN", message: "Unknown parse error" });
        return;
      }

      setPayload(body.normalized);
      await refreshTimeline();
    } finally {
      setLoading(false);
    }
  }

  async function handlePersist() {
    if (!payload) {
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/canonical/events", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ payload, source: "canonical-web-ui" })
      });
      const body = (await response.json()) as { ok: boolean; error?: ApiError };
      if (!body.ok) {
        setError(body.error ?? { code: "E_UNKNOWN", message: "Persist failed" });
        return;
      }
      await refreshTimeline();
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <header style={{ marginBottom: "1rem" }}>
        <h1>Canonical SSOT v1 Pilot</h1>
        <p>
          DSL textual autoral -&gt; JSON normalizado -&gt; idempotência -&gt; event log (Postgres first, fallback memory).
        </p>
      </header>

      {errorText ? <div className="error">{errorText}</div> : null}

      <div className="grid" style={{ marginTop: "1rem" }}>
        <CanonicalInputForm
          dsl={dsl}
          onChange={setDsl}
          onLoadSample={() => setDsl(SAMPLE_DSL)}
          onParse={handleParse}
          onPersist={handlePersist}
          loading={loading}
          canPersist={Boolean(payload)}
        />
        <CanonicalReviewCard payload={payload} />
      </div>

      <div className="grid" style={{ marginTop: "1rem" }}>
        <CanonicalIAMCard payload={payload} />
        <CanonicalTimeline rows={timeline} />
      </div>
    </main>
  );
}
