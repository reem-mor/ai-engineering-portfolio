-- Incident Assistant RAG — tables expected by app/db/*_repository.py
-- Run in Supabase: SQL Editor → New query → Paste → Run.
-- The backend uses the SERVICE ROLE key (server-side only); it bypasses RLS.
-- Rotate the key if it is ever exposed.

-- Chat history + retrieval audit
create table if not exists public.chat_sessions (
    id uuid primary key default gen_random_uuid(),
    title text not null default 'New chat',
    created_at timestamptz not null default now()
);

create table if not exists public.chat_messages (
    id uuid primary key default gen_random_uuid(),
    session_id uuid not null references public.chat_sessions (id) on delete cascade,
    role text not null,
    content text not null,
    confidence text null,
    used_context boolean not null default false,
    created_at timestamptz not null default now()
);

create table if not exists public.retrieval_logs (
    id uuid primary key default gen_random_uuid(),
    message_id uuid not null references public.chat_messages (id) on delete cascade,
    chunk_id text not null,
    source_file text not null,
    chunk_index integer not null,
    score double precision not null,
    chunk_preview text not null,
    created_at timestamptz not null default now()
);

-- Upload metadata (vectors still live in local FAISS + files on disk)
create table if not exists public.documents (
    id uuid primary key default gen_random_uuid(),
    filename text not null,
    saved_as text null,
    source_type text not null,
    content_type text null,
    size_bytes bigint null,
    status text not null default 'uploaded',
    chunk_count integer not null default 0,
    created_at timestamptz not null default now()
);

-- Incident analyzer responses
create table if not exists public.incident_analyses (
    id uuid primary key default gen_random_uuid(),
    description text not null,
    affected_service text null,
    environment text null,
    severity text not null,
    incident_summary text not null,
    likely_causes jsonb not null default '[]'::jsonb,
    recommended_checks jsonb not null default '[]'::jsonb,
    missing_information jsonb not null default '[]'::jsonb,
    next_best_action text not null,
    escalation_recommendation text not null,
    confidence text not null,
    used_context boolean not null default false,
    created_at timestamptz not null default now()
);

-- Helpful indexes
create index if not exists idx_chat_messages_session_id on public.chat_messages (session_id);
create index if not exists idx_retrieval_logs_message_id on public.retrieval_logs (message_id);
create index if not exists idx_documents_created_at on public.documents (created_at desc);
