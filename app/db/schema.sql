CREATE SEQUENCE IF NOT EXISTS sources_seq;
CREATE SEQUENCE IF NOT EXISTS policies_seq;

CREATE TABLE IF NOT EXISTS sources (
  source_id INTEGER DEFAULT nextval('sources_seq'),
  url TEXT,
  fetched_at TIMESTAMP,
  clean_text TEXT
);

CREATE TABLE IF NOT EXISTS policies (
  policy_id INTEGER DEFAULT nextval('policies_seq'),
  source_id INTEGER,
  policy_area TEXT,
  promise TEXT,
  feasibility_score DOUBLE,
  notes TEXT,
  created_at TIMESTAMP
);
