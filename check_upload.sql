-- Check the latest uploaded file and its path
SELECT id, filename, file_path, category, created_at 
FROM document_attachments 
ORDER BY created_at DESC 
LIMIT 5;
