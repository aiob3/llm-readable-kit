// parte
{
  "proposed_visual_model": {
    "correlation_types": [
      {
        "type": "causal_dependency",
        "maps_from": ["depends_on"],
        "color": "solid_blue",
        "hex": "#2563EB",
        "width": 2.8,
        "style": "solid",
        "label": "→ (depende de)",
        "meaning": "A não pode existir sem B (pré-condição forte).",
        "example": "Checkpoint depende de session_start + code_change concluído."
      },
      {
        "type": "temporal_precedence",
        "maps_from": ["precedes"],
        "color": "solid_green",
        "hex": "#16A34A",
        "width": 2.2,
        "style": "solid",
        "label": "⟹ (precede)",
        "meaning": "A deve ocorrer antes de B por política/processo.",
        "example": "Decision precede implementation em fluxo de governança."
      },
      {
        "type": "implementation",
        "maps_from": ["implements", "enables"],
        "color": "solid_orange",
        "hex": "#EA580C",
        "width": 2.4,
        "style": "solid",
        "label": "✓ (implementa/habilita)",
        "meaning": "A executa ou habilita materialmente B.",
        "example": "Code change implementa decisão e habilita delivery."
      },
      {
        "type": "validation",
        "maps_from": ["validates"],
        "color": "solid_purple",
        "hex": "#7C3AED",
        "width": 1.8,
        "style": "solid",
        "label": "✔ (valida)",
        "meaning": "A confirma qualidade/aderência de B.",
        "example": "Delivery valida checkpoint e hardening técnico."
      },
      {
        "type": "refinement",
        "maps_from": ["refines"],
        "color": "solid_teal",
        "hex": "#0D9488",
        "width": 1.6,
        "style": "solid",
        "label": "↺ (refina)",
        "meaning": "A melhora/torna mais preciso B sem contradizê-lo.",
        "example": "Atualização de relatório refina resultado de validação."
      },
      {
        "type": "contradiction",
        "maps_from": ["contradicts"],
        "color": "solid_red",
        "hex": "#DC2626",
        "width": 2.6,
        "style": "solid",
        "label": "✕ (contradiz)",
        "meaning": "A conflita semanticamente com B e exige revisão.",
        "example": "Decisão nova contradiz decisão anterior não revogada."
      },
      {
        "type": "passive_similarity",
        "maps_from": ["semantic_similarity", "crossref_embedding"],
        "color": "dashed_gray",
        "hex": "#6B7280",
        "width": 0.9,
        "style": "dashed",
        "opacity": 0.35,
        "label": "~ (similar)",
        "meaning": "Relação semântica automática, sem causalidade comprovada.",
        "example": "Crossrefs por embeddings entre memórias próximas."
      }
    ],
    "render_rules": {
      "direction": "all_edges_directed_except_passive_similarity",
      "arrowheads": {
        "causal_dependency": "triangle",
        "temporal_precedence": "vee",
        "implementation": "triangle",
        "validation": "diamond",
        "refinement": "circle",
        "contradiction": "tee",
        "passive_similarity": "none"
      },
      "certainty_to_opacity": [
        { "range": ">=0.95", "opacity": 1.0 },
        { "range": "0.85-0.94", "opacity": 0.85 },
        { "range": "0.70-0.84", "opacity": 0.65 },
        { "range": "<0.70", "opacity": 0.45 }
      ],
      "certainty_to_width_multiplier": [
        { "range": ">=0.95", "multiplier": 1.15 },
        { "range": "0.85-0.94", "multiplier": 1.0 },
        { "range": "0.70-0.84", "multiplier": 0.9 },
        { "range": "<0.70", "multiplier": 0.8 }
      ],
      "visual_priority": [
        "contradiction",
        "causal_dependency",
        "implementation",
        "validation",
        "refinement",
        "temporal_precedence",
        "passive_similarity"
      ],
      "label_policy": "show_label_if_width>=1.6_or_user_hover"
    }
  }
}