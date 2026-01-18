-- Migration to add category column to document_attachments table
-- Run this in your Supabase SQL Editor if the Python script fails

ALTER TABLE document_attachments 
ADD COLUMN IF NOT EXISTS category VARCHAR(50) DEFAULT 'Khác';

-- Verify the column was added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'document_attachments' AND column_name = 'category';
