# Τ{Raven} - System Architecture Diagram

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER LAYER                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Telegram Messages
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      TELEGRAM API                                │
│                   (Bot API / Webhooks)                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RAVEN BOT LAYER                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Command Router                                           │  │
│  │  ┌─────────┬─────────┬─────────┬─────────┬─────────┐   │  │
│  │  │  /ask   │  /git   │  /file  │  /run   │ /context│   │  │
│  │  └─────────┴─────────┴─────────┴─────────┴─────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│  ┌───────────────────────────┴──────────────────────────────┐  │
│  │             Services Layer                                │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │  │
│  │  │ AI Bridge   │  │Git Manager  │  │Context Track│    │  │
│  │  │  (Claude)   │  │             │  │             │    │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                 ┌────────────┼────────────┐
                 │            │            │
                 ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Anthropic  │  │    Redis     │  │  PostgreSQL  │         │
│  │   Claude API │  │   Sessions   │  │   History    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      WORKSPACE LAYER                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  /workspace (Git Repository)                              │  │
│  │  ├── src/                                                 │  │
│  │  ├── tests/                                               │  │
│  │  ├── .git/                                                │  │
│  │  └── ...                                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### 1. Ask Command Flow

```
┌──────────┐
│   User   │ "How does X work?"
└─────┬────┘
      │
      ▼
┌──────────────┐
│   Telegram   │ Receives message
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│  Command Handler │ Routes to /ask
└─────────┬────────┘
          │
          ▼
┌──────────────────────┐
│  Context Tracker     │ Gathers:
│  ┌─────────────────┐ │ - Git status
│  │ • Git status    │ │ - File tree
│  │ • Branch info   │ │ - Recent commits
│  │ • File tree     │ │
│  │ • Recent commits│ │
│  └─────────────────┘ │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│    AI Bridge         │
│  ┌─────────────────┐ │
│  │ Build prompt    │ │ 1. System prompt + context
│  │      ↓          │ │ 2. User question
│  │ Call Claude API │ │ 3. Get response
│  │      ↓          │ │
│  │ Format response │ │
│  └─────────────────┘ │
└──────────┬───────────┘
           │
           ▼
┌──────────────────┐
│  Response Back   │ Formatted message
└─────────┬────────┘
          │
          ▼
┌──────────────┐
│  Telegram    │ Sends to user
└──────┬───────┘
       │
       ▼
┌──────────┐
│   User   │ Receives answer
└──────────┘
```

### 2. Git Command Flow

```
User → Telegram → Bot → Git Manager → Execute Command → Parse Output → Format → User
                                ↓
                          /workspace/.git
```

### 3. File Operation Flow

```
User → Telegram → Bot → Validate Path → Read/Write File → Response → User
                          ↓                    ↓
                    Security Check        /workspace/*
```

## Component Interaction Matrix

```
┌─────────────┬─────────┬─────┬──────────┬────────┬──────┐
│ Component   │Telegram │Redis│PostgreSQL│Workspace│Claude│
├─────────────┼─────────┼─────┼──────────┼────────┼──────┤
│ Bot Main    │   ✓✓✓   │  ✓  │    ✓     │   ✓    │      │
│ AI Bridge   │         │     │          │        │ ✓✓✓  │
│ Git Manager │         │     │          │  ✓✓✓   │      │
│ Context Tr. │         │  ✓  │    ✓     │  ✓✓✓   │      │
│ Session Mgr │         │ ✓✓✓ │   ✓✓✓    │        │      │
└─────────────┴─────────┴─────┴──────────┴────────┴──────┘

Legend: ✓ = Uses, ✓✓✓ = Heavy usage
```

## Container Architecture (Docker)

