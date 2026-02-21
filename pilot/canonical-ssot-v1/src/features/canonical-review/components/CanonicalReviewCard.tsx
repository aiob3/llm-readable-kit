import type { CanonicalContextV1 } from "@/src/shared/schema/generated-types";

interface CanonicalReviewCardProps {
  payload: CanonicalContextV1 | null;
}

export function CanonicalReviewCard({ payload }: CanonicalReviewCardProps) {
  return (
    <section className="panel">
      <h2>
        SEMANTIC_REVIEW
        <span className="mds-badge panel-badge-right">event_layer</span>
      </h2>
      {!payload ? (
        <p className="timeline-empty">Execute parse para visualizar o JSON normalizado.</p>
      ) : (
        <>
          <div className="review-schema-version">
            schema_version: <strong>{payload.schema_version}</strong>
          </div>
          <div className="kv code">
            {Object.entries(payload.event_layer).map(([key, value]) => (
              <div key={key}>
                <strong>{key}</strong>: {String(value)}
              </div>
            ))}
          </div>
        </>
      )}
    </section>
  );
}
