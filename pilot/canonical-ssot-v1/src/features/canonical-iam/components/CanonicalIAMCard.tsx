import type { CanonicalContextV1 } from "@/src/shared/schema/generated-types";

interface CanonicalIAMCardProps {
  payload: CanonicalContextV1 | null;
}

export function CanonicalIAMCard({ payload }: CanonicalIAMCardProps) {
  return (
    <section className="panel">
      <h2>
        IAM_RESOLUTION
        <span className="mds-badge panel-badge-right">acl::resolved</span>
      </h2>
      {!payload ? (
        <p className="timeline-empty">Nenhuma resolução IAM disponível.</p>
      ) : (
        <div className="code">
          <div className="iam-field-row">
            <span className="iam-field-key">role_code</span>
            <span className="iam-field-val">{payload.catalog_resolution.role_code}</span>
            <span className="iam-field-label">({payload.catalog_resolution.role_label})</span>
          </div>
          <div className="iam-field-row">
            <span className="iam-field-key">zone_level</span>
            <span className="iam-field-val">{payload.catalog_resolution.zone_level}</span>
            <span className="iam-field-label">({payload.catalog_resolution.zone_label})</span>
          </div>
          <hr className="iam-divider" />
          <div className="kv">
            {Object.entries(payload.iam_layer).map(([key, value]) => (
              <div key={key}>
                <strong>{key}</strong>: {String(value)}
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
