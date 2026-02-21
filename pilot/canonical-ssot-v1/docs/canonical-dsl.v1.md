# canonical-dsl.v1

## Purpose
Canonical textual DSL for event + IAM payloads using atomic key-value lines.

## Syntax
- One entry per line: `[key]: value`
- Inline comments are allowed after `#`.
- Empty lines are ignored.

Example:
```txt
[o_opp]: o_26q1-lead-20260219-171-vo2tr-199-10-110-204343-24-190226
```

## Mandatory Event Layer Keys
- `o_opp`
- `v_vdd`
- `i_idl`
- `q_qbr`
- `l_led`
- `k_kbi`
- `a_acc`
- `s_src`
- `e_e2e`
- `b_b2b`
- `n_n2c`
- `h_hor`
- `t_tzo`
- `d_dat`

## Mandatory IAM Layer Keys
- `u_usr`
- `w_www`
- `m_mob`
- `c_con`
- `x_pwd`
- `f_hom`
- `z_zon`

## Invariants
- `i_idl` must be exactly: `i_q-l-k-a-s-e-b-n-h-t-d`
- `u_usr` must include `${a_*-}` (explicit reference to account atom).
- `f_hom` must include `${u_<code>}` style reference.
- `c_con` and `z_zon` numeric codes must exist in IAM catalogs.

## Format Constraints (v1)
- `k_kbi`: `k_yyyyMMdd-HHmmss`
- `h_hor`: `h_HH-mm-ss`
- `d_dat`: `d_dd-MM-yy`
- `t_tzo`: `t_<num>-Area/City`
- `x_pwd`: `x_<min>-<secret>` where `<secret>.length >= min`

## Normalized Output
`canonical-normalized.v1` JSON with deterministic key order, schema validation, payload hash and idempotency key.
