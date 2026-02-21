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
      {/* ── System header — Neural Cartography identity ── */}
      <header className="sys-header">
        <div className="sys-header-meta">
          <span className="sys-node-dot" />
          <span className="sys-node-uri">node://canonical.ssot.v1</span>
          <span className="mds-badge">PILOT</span>
        </div>

        <h1 className="sys-title">
          canonical<span className="sys-title-sep">::</span>ssot
          <span className="sys-title-version">v1</span>
        </h1>

        <p className="sys-subtitle">
          DSL autoral
          <span className="sys-arrow">→</span>
          JSON normalizado
          <span className="sys-arrow">→</span>
          idempotência
          <span className="sys-arrow">→</span>
          event log
        </p>
      </header>

      {errorText ? (
        <div className="error error-block">{errorText}</div>
      ) : null}

      <div className="grid grid-with-gap">
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

      <div className="grid grid-with-gap">
        <CanonicalIAMCard payload={payload} />
        <CanonicalTimeline rows={timeline} />
      </div>
    </main>
  );
}
