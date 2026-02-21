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
      <h2>
        EVENT_LOG
        <span className="mds-badge panel-badge-right">{rows.length} events</span>
      </h2>
      {rows.length === 0 ? (
        <p className="timeline-empty">Nenhum evento persistido nesta sessão.</p>
      ) : (
        rows.map((row) => (
          <div key={row.id} className="timeline-item code">
            <div>
              <span className="timeline-id">#{row.id}</span>
              {" "}
              <span className="timeline-source">[{row.source}]</span>
              {" "}
              <span className="timeline-ts">{row.created_at}</span>
            </div>
            <div className="timeline-hash">key: {row.idempotency_key}</div>
            <div className="timeline-hash">hash: {row.payload_hash}</div>
          </div>
        ))
      )}
    </section>
  );
}
