--▛//▞▞ ⟦⎊⟧ :: DB.SEED ⫸
-- initialize Codex memory tables with drift.lock

create extension if not exists vector;

create table if not exists user_facts(
  user_id text,
  key text,
  value jsonb,
  confidence real default 0.9,
  sealed_at timestamptz default now(),
  revoked_at timestamptz,
  primary key(user_id, key, sealed_at)
);

create table if not exists events(
  id bigserial primary key,
  ts timestamptz default now(),
  user_id text,
  kind text,      -- "prompt.run", "tool.call"
  banner text,
  seal text,      -- ":: ∎"
  payload jsonb
);

create table if not exists memory_chunks(
  id bigserial primary key,
  user_id text,
  banner text,
  tags text[],
  text text,
  embedding vector(1536)
);

create index if not exists memory_chunks_embedding_idx
  on memory_chunks using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

create index if not exists events_user_ts_idx
  on events(user_id, ts desc);

create index if not exists user_facts_user_idx
  on user_facts(user_id)
  where revoked_at is null;

comment on schema public is
  '▛//▞▞ Memory Codex — drift.locked by seal ∎';

-- Grant permissions
grant all privileges on all tables in schema public to codex;
grant all privileges on all sequences in schema public to codex;

-- ∎
