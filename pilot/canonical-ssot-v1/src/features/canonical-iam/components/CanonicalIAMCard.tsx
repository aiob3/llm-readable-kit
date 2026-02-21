import type { CanonicalContextV1 } from "@/src/shared/schema/generated-types";

interface CanonicalIAMCardProps {
  payload: CanonicalContextV1 | null;
}

export function CanonicalIAMCard({ payload }: CanonicalIAMCardProps) {
  return (
    <section className="panel">
      <h2>IAM Resolution</h2>
      {!payload ? (
        <p>Nenhuma resolução IAM disponível.</p>
      ) : (
        <div className="code">
          <p>
            role_code: <strong>{payload.catalog_resolution.role_code}</strong> ({payload.catalog_resolution.role_label})
          </p>
          <p>
            zone_level: <strong>{payload.catalog_resolution.zone_level}</strong> ({payload.catalog_resolution.zone_label})
          </p>
          <div className="kv">
            {Object.entries(payload.iam_layer).map(([key, value]) => (
              <div key={key}>
                <strong>{key}</strong>: {value}
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
