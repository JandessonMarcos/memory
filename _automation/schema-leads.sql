-- Memory Lab — lead capture (Cloudflare D1 / SQLite)
-- Binding: DB   (configure on the Pages project: Settings -> Functions -> Bindings)
-- Written by: functions/api/lead.js  (POST /api/lead)

CREATE TABLE IF NOT EXISTS leads (
  id               INTEGER PRIMARY KEY AUTOINCREMENT,
  lead_id          TEXT,                         -- short id from quiz.js (joins to subid)
  email            TEXT NOT NULL,
  subid            TEXT,                         -- quiz_<lead_id>_<segment>; matches sales.subid later
  segment          TEXT,                         -- ssym_aage_ddur_ttried
  q_symptom        TEXT,
  q_age            TEXT,
  q_dur            TEXT,
  q_tried          TEXT,
  source_page      TEXT,
  referrer         TEXT,
  incoming_clickid TEXT,                         -- original ad click id, if they arrived from paid
  utm_source       TEXT,
  utm_medium       TEXT,
  utm_campaign     TEXT,
  country          TEXT,
  ua               TEXT,
  status           TEXT NOT NULL DEFAULT 'new',  -- new | emailed | converted | unsub
  event_day        TEXT NOT NULL,                -- YYYY-MM-DD
  created_at       TEXT NOT NULL,                -- ISO 8601
  raw              TEXT                          -- full JSON payload (audit)
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_leads_email ON leads(email);
CREATE INDEX        IF NOT EXISTS idx_leads_day   ON leads(event_day);
CREATE INDEX        IF NOT EXISTS idx_leads_subid ON leads(subid);
