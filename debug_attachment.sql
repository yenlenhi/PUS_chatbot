-- Search for the attachment by name or description to see its current state
SELECT * 
FROM document_attachments 
WHERE filename ILIKE '%tiếp tục học%' OR description ILIKE '%tiếp tục học%' OR 'tiếp tục học' = ANY(keywords);
