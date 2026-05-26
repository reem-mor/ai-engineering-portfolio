create extension if not exists "uuid-ossp";

create table if not exists documents (
    id uuid primary key default uuid_generate_v4(),
    filename text not null,
    saved_as text,
    source_type text not null default 'sample',
    content_type text,
    size_bytes integer,
    status text not null default 'uploaded',
    chunk_count integer default 0,
    created_at timestamptz not null default now()
);

create table if not exists chat_sessions (
    id uuid primary key default uuid_generate_v4(),
    title text not null default 'New chat',
    created_at timestamptz not null default now()
);

create table if not exists chat_messages (
    id uuid primary key default uuid_generate_v4(),
    session_id uuid references chat_sessions(id) on delete cascade,
    role text not null check (role in ('user', 'assistant')),
    content text not null,
    confidence text,
    used_context boolean default false,
    created_at timestamptz not null default now()
);

create table if not exists retrieval_logs (
    id uuid primary key default uuid_generate_v4(),
    message_id uuid references chat_messages(id) on delete cascade,
    chunk_id text not null,
    source_file text not null,
    chunk_index integer not null,
    score numeric not null,
    chunk_preview text,
    created_at timestamptz not null default now()
);

create table if not exists incident_analyses (
    id uuid primary key default uuid_generate_v4(),
    description text not null,
    affected_service text,
    environment text,
    severity text not null,
    incident_summary text not null,
    likely_causes jsonb not null default '[]',
    recommended_checks jsonb not null default '[]',
    missing_information jsonb not null default '[]',
    next_best_action text not null,
    escalation_recommendation text not null,
    confidence text not null,
    used_context boolean not null default false,
    created_at timestamptz not null default now()
);

create table if not exists evaluation_results (
    id uuid primary key default uuid_generate_v4(),
    question text not null,
    expected_behavior text,
    actual_answer text,
    passed boolean,
    notes text,
    created_at timestamptz not null default now()
);

create index if not exists idx_chat_messages_session_id on chat_messages(session_id);
create index if not exists idx_retrieval_logs_message_id on retrieval_logs(message_id);
create index if not exists idx_documents_filename on documents(filename);
create index if not exists idx_incident_analyses_created_at on incident_analyses(created_at desc);
