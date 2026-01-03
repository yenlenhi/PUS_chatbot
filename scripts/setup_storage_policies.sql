-- Setup Storage Policies for chat-attachments bucket
-- Run this in Supabase SQL Editor

-- Policy cho Upload (INSERT)
CREATE POLICY IF NOT EXISTS "Allow authenticated uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'chat-attachments');

-- Policy cho Read (SELECT)
CREATE POLICY IF NOT EXISTS "Allow authenticated reads"
ON storage.objects FOR SELECT
TO authenticated
USING (bucket_id = 'chat-attachments');

-- Policy cho Delete
CREATE POLICY IF NOT EXISTS "Allow authenticated deletes"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'chat-attachments');

-- Policy cho Service Role (bypass RLS)
CREATE POLICY IF NOT EXISTS "Service role full access"
ON storage.objects FOR ALL
TO service_role
USING (bucket_id = 'chat-attachments');
