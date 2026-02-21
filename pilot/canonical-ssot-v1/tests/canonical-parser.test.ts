import { describe, expect, test } from "vitest";
import { parseCanonicalDsl } from "../src/canonical/parser";
import { normalizeCanonicalRecord } from "../src/canonical/normalize";
import { validateCanonicalJson } from "../src/canonical/validator";
import { CanonicalError } from "../src/canonical/errors";

const fullDsl = `[o_opp]: o_26q1-lead-20260219-171-vo2tr-199-10-110-204343-24-190226
[v_vdd]: v_261-99-20260219-171-55-199-10-110-204343-24-190226
[i_idl]: i_q-l-k-a-s-e-b-n-h-t-d
[q_qbr]: q_q1-26-1
[l_led]: l_99-lead-vo2tr-204343-190226
[k_kbi]: k_20260219-204343
[a_acc]: a_171-Fernando-Brito
[s_src]: s_55-vo2tr-callrecorder
[e_e2e]: e_199-New-Logo
[b_b2b]: b_10-O2Print
[n_n2c]: n_110-Prevent-Senior
[h_hor]: h_20-43-43
[t_tzo]: t_24-America/Sao_Paulo
[d_dat]: d_19-02-26
[u_usr]: u_10-\${a_*-}-fbrito
[w_www]: w_vcia-com-br
[m_mob]: m_5511963982357
[c_con]: c_86-isBrito
[x_pwd]: x_8-********
[f_hom]: f_home-\${u_10}
[z_zon]: z_254-c_86-u_10`;

describe("canonical parser", () => {
  test("parse feliz com payload completo", () => {
    const parsed = parseCanonicalDsl(fullDsl);
    const normalized = normalizeCanonicalRecord(parsed);

    expect(normalized.schema_version).toBe("canonical-normalized.v1");
    expect(normalized.event_layer.o_opp).toContain("o_26q1");
    expect(normalized.catalog_resolution.role_code).toBe(86);
    expect(normalized.catalog_resolution.zone_level).toBe(254);
  });

  test("falha por parâmetro ausente na camada de eventos", () => {
    const invalid = fullDsl.replace("[k_kbi]: k_20260219-204343\n", "");
    expect(() => parseCanonicalDsl(invalid)).toThrowError(CanonicalError);
    try {
      parseCanonicalDsl(invalid);
    } catch (error) {
      const e = error as CanonicalError;
      expect(e.code).toBe("E_PARSE_MISSING_EVENT");
    }
  });

  test("falha por parâmetro ausente na camada IAM", () => {
    const invalid = fullDsl.replace("[c_con]: c_86-isBrito\n", "");
    expect(() => parseCanonicalDsl(invalid)).toThrowError(CanonicalError);
    try {
      parseCanonicalDsl(invalid);
    } catch (error) {
      const e = error as CanonicalError;
      expect(e.code).toBe("E_PARSE_MISSING_IAM");
    }
  });

  test("falha por referência quebrada em u_usr", () => {
    const invalid = fullDsl.replace("u_10-${a_*-}-fbrito", "u_10-fbrito");
    expect(() => parseCanonicalDsl(invalid)).toThrowError(CanonicalError);
    try {
      parseCanonicalDsl(invalid);
    } catch (error) {
      const e = error as CanonicalError;
      expect(e.code).toBe("E_PARSE_FORMAT");
    }
  });

  test("falha por formato inválido em k_kbi/d_dat/t_tzo/x_pwd", () => {
    const invalid = fullDsl
      .replace("k_20260219-204343", "k_20260219")
      .replace("d_19-02-26", "d_190226")
      .replace("t_24-America/Sao_Paulo", "t_America/Sao_Paulo")
      .replace("x_8-********", "x_10-123");

    expect(() => parseCanonicalDsl(invalid)).toThrowError(CanonicalError);
  });

  test("falha por código IAM fora do catálogo", () => {
    const invalid = fullDsl.replace("c_86-isBrito", "c_777-unknown").replace("z_254-c_86-u_10", "z_254-c_777-u_10");
    expect(() => parseCanonicalDsl(invalid)).toThrowError(CanonicalError);
    try {
      parseCanonicalDsl(invalid);
    } catch (error) {
      const e = error as CanonicalError;
      expect(e.code).toBe("E_IAM_ROLE");
    }
  });

  test("validação de schema passa para payload válido", () => {
    const parsed = parseCanonicalDsl(fullDsl);
    const normalized = normalizeCanonicalRecord(parsed);
    expect(validateCanonicalJson(normalized)).toBe(true);
  });
});