```
┌─────────────────────────────────────────────────────────────┐
│  Docker Network: raven-network                              │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  raven-bot (Python Container)                         │  │
│  │  ├── /app (Bot code)                                  │  │
│  │  ├── /workspace (mounted from host)                   │  │
│  │  └── /app/logs (mounted volume)                       │  │
│  └────────────┬─────────────────────┬───────────────────┘  │
│               │                     │                       │
│  ┌────────────▼─────────┐  ┌───────▼────────┐             │
│  │  redis                │  │  postgres      │             │
│  │  (Session Store)      │  │  (History DB)  │             │
│  │  Port: 6379          │  │  Port: 5432    │             │
│  └──────────────────────┘  └────────────────┘             │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  n8n (Optional - Workflow Automation)                 │  │
│  │  Port: 5678                                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  web-interface (Optional - React UI)                  │  │
│  │  Port: 3000                                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  nginx (Optional - Reverse Proxy)                     │  │
│  │  Port: 80, 443                                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                           │
│                                                              │
│  1. User Authentication                                      │
│     └─ Telegram User ID whitelist                           │
│                                                              │
│  2. Command Validation                                       │
│     └─ Input sanitization, path traversal protection        │
│                                                              │
│  3. Rate Limiting                                            │
│     └─ Per-user request throttling                          │
│                                                              │
│  4. API Key Management                                       │
│     └─ Environment variables, Docker secrets                │
│                                                              │
│  5. Audit Logging                                            │
│     └─ All commands logged to PostgreSQL                    │
│                                                              │
│  6. Network Isolation                                        │
│     └─ Docker network, firewall rules                       │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Topologies

### Development (Local)

```
┌──────────────┐
│  Developer   │
│   Machine    │
│              │
│  ├─ Python   │
│  ├─ Redis    │◄─── All local
│  └─ Postgres │
└──────────────┘
```

### Production (Single Server)

```
┌────────────────────────────────┐
│        VPS / Cloud VM          │
│                                │
│  ┌─────────────────────────┐  │
│  │  Docker Compose         │  │
│  │  ├─ Bot                 │  │
│  │  ├─ Redis               │  │
│  │  ├─ PostgreSQL          │  │
│  │  └─ Nginx               │  │
│  └─────────────────────────┘  │
│                                │
│  ┌─────────────────────────┐  │
│  │  Backups → S3/Storage   │  │
│  └─────────────────────────┘  │
└────────────────────────────────┘
```

### Production (High Availability)

```
┌─────────────────────────────────────────────────────────┐
│                  Load Balancer                           │
└─────────┬────────────────────────────┬──────────────────┘
          │                            │
    ┌─────▼─────┐              ┌───────▼─────┐
    │  Bot VM 1 │              │  Bot VM 2   │
    │  (Active) │              │  (Standby)  │
    └─────┬─────┘              └───────┬─────┘
          │                            │
          └────────────┬───────────────┘
                       │
    ┌──────────────────▼──────────────────┐
    │       Managed Database Cluster      │
    │  ├─ Redis (Primary + Replicas)     │
    │  └─ PostgreSQL (Primary + Standby) │
    └─────────────────────────────────────┘
```

## Data Models

### Session State
```
Session {
  user_id: int
  username: string
  conversation_history: Message[]
  workspace_path: string
  created_at: timestamp
  last_active: timestamp
}
```

### Message
```
Message {
  role: "user" | "assistant" | "system"
  content: string
  timestamp: timestamp
  metadata: json
}
```

### Workspace Context
```
Context {
  workspace_path: string
  git_info: {
    branch: string
    status: string
    recent_commits: string[]
    modified_files: int
  }
  file_tree: string[]
  project_type: string
  timestamp: timestamp
}
```

## API Endpoints (Internal)

```
AI Bridge:
  - ask_with_context(question, context) → response
  - ask_simple(question) → response

Git Manager:
  - execute_command(git_args) → output
  - get_status() → status_dict
  - get_recent_commits(count) → commits_string
  - get_diff(staged) → diff_output

Context Tracker:
  - get_full_context() → context_dict
  - get_file_tree(max_files) → file_list
  - get_git_info() → git_dict
  - search_files(pattern) → matching_files
```

## Scalability Considerations

### Vertical Scaling
- Increase container resources
- Upgrade server tier
- Add more CPU/RAM

### Horizontal Scaling
- Multiple bot instances with load balancer
- Shared Redis for session state
- Read replicas for PostgreSQL
- Distributed file system for workspace

### Performance Optimization
- Cache frequent AI responses (Redis)
- Connection pooling (PostgreSQL)
- Async message processing (Celery queue)
- CDN for static assets (if web interface)

---

**This architecture supports:**
- ✅ Personal use (single user)
- ✅ Small team (< 10 users)
- ✅ Scalable to hundreds of users
- ✅ High availability deployments
- ✅ Cloud-native infrastructure
