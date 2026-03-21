// Supabase Storage utility functions
import { createClient } from '@supabase/supabase-js';

// Supabase Storage URL configuration — all values must come from env variables
const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SUPABASE_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
const STORAGE_BUCKET = process.env.NEXT_PUBLIC_SUPABASE_STORAGE_BUCKET || 'documents';

if (!SUPABASE_URL || !SUPABASE_KEY) {
  throw new Error('Missing required Supabase environment variables: NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY');
}

// Create Supabase client
export const supabase = createClient(SUPABASE_URL!, SUPABASE_KEY!);

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
  
  return `${SUPABASE_URL!}/storage/v1/object/public/${STORAGE_BUCKET}/${encodedFilename}`;
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

const supabaseUtils = {
  getDocumentUrl,
  getDocumentDownloadUrl,
  isPdfDocument,
  formatDocumentName,
  SUPABASE_URL,
  STORAGE_BUCKET,
};

export default supabaseUtils;
