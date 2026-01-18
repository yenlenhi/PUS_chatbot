-- Comprehensive Migration to add ALL potentially missing columns to document_attachments table

-- 1. Add 'description' column if it doesn't exist
ALTER TABLE document_attachments 
ADD COLUMN IF NOT EXISTS description TEXT;

-- 2. Add 'keywords' column if it doesn't exist
ALTER TABLE document_attachments 
ADD COLUMN IF NOT EXISTS keywords TEXT[] DEFAULT '{}';

-- 3. Add 'category' column if it doesn't exist
ALTER TABLE document_attachments 
ADD COLUMN IF NOT EXISTS category VARCHAR(50) DEFAULT 'Khác';

-- 4. Add 'is_active' column if it doesn't exist (CRITICAL for filters)
ALTER TABLE document_attachments 
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- 5. Add 'created_at' column if it doesn't exist (CRITICAL for sorting)
ALTER TABLE document_attachments 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

-- 6. Add 'updated_at' column if it doesn't exist
ALTER TABLE document_attachments 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

-- Verify all columns
SELECT column_name, data_type, column_default
FROM information_schema.columns 
WHERE table_name = 'document_attachments';
