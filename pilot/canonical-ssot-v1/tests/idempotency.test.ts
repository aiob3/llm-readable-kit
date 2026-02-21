import { describe, expect, test } from "vitest";
import { parseCanonicalDsl } from "../src/canonical/parser";
import { normalizeCanonicalRecord } from "../src/canonical/normalize";
import { InMemoryCanonicalEventStore } from "../src/canonical/eventLog";

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

describe("idempotency", () => {
  test("mesmo payload gera mesma idempotency_key", () => {
    const parsed = parseCanonicalDsl(fullDsl);
    const p1 = normalizeCanonicalRecord(parsed);
    const p2 = normalizeCanonicalRecord(parsed);

    expect(p1.metadata.idempotency_key).toBe(p2.metadata.idempotency_key);
    expect(p1.metadata.payload_hash).toBe(p2.metadata.payload_hash);
  });

  test("concorrência não duplica evento no store", async () => {
    const parsed = parseCanonicalDsl(fullDsl);
    const payload = normalizeCanonicalRecord(parsed);
    const store = new InMemoryCanonicalEventStore();

    const results = await Promise.all(
      Array.from({ length: 20 }).map(async () => store.upsertByIdempotency(payload, "test"))
    );

    expect(new Set(results.map((item) => item.id)).size).toBe(1);
    expect(store.getAll().length).toBe(1);
  });
});
