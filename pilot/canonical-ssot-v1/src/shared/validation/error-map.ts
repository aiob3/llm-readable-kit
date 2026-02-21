export const ERROR_HELP: Record<string, string> = {
  E_PARSE_SYNTAX: "A linha DSL não está no formato [key]: value.",
  E_PARSE_MISSING_EVENT: "Há campos obrigatórios faltando na camada de eventos.",
  E_PARSE_MISSING_IAM: "Há campos obrigatórios faltando na camada IAM.",
  E_PARSE_REFERENCE: "Há referência quebrada entre átomos (ex.: u_usr -> a_acc).",
  E_PARSE_FORMAT: "Um ou mais campos não respeitam o padrão de formato canônico.",
  E_SCHEMA_VALIDATION: "O JSON normalizado não passou no schema v1.",
  E_IAM_ROLE: "Código de role não existe no catálogo IAM.",
  E_IAM_ZONE: "Código de zone não existe no catálogo IAM.",
  E_IAM_INCONSISTENCY: "Há inconsistência entre role em c_con e c embutido em z_zon.",
  E_IDEMPOTENCY_CONFLICT: "Conflito de idempotência detectado para este payload."
};
