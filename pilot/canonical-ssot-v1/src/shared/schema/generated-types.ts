/* eslint-disable */
// AUTO-GENERATED FILE. Source: schema/canonical-normalized.v1.schema.json

export type CanonicalEventKey = "o_opp" | "v_vdd" | "i_idl" | "q_qbr" | "l_led" | "k_kbi" | "a_acc" | "s_src" | "e_e2e" | "b_b2b" | "n_n2c" | "h_hor" | "t_tzo" | "d_dat";
export type CanonicalIAMKey = "u_usr" | "w_www" | "m_mob" | "c_con" | "x_pwd" | "f_hom" | "z_zon";

export type CanonicalEventV1 = Record<CanonicalEventKey, string>;
export type CanonicalIAMV1 = Record<CanonicalIAMKey, string>;

export interface CanonicalContextV1 {
  schema_version: "canonical-normalized.v1";
  event_layer: CanonicalEventV1;
  iam_layer: CanonicalIAMV1;
  catalog_resolution: {
    role_code: number;
    role_label: string;
    zone_level: number;
    zone_label: string;
  };
  metadata: {
    payload_hash: string;
    idempotency_key: string;
    normalized_at_utc: string;
  };
}
