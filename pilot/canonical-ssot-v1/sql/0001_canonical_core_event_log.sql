BEGIN;

CREATE TABLE IF NOT EXISTS canonical_context (
  id BIGSERIAL PRIMARY KEY,
  o_opp TEXT NOT NULL,
  v_vdd TEXT NOT NULL,
  i_idl TEXT NOT NULL,
  q_qbr TEXT NOT NULL,
  l_led TEXT NOT NULL,
  k_kbi TEXT NOT NULL,
  a_acc TEXT NOT NULL,
  s_src TEXT NOT NULL,
  e_e2e TEXT NOT NULL,
  b_b2b TEXT NOT NULL,
  n_n2c TEXT NOT NULL,
  h_hor TEXT NOT NULL,
  t_tzo TEXT NOT NULL,
  d_dat TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS canonical_identity (
  id BIGSERIAL PRIMARY KEY,
  u_usr TEXT NOT NULL,
  w_www TEXT NOT NULL,
  m_mob TEXT NOT NULL,
  c_con TEXT NOT NULL,
  x_pwd TEXT NOT NULL,
  f_hom TEXT NOT NULL,
  z_zon TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS canonical_role_catalog (
  role_code INTEGER PRIMARY KEY,
  role_label TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS canonical_zone_catalog (
  zone_level INTEGER PRIMARY KEY,
  zone_label TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS canonical_acl_binding (
  id BIGSERIAL PRIMARY KEY,
  identity_id BIGINT NOT NULL REFERENCES canonical_identity(id) ON DELETE CASCADE,
  role_code INTEGER NOT NULL REFERENCES canonical_role_catalog(role_code),
  zone_level INTEGER NOT NULL REFERENCES canonical_zone_catalog(zone_level),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(identity_id, role_code, zone_level)
);

CREATE TABLE IF NOT EXISTS canonical_event_log (
  id BIGSERIAL PRIMARY KEY,
  context_id BIGINT NOT NULL REFERENCES canonical_context(id) ON DELETE RESTRICT,
  identity_id BIGINT NOT NULL REFERENCES canonical_identity(id) ON DELETE RESTRICT,
  payload_hash CHAR(64) NOT NULL,
  idempotency_key CHAR(64) NOT NULL,
  payload_jsonb JSONB NOT NULL,
  source TEXT NOT NULL DEFAULT 'canonical-cli',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_canonical_event_log_idempotency_key
  ON canonical_event_log (idempotency_key);

CREATE INDEX IF NOT EXISTS ix_canonical_context_o_opp ON canonical_context (o_opp);
CREATE INDEX IF NOT EXISTS ix_canonical_context_k_kbi ON canonical_context (k_kbi);
CREATE INDEX IF NOT EXISTS ix_canonical_identity_u_usr ON canonical_identity (u_usr);
CREATE INDEX IF NOT EXISTS ix_canonical_identity_c_con ON canonical_identity (c_con);
CREATE INDEX IF NOT EXISTS ix_canonical_identity_z_zon ON canonical_identity (z_zon);
CREATE INDEX IF NOT EXISTS ix_canonical_event_log_payload_jsonb
  ON canonical_event_log USING GIN (payload_jsonb);

INSERT INTO canonical_role_catalog (role_code, role_label) VALUES
  (1, 'admin-is-user'),
  (2, 'super-is-guest'),
  (44, 'supermario-is-sudo'),
  (51, 'luigi-is-admin'),
  (63, 'yoshi-is-manager'),
  (86, 'isBrito')
ON CONFLICT (role_code) DO NOTHING;

INSERT INTO canonical_zone_catalog (zone_level, zone_label) VALUES
  (254, 'godBrito'),
  (1986, 'sudoRoot'),
  (1999, 'neo'),
  (2000, 'y2k'),
  (2500, 'staff'),
  (2666, 'powerUser'),
  (2699, 'editor'),
  (2700, 'collaborator'),
  (2800, 'audit'),
  (3000, 'userManager'),
  (4000, 'communityModerator'),
  (4500, 'teamsModerator'),
  (5000, 'editWriteRead'),
  (9900, 'selfData'),
  (9950, 'readContent'),
  (9980, 'canLogin'),
  (9984, 'resetPasswd'),
  (9985, 'ssoOauth'),
  (9995, 'canSignIn'),
  (9997, 'viewPage'),
  (9998, 'redirectHome'),
  (9999, 'limitedView')
ON CONFLICT (zone_level) DO NOTHING;

COMMIT;
