-- 가족 공유 앱 스키마
-- Supabase SQL Editor에서 한 번에 실행하세요.

create table if not exists categories (
  id bigint generated always as identity primary key,
  name text not null unique,
  created_at timestamptz not null default now()
);

create table if not exists text_items (
  id bigint generated always as identity primary key,
  category_id bigint not null references categories (id) on delete cascade,
  content text not null,
  checked boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists photos (
  id bigint generated always as identity primary key,
  category_id bigint not null references categories (id) on delete cascade,
  storage_path text not null,
  created_at timestamptz not null default now()
);

create index if not exists text_items_category_id_idx on text_items (category_id);
create index if not exists photos_category_id_idx on photos (category_id);

-- Storage 버킷 (공개 읽기: 앱 비밀번호가 접근을 막음)
insert into storage.buckets (id, name, public)
values ('photos', 'photos', true)
on conflict (id) do nothing;

-- Streamlit은 service_role 키로 접속하므로 RLS를 켜 두되,
-- anon 직접 접근은 막습니다. (앱 secrets의 service_role이 우회)
alter table categories enable row level security;
alter table text_items enable row level security;
alter table photos enable row level security;
