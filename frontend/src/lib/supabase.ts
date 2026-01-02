// Supabase Storage utility functions

// Supabase Storage URL configuration
const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://thessjemstjljfbkvzih.supabase.co';
const STORAGE_BUCKET = process.env.NEXT_PUBLIC_SUPABASE_STORAGE_BUCKET || 'documents';

/**
 * Get the public URL for a document stored in Supabase Storage
 * @param filename - The filename of the document
 * @returns The public URL of the document
 */
export function getDocumentUrl(filename: string): string {
  // Normalize filename - remove path prefixes if any
  const normalizedFilename = filename.split('/').pop() || filename;
  
  // URL encode the filename for special characters
  const encodedFilename = encodeURIComponent(normalizedFilename);
  
  return `${SUPABASE_URL}/storage/v1/object/public/${STORAGE_BUCKET}/${encodedFilename}`;
}

/**
 * Get the download URL for a document (same as public URL for Supabase)
 * @param filename - The filename of the document
 * @returns The download URL of the document
 */
export function getDocumentDownloadUrl(filename: string): string {
  return getDocumentUrl(filename);
}

/**
 * Check if a filename is a PDF document
 * @param filename - The filename to check
 * @returns True if the file is a PDF
 */
export function isPdfDocument(filename: string): boolean {
  return filename.toLowerCase().endsWith('.pdf');
}

/**
 * Format filename for display (remove extension and clean up)
 * @param filename - The filename to format
 * @returns Formatted display name
 */
export function formatDocumentName(filename: string): string {
  return filename
    .replace(/\.(pdf|doc|docx|txt)$/i, '')
    .replace(/[_-]/g, ' ')
    .trim();
}

export default {
  getDocumentUrl,
  getDocumentDownloadUrl,
  isPdfDocument,
  formatDocumentName,
  SUPABASE_URL,
  STORAGE_BUCKET,
};
