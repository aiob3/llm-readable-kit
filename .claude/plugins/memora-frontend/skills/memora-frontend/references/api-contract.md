# Memora API — Contratos e Payloads de Referência

## GET /api/graph
```json
{
  "nodes": [
    {
      "id": "mem_001",
      "label": "Brito - Setup WSL2",
      "type": "memory",
      "observations": ["Ubuntu 24.04", "Docker Desktop", "VSCode July 2025"],
      "created_at": "2025-02-20T14:30:00Z"
    },
    {
      "id": "ent_001",
      "label": "Projeto VCIA",
      "type": "entity",
      "observations": ["vcia.com.br", "VPS KVM4", "Stack completo"],
      "created_at": "2025-02-18T10:00:00Z"
    }
  ],
  "edges": [
    {
      "source": "mem_001",
      "target": "ent_001",
      "type": "relates_to"
    }
  ]
}
```

## GET /api/memories
```json
[
  {
    "id": "mem_001",
    "content": "Setup WSL2 com Ubuntu 24.04 e Docker Desktop",
    "type": "technical",
    "crossrefs": ["ent_001"],
    "actions": [],
    "created_at": "2025-02-20T14:30:00Z",
    "updated_at": "2025-02-20T14:30:00Z"
  }
]
```

## POST /api/memories — body
```json
{
  "content": "string (required)",
  "type": "technical | personal | project | context",
  "tags": ["string"]
}
```

## GET /api/views
```json
{
  "by_type": {
    "technical": 12,
    "personal": 4,
    "project": 8
  },
  "recent": [...],
  "most_connected": [...]
}
```

## Tipos de relação (rel_type) em memories_crossrefs
- `relates_to` — relação genérica
- `depends_on` — dependência técnica
- `part_of` — composição
- `contradicts` — conflito
- `extends` — extensão/herança
