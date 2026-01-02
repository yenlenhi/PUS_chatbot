'use client';

import React, { useRef, useState, useCallback } from 'react';
import { ImagePlus, X, ZoomIn } from 'lucide-react';

export interface UploadedImage {
  id: string;
  name: string;
  mimeType: string;
  file?: File;
  preview: string;
  base64: string;
  serverUrl?: string; // URL after uploaded to server (Supabase)
  serverId?: string; // Server-generated ID
  supabasePath?: string; // Supabase Storage path
}

interface ImageUploadProps {
  images: UploadedImage[];
  onImagesChange: (images: UploadedImage[]) => void;
  maxImages?: number;
  maxSizeMB?: number;
  disabled?: boolean;
  className?: string;
}

const ImageUpload: React.FC<ImageUploadProps> = ({
  images,
  onImagesChange,
  maxImages = 4,
  maxSizeMB = 2,
  disabled = false,
  className = ''
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [previewImage, setPreviewImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const uploadImagesToServer = async (imageFiles: File[]) => {
    setUploading(true);
    setUploadProgress(0);
    
    try {
      const formData = new FormData();
      imageFiles.forEach((file, index) => {
        formData.append(`images${index}`, file);
      });

      const response = await fetch('/api/upload/images', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.error || 'Đã xảy ra lỗi khi upload');
      }

      setUploadProgress(100);
      return result.files;
    } catch (error) {
      console.error('Error uploading images:', error);
      throw error;
    } finally {
      setUploading(false);
      setTimeout(() => setUploadProgress(0), 1000);
    }
  };

  const convertToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = error => reject(error);
    });
  };

  const handleFileSelect = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setError(null);

    const remainingSlots = maxImages - images.length;
    if (remainingSlots <= 0) {
      setError(`Chỉ được tải tối đa ${maxImages} ảnh`);
      return;
    }

    const filesToProcess = Array.from(files).slice(0, remainingSlots);
    const newImages: UploadedImage[] = [];

    for (const file of filesToProcess) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setError('Chỉ hỗ trợ file ảnh (PNG, JPG, GIF, WebP)');
        continue;
      }

      // Validate file size (max 2MB)
      const sizeMB = file.size / (1024 * 1024);
      if (sizeMB > maxSizeMB) {
        setError(`Ảnh "${file.name}" vượt quá giới hạn ${maxSizeMB}MB (hiện tại: ${sizeMB.toFixed(2)}MB)`);
        continue;
      }

      try {
        const base64 = await convertToBase64(file);
        const preview = URL.createObjectURL(file);

        newImages.push({
          id: `img-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          name: file.name,
          mimeType: file.type,
          file,
          preview,
          base64
        });
      } catch (err) {
        console.error('Error processing image:', err);
        setError('Lỗi xử lý ảnh');
      }
    }

    if (newImages.length > 0) {
      try {
        // Upload images to server
        const uploadedFiles = await uploadImagesToServer(newImages.map(img => img.file!));
        
        // Update images with server URLs
        const imagesWithUrls = newImages.map((img, index) => ({
          ...img,
          serverUrl: uploadedFiles[index]?.url,
          serverId: uploadedFiles[index]?.id,
          supabasePath: uploadedFiles[index]?.supabasePath
        }));
        
        onImagesChange([...images, ...imagesWithUrls]);
        setError(null); // Clear any previous errors
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Lỗi upload ảnh');
        // Don't add images if upload fails
      }
    }

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [images, maxImages, maxSizeMB, onImagesChange]);

  const handleRemoveImage = useCallback((id: string) => {
    const imageToRemove = images.find(img => img.id === id);
    if (imageToRemove) {
      URL.revokeObjectURL(imageToRemove.preview);
    }
    onImagesChange(images.filter(img => img.id !== id));
  }, [images, onImagesChange]);

  const handleButtonClick = () => {
    if (!disabled && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <div className={className}>
      {/* Error message */}
      {error && (
        <div className="mb-2 px-3 py-2 bg-red-50 border border-red-200 rounded-lg text-red-600 text-xs">
          {error}
        </div>
      )}

      {/* Upload progress */}
      {uploading && (
        <div className="mb-2 px-3 py-2 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center justify-between text-blue-600 text-xs mb-1">
            <span>Đang tải ảnh lên...</span>
            <span>{uploadProgress}%</span>
          </div>
          <div className="w-full bg-blue-200 rounded-full h-1.5">
            <div 
              className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Image previews */}
      {images.length > 0 && (
        <div className="mb-2 flex flex-wrap gap-2">
          {images.map((image) => (
            <div
              key={image.id}
              className="relative group w-16 h-16 rounded-lg overflow-hidden border border-gray-200 bg-gray-50"
            >
              <img
                src={image.preview}
                alt="Preview"
                className="w-full h-full object-cover"
              />
              {/* Overlay on hover */}
              <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-1">
                <button
                  type="button"
                  onClick={() => setPreviewImage(image.preview)}
                  className="p-1 bg-white/20 rounded-full hover:bg-white/40 transition-colors"
                  title="Xem ảnh"
                >
                  <ZoomIn className="w-3 h-3 text-white" />
                </button>
                <button
                  type="button"
                  onClick={() => handleRemoveImage(image.id)}
                  className="p-1 bg-white/20 rounded-full hover:bg-red-500/80 transition-colors"
                  title="Xóa ảnh"
                >
                  <X className="w-3 h-3 text-white" />
                </button>
              </div>
            </div>
          ))}

          {/* Add more button (if under limit) */}
          {images.length < maxImages && (
            <button
              type="button"
              onClick={handleButtonClick}
              disabled={disabled}
              className="w-16 h-16 rounded-lg border-2 border-dashed border-gray-300 hover:border-blue-400 flex items-center justify-center text-gray-400 hover:text-blue-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Thêm ảnh"
            >
              <ImagePlus className="w-5 h-5" />
            </button>
          )}
        </div>
      )}

      {/* Upload button (when no images) */}
      {images.length === 0 && (
        <button
          type="button"
          onClick={handleButtonClick}
          disabled={disabled}
          className="p-3 rounded-xl bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          title="Tải ảnh lên"
        >
          <ImagePlus className="w-5 h-5" />
        </button>
      )}

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        multiple
        onChange={handleFileSelect}
        className="hidden"
        disabled={disabled}
      />

      {/* Full preview modal */}
      {previewImage && (
        <div
          className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4"
          onClick={() => setPreviewImage(null)}
        >
          <button
            onClick={() => setPreviewImage(null)}
            className="absolute top-4 right-4 p-2 bg-white/20 rounded-full hover:bg-white/40 transition-colors"
          >
            <X className="w-6 h-6 text-white" />
          </button>
          <img
            src={previewImage}
            alt="Full preview"
            className="max-w-full max-h-full object-contain rounded-lg"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </div>
  );
};

export default ImageUpload;
