import { describe, expect, test } from "vitest";
import { ERROR_HELP } from "../src/shared/validation/error-map";

describe("frontend validation mapping", () => {
  test("mapeia classes de erro canônicas", () => {
    expect(ERROR_HELP.E_PARSE_MISSING_EVENT).toContain("camada de eventos");
    expect(ERROR_HELP.E_PARSE_MISSING_IAM).toContain("camada IAM");
    expect(ERROR_HELP.E_SCHEMA_VALIDATION).toContain("schema");
    expect(ERROR_HELP.E_IDEMPOTENCY_CONFLICT).toContain("idempotência");
  });
});
