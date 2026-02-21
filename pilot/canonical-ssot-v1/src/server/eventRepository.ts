import { Pool } from "pg";
import type { CanonicalNormalized } from "../canonical/types";
import { InMemoryCanonicalEventStore } from "../canonical/eventLog";

const inMemoryStore = new InMemoryCanonicalEventStore();
let pool: Pool | null = null;

function getPool(): Pool | null {
  const url = process.env.DATABASE_URL;
  if (!url) {
    return null;
  }
  if (!pool) {
    pool = new Pool({ connectionString: url });
  }
  return pool;
}

export async function persistCanonicalEvent(
  payload: CanonicalNormalized,
  source = "canonical-web"
): Promise<{ id: number; idempotency_key: string; created_at: string; source: string; engine: "postgres" | "memory" }> {
  const db = getPool();

  if (!db) {
    const row = inMemoryStore.upsertByIdempotency(payload, source);
    return {
      id: row.id,
      idempotency_key: row.idempotency_key,
      created_at: row.created_at,
      source: row.source,
      engine: "memory"
    };
  }

  const client = await db.connect();
  try {
    await client.query("BEGIN");

    const contextInsert = await client.query(
      `INSERT INTO canonical_context (o_opp, v_vdd, i_idl, q_qbr, l_led, k_kbi, a_acc, s_src, e_e2e, b_b2b, n_n2c, h_hor, t_tzo, d_dat)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14)
       RETURNING id`,
      [
        payload.event_layer.o_opp,
        payload.event_layer.v_vdd,
        payload.event_layer.i_idl,
        payload.event_layer.q_qbr,
        payload.event_layer.l_led,
        payload.event_layer.k_kbi,
        payload.event_layer.a_acc,
        payload.event_layer.s_src,
        payload.event_layer.e_e2e,
        payload.event_layer.b_b2b,
        payload.event_layer.n_n2c,
        payload.event_layer.h_hor,
        payload.event_layer.t_tzo,
        payload.event_layer.d_dat
      ]
    );

    const identityInsert = await client.query(
      `INSERT INTO canonical_identity (u_usr, w_www, m_mob, c_con, x_pwd, f_hom, z_zon)
       VALUES ($1,$2,$3,$4,$5,$6,$7)
       RETURNING id`,
      [
        payload.iam_layer.u_usr,
        payload.iam_layer.w_www,
        payload.iam_layer.m_mob,
        payload.iam_layer.c_con,
        payload.iam_layer.x_pwd,
        payload.iam_layer.f_hom,
        payload.iam_layer.z_zon
      ]
    );

    await client.query(
      `INSERT INTO canonical_acl_binding (identity_id, role_code, zone_level)
       VALUES ($1, $2, $3)
       ON CONFLICT (identity_id, role_code, zone_level) DO NOTHING`,
      [identityInsert.rows[0].id, payload.catalog_resolution.role_code, payload.catalog_resolution.zone_level]
    );

    const eventInsert = await client.query(
      `INSERT INTO canonical_event_log (context_id, identity_id, payload_hash, idempotency_key, payload_jsonb, source)
       VALUES ($1, $2, $3, $4, $5::jsonb, $6)
       ON CONFLICT (idempotency_key)
       DO UPDATE SET source = EXCLUDED.source
       RETURNING id, idempotency_key, created_at, source`,
      [
        contextInsert.rows[0].id,
        identityInsert.rows[0].id,
        payload.metadata.payload_hash,
        payload.metadata.idempotency_key,
        JSON.stringify(payload),
        source
      ]
    );

    await client.query("COMMIT");

    const row = eventInsert.rows[0] as {
      id: number;
      idempotency_key: string;
      created_at: string;
      source: string;
    };

    return {
      id: row.id,
      idempotency_key: row.idempotency_key,
      created_at: row.created_at,
      source: row.source,
      engine: "postgres"
    };
  } catch (error) {
    await client.query("ROLLBACK");
    throw error;
  } finally {
    client.release();
  }
}

export function listInMemoryEvents() {
  return inMemoryStore.getAll();
}
