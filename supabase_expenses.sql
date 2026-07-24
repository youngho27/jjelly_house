-- 계산기 모드용 (기존 프로젝트에 한 번 실행)
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
