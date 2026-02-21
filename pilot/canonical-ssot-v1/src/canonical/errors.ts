export class CanonicalError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly details?: Record<string, unknown>
  ) {
    super(message);
    this.name = "CanonicalError";
  }
}

export function toErrorPayload(error: unknown): {
  code: string;
  message: string;
  details?: Record<string, unknown>;
} {
  if (error instanceof CanonicalError) {
    return {
      code: error.code,
      message: error.message,
      details: error.details
    };
  }

  return {
    code: "E_UNKNOWN",
    message: error instanceof Error ? error.message : String(error)
  };
}
