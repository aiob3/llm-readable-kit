interface TimelineRow {
  id: number;
  idempotency_key: string;
  payload_hash: string;
  created_at: string;
  source: string;
}

interface CanonicalTimelineProps {
  rows: TimelineRow[];
}

export function CanonicalTimeline({ rows }: CanonicalTimelineProps) {
  return (
    <section className="panel">
      <h2>Canonical Timeline</h2>
      {rows.length === 0 ? (
        <p>Nenhum evento persistido nesta sessão.</p>
      ) : (
        rows.map((row) => (
          <div key={row.id} className="timeline-item code">
            <div>
              <strong>#{row.id}</strong> [{row.source}] {row.created_at}
            </div>
            <div>idempotency_key: {row.idempotency_key}</div>
            <div>payload_hash: {row.payload_hash}</div>
          </div>
        ))
      )}
    </section>
  );
}
