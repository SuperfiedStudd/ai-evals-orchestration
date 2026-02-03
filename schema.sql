-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- 1. Experiments Table
create table public.experiments (
  experiment_id uuid default uuid_generate_v4() primary key,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  media_id text not null,
  status text not null, -- running, failed, complete
  decision text, -- ship, iterate, rollback
  decision_reason text,
  recommendation text,
  recommendation_reason text,
  tradeoffs jsonb,
  error_log text
);

-- 2. Model Runs Table
create table public.model_runs (
  run_id uuid default uuid_generate_v4() primary key,
  experiment_id uuid references public.experiments(experiment_id) not null,
  model_name text not null,
  raw_output text, -- or jsonb if structured
  latency_ms integer,
  cost_usd float,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 3. Evaluation Metrics Table
create table public.eval_metrics (
  eval_id uuid default uuid_generate_v4() primary key,
  run_id uuid references public.model_runs(run_id) not null,
  scores jsonb not null, -- Stores the list of scores
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
