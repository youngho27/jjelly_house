-- 가족 구매 리스트 스키마
-- Supabase SQL Editor에서 실행하세요. (신규 / 기존 모두 가능)

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
  storage_path text,
  created_at timestamptz not null default now()
);

-- 기존 프로젝트: 물품에 사진 컬럼 추가
alter table text_items add column if not exists storage_path text;

create index if not exists text_items_category_id_idx on text_items (category_id);

insert into storage.buckets (id, name, public)
values ('photos', 'photos', true)
on conflict (id) do nothing;

alter table categories enable row level security;
alter table text_items enable row level security;

-- 계산기 모드: 지출 내역
create table if not exists expenses (
  id bigint generated always as identity primary key,
  title text not null,
  amount numeric(12, 0) not null check (amount >= 0),
  category text not null,
  created_at timestamptz not null default now()
);

create index if not exists expenses_category_idx on expenses (category);
create index if not exists expenses_created_at_idx on expenses (created_at);

alter table expenses enable row level security;
