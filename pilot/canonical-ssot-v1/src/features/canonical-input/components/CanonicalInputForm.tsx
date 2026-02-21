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
      <h2>Canonical Input DSL</h2>
      <p>Entrada autoral no formato `[key]: value` com camada de Eventos + IAM.</p>
      <textarea
        className="textarea"
        value={dsl}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Cole o payload DSL aqui"
      />
      <div className="button-row">
        <button type="button" onClick={onLoadSample} disabled={loading}>
          Load sample
        </button>
        <button type="button" onClick={onParse} disabled={loading || !dsl.trim()}>
          Parse + validate
        </button>
        <button
          type="button"
          className="secondary"
          onClick={onPersist}
          disabled={loading || !canPersist}
        >
          Persist event
        </button>
      </div>
    </section>
  );
}
