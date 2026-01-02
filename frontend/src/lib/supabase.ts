// Supabase Storage utility functions
import { createClient } from '@supabase/supabase-js';

// Supabase Storage URL configuration
const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://thessjemstjljfbkvzih.supabase.co';
const SUPABASE_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
const STORAGE_BUCKET = process.env.NEXT_PUBLIC_SUPABASE_STORAGE_BUCKET || 'documents';
const USER_IMAGES_BUCKET = 'user-images';

// Create Supabase client
export const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

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

/**
 * Get the public URL for a user uploaded image
 * @param filename - The filename of the image in user-images bucket
 * @returns The public URL of the image
 */
export function getUserImageUrl(filename: string): string {
  const { data } = supabase.storage
    .from(USER_IMAGES_BUCKET)
    .getPublicUrl(filename);
  
  return data.publicUrl;
}

/**
 * Upload image to user-images bucket
 * @param file - File to upload
 * @param fileName - Optional custom filename
 * @returns Upload result with public URL
 */
export async function uploadUserImage(file: File, fileName?: string) {
  if (!fileName) {
    const timestamp = Date.now();
    const randomString = Math.random().toString(36).substring(2, 15);
    const fileExtension = file.name.split('.').pop() || 'jpg';
    fileName = `img_${timestamp}_${randomString}.${fileExtension}`;
  }

  const { data, error } = await supabase.storage
    .from(USER_IMAGES_BUCKET)
    .upload(fileName, file, {
      contentType: file.type,
      cacheControl: '3600',
      upsert: false
    });

  if (error) {
    throw error;
  }

  const { data: urlData } = supabase.storage
    .from(USER_IMAGES_BUCKET)
    .getPublicUrl(fileName);

  return {
    path: data.path,
    url: urlData.publicUrl,
    fileName
  };
}

/**
 * Delete image from user-images bucket
 * @param filePath - Path to the file in the bucket
 * @returns Deletion result
 */
export async function deleteUserImage(filePath: string) {
  const { error } = await supabase.storage
    .from(USER_IMAGES_BUCKET)
    .remove([filePath]);

  if (error) {
    throw error;
  }

  return { success: true };
}

export default {
  getDocumentUrl,
  getDocumentDownloadUrl,
  isPdfDocument,
  formatDocumentName,
  SUPABASE_URL,
  STORAGE_BUCKET,
};
