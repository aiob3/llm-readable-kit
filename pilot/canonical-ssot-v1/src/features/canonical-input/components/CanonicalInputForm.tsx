"use client";

interface CanonicalInputFormProps {
  dsl: string;
  onChange: (value: string) => void;
  onLoadSample: () => void;
  onParse: () => void;
  onPersist: () => void;
  loading: boolean;
  canPersist: boolean;
}

export function CanonicalInputForm({
  dsl,
  onChange,
  onLoadSample,
  onParse,
  onPersist,
  loading,
  canPersist
}: CanonicalInputFormProps) {
  return (
    <section className="panel">
      <h2>
        DSL_INPUT
        <span className="mds-badge panel-badge-right">canonical/dsl</span>
      </h2>
      <p className="code panel-hint">
        Formato: <span className="panel-hint-accent">[key]: value</span> com camadas event + iam
      </p>
      <textarea
        className="textarea"
        value={dsl}
        onChange={(event) => onChange(event.target.value)}
        placeholder={`[context]: meu-projeto\n[event_type]: user.login\n[identity]: brito\n[role]: admin\n[zone]: public`}
      />
      <div className="button-row">
        <button type="button" onClick={onLoadSample} disabled={loading}>
          load_sample
        </button>
        <button type="button" onClick={onParse} disabled={loading || !dsl.trim()}>
          parse + validate
        </button>
        <button
          type="button"
          className="secondary"
          onClick={onPersist}
          disabled={loading || !canPersist}
        >
          persist_event
        </button>
      </div>
    </section>
  );
}
