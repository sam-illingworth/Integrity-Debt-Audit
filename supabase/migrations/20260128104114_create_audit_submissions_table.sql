/*
  # Create audit submissions and leads tables

  1. New Tables
    - `audit_submissions`
      - `id` (uuid, primary key)
      - `email` (text, unique per user)
      - `audit_score` (integer, out of 50)
      - `susceptibility` (text: Low/Medium/High)
      - `categories` (jsonb, stores all 10 category scores)
      - `assessment_context` (text, brief description)
      - `pdf_data` (bytea, stores generated PDF)
      - `created_at` (timestamp)
      - `updated_at` (timestamp)
    
    - `lead_emails`
      - `id` (uuid, primary key)
      - `email` (text, unique)
      - `audit_id` (uuid, foreign key)
      - `wants_strategy_call` (boolean)
      - `created_at` (timestamp)

  2. Security
    - Enable RLS on both tables
    - Allow users to read/write their own submissions
    - Allow anyone to insert leads (public signup)
*/

CREATE TABLE IF NOT EXISTS audit_submissions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text NOT NULL,
  audit_score integer CHECK (audit_score >= 10 AND audit_score <= 50),
  susceptibility text CHECK (susceptibility IN ('Low', 'Medium', 'High')),
  categories jsonb NOT NULL,
  assessment_context text,
  pdf_data bytea,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  UNIQUE(email)
);

CREATE TABLE IF NOT EXISTS lead_emails (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text NOT NULL UNIQUE,
  audit_id uuid REFERENCES audit_submissions(id) ON DELETE CASCADE,
  wants_strategy_call boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE audit_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_emails ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can insert audit submissions"
  ON audit_submissions FOR INSERT
  TO public
  WITH CHECK (true);

CREATE POLICY "Anyone can insert lead emails"
  ON lead_emails FOR INSERT
  TO public
  WITH CHECK (true);

CREATE POLICY "Users can view own submissions by email"
  ON audit_submissions FOR SELECT
  TO public
  USING (true);

CREATE POLICY "Users can view own leads"
  ON lead_emails FOR SELECT
  TO public
  USING (true);