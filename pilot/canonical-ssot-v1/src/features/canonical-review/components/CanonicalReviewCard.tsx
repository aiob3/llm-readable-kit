import type { CanonicalContextV1 } from "@/src/shared/schema/generated-types";

interface CanonicalReviewCardProps {
  payload: CanonicalContextV1 | null;
}

export function CanonicalReviewCard({ payload }: CanonicalReviewCardProps) {
  return (
    <section className="panel">
      <h2>Semantic Review</h2>
      {!payload ? (
        <p>Execute parse para visualizar o JSON normalizado.</p>
      ) : (
        <>
          <p>
            Version: <strong>{payload.schema_version}</strong>
          </p>
          <div className="kv code">
            {Object.entries(payload.event_layer).map(([key, value]) => (
              <div key={key}>
                <strong>{key}</strong>: {value}
              </div>
            ))}
          </div>
        </>
      )}
    </section>
  );
}
