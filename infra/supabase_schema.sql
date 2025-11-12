
-- Minimal schema
create extension if not exists pgcrypto;
create table if not exists organizations (
  id uuid primary key default gen_random_uuid(),
  name text,
  domain text unique not null,
  created_at timestamptz default now()
);
create table if not exists runs (
  id uuid primary key default gen_random_uuid(),
  org_id uuid references organizations(id) on delete cascade,
  tier text check (tier in ('lite','deep')) not null,
  started_at timestamptz default now(),
  finished_at timestamptz
);
create table if not exists assets (
  id uuid primary key default gen_random_uuid(),
  org_id uuid references organizations(id) on delete cascade,
  type text not null, -- domain, host, ip
  identifier text not null,
  discovered_at timestamptz default now(),
  unique(org_id,type,identifier)
);
create table if not exists findings (
  id uuid primary key default gen_random_uuid(),
  org_id uuid references organizations(id) on delete cascade,
  run_id uuid references runs(id) on delete cascade,
  asset_id uuid references assets(id) on delete set null,
  source text not null,
  title text not null,
  severity text check (severity in ('info','low','medium','high','critical')) not null,
  cvss numeric,
  evidence jsonb,
  first_seen timestamptz default now(),
  last_seen timestamptz default now()
);
alter table organizations enable row level security;
alter table runs enable row level security;
alter table assets enable row level security;
alter table findings enable row level security;
create policy read_all_org on organizations for select using (true);
create policy read_all_runs on runs for select using (true);
create policy read_all_assets on assets for select using (true);
create policy read_all_findings on findings for select using (true);
