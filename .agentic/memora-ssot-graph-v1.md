# Memora SSOT Graph v1

```yaml
spec:
  id: memora-ssot-graph-v1
  version: 1.0.0
  format: markdown+yaml
  schema_version: canonical-normalized.v1

governance:
  hitl:
    operator_is_final_authority: true
    assistant_role: sugerir alternativas, nunca decidir sozinho mudancas estruturais
  anti_patterns_blocked:
    - assumir schema sem inspecao do banco real
    - misturar motores de filtro paralelos
    - marcar causalidade como duplicidade
    - declarar resolvido sem validacao online
    - ocultar ruido sem plano corretivo auditavel
  approval_gates:
    - qualquer reset destrutivo exige confirmacao explicita
    - qualquer alteracao de ontologia exige validacao do operador

canonical_dictionary:
  layers:
    event:
      required_keys:
        - o_opp
        - v_vdd
        - i_idl
        - q_qbr
        - l_led
        - k_kbi
        - a_acc
        - s_src
        - e_e2e
        - b_b2b
        - n_n2c
        - h_hor
        - t_tzo
        - d_dat
    iam:
      required_keys:
        - u_usr
        - w_www
        - m_mob
        - c_con
        - x_pwd
        - f_hom
        - z_zon

cluster_model:
  project_master:
    canonical_id: project.master
    domains: [clusters, sync/status, commit/merge]
  session_master:
    canonical_id: session.master
    lifecycle: [session.start, session.resume, session.hidden]
  workstreams:
    - ws.features
    - ws.plan
    - ws.error_bug_fix
    - ws.research_improve
    - ws.build_plan_fix

membership:
  policy: primary_plus_secondary
  rule:
    - cada registro tem 1 cluster primario obrigatorio
    - pode ter N clusters secundarios

lexical_aliases:
  session:
    init: session.start
    start: session.start
    new: session.start
    resume: session.resume
    continue: session.resume
    discard: session.hidden
    hide: session.hidden
  workstreams:
    roadmap: ws.features
    features: ws.features
    plan: ws.plan
    backlog: ws.plan
    issue: ws.error_bug_fix
    issues: ws.error_bug_fix
    fix: ws.error_bug_fix
    error: ws.error_bug_fix
    errors: ws.error_bug_fix
    bug: ws.error_bug_fix
    research: ws.research_improve
    enhance: ws.research_improve
    improve: ws.research_improve
    build: ws.build_plan_fix

edge_matrix:
  - id: E001
    from: project.master
    to: session.master
    type: contains
    score: 1.00
  - id: E002
    from: session.start
    to: session.resume
    type: enables
    score: 0.90
  - id: E003
    from: session.resume
    to: ws.plan
    type: enables
    score: 0.86
  - id: E004
    from: ws.plan
    to: ws.features
    type: enables
    score: 0.92
  - id: E005
    from: ws.build_plan_fix
    to: ws.features
    type: implements
    score: 0.95
  - id: E006
    from: ws.error_bug_fix
    to: ws.plan
    type: refines
    score: 0.88
  - id: E007
    from: ws.error_bug_fix
    to: ws.build_plan_fix
    type: validates
    score: 0.90
  - id: E008
    from: ws.research_improve
    to: ws.plan
    type: refines
    score: 0.84
  - id: E009
    from: project.commit_merge
    to: project.sync_status
    type: validates
    score: 0.91
  - id: E010
    from: session.hidden
    to: session.master
    type: state_change
    score: 1.00

duplicate_semantic_edges_only:
  allowed_edge_types: [related_to, near_duplicate]
  allowed_sources: [embedding_auto, semantic_similarity]
  threshold: 0.85
  excluded_edge_types:
    - contains
    - enables
    - implements
    - depends_on
    - validates
    - refines
    - follows
    - preceded_by
    - references
    - state_change

inference_pipeline:
  - validate_input
  - normalize_aliases
  - derive_keys
  - assign_clusters
  - emit_atomic_segments
  - infer_edges
  - apply_visibility
  - recompute_graph_state
  - audit_log

filter_engine:
  single_source_of_truth: true
  dimensions: [time, section, tag, cluster, session, degreeMin, duplicates, visibility, spotlight]
  composition:
    intra_dimension: OR
    inter_dimension: AND_OR_global_toggle
  defaults:
    showDuplicates: true
    showHidden: false
    logic: AND
```
