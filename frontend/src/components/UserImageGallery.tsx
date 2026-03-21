'use client';
/* eslint-disable @next/next/no-img-element */

import React, { useEffect, useState } from 'react';
import { Download, Eye, RefreshCw } from 'lucide-react';

interface UploadedImageInfo {
  id: string;
  name: string;
  url: string;
  size?: number;
  uploadedAt: string;
  mimeType?: string;
}

interface UserImageGalleryProps {
  onImageSelect?: (imageUrl: string) => void;
  showControls?: boolean;
  className?: string;
}

const UserImageGallery: React.FC<UserImageGalleryProps> = ({
  onImageSelect,
  showControls = true,
  className = '',
}) => {
  const [images, setImages] = useState<UploadedImageInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);

  const fetchImages = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/upload/images');
      const result = await response.json();

      if (result.success) {
        setImages(result.files || []);
      } else {
        setError(result.error || 'Loi tai danh sach anh');
      }
    } catch (err) {
      console.error('Error fetching images:', err);
      setError('Loi ket noi khi tai anh');
    } finally {
      setLoading(false);
    }
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'N/A';
    const kb = bytes / 1024;
    const mb = kb / 1024;
    return mb > 1 ? `${mb.toFixed(2)} MB` : `${kb.toFixed(2)} KB`;
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString('vi-VN');
    } catch {
      return dateString;
    }
  };

  useEffect(() => {
    fetchImages();
  }, []);

  return (
    <div className={className}>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">
          Anh da tai len ({images.length})
        </h3>
        <button
          onClick={fetchImages}
          disabled={loading}
          className="flex items-center gap-2 rounded-lg bg-blue-100 px-3 py-2 text-blue-700 transition-colors hover:bg-blue-200 disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Lam moi
        </button>
      </div>

      <p className="mb-4 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-700">
        Tinh nang xoa anh da tam khoa tren giao dien demo.
      </p>

      {error && (
        <div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-600">
          {error}
        </div>
      )}

      {loading && (
        <div className="py-8 text-center">
          <div className="mx-auto mb-2 h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
          <p className="text-gray-500">Dang tai anh...</p>
        </div>
      )}

      {!loading && images.length === 0 && (
        <div className="py-8 text-center text-gray-500">
          <p>Chua co anh nao duoc tai len</p>
        </div>
      )}

      {!loading && images.length > 0 && (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
          {images.map((image) => (
            <div
              key={image.id}
              className="group relative overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm transition-shadow hover:shadow-md"
            >
              <div className="relative aspect-square">
                <img
                  src={image.url}
                  alt={image.name}
                  className="h-full w-full cursor-pointer object-cover"
                  onClick={() => {
                    setSelectedImage(image.url);
                    onImageSelect?.(image.url);
                  }}
                />

                {showControls && (
                  <div className="absolute inset-0 flex items-center justify-center gap-2 bg-black/50 opacity-0 transition-opacity group-hover:opacity-100">
                    <button
                      onClick={() => setSelectedImage(image.url)}
                      className="rounded-full bg-white/20 p-2 transition-colors hover:bg-white/40"
                      title="Xem anh"
                    >
                      <Eye className="h-4 w-4 text-white" />
                    </button>

                    <a
                      href={image.url}
                      download={image.name}
                      className="rounded-full bg-white/20 p-2 transition-colors hover:bg-white/40"
                      title="Tai xuong"
                    >
                      <Download className="h-4 w-4 text-white" />
                    </a>
                  </div>
                )}
              </div>

              <div className="p-3">
                <p className="truncate text-sm font-medium text-gray-900" title={image.name}>
                  {image.name}
                </p>
                <div className="mt-1 space-y-1 text-xs text-gray-500">
                  <p>{formatFileSize(image.size)}</p>
                  <p>{formatDate(image.uploadedAt)}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedImage && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4"
          onClick={() => setSelectedImage(null)}
        >
          <div className="relative max-h-full max-w-4xl">
            <img
              src={selectedImage}
              alt="Preview"
              className="max-h-full max-w-full object-contain"
              onClick={(e) => e.stopPropagation()}
            />
            <button
              onClick={() => setSelectedImage(null)}
              className="absolute right-4 top-4 rounded-full bg-black/50 p-2 text-white transition-colors hover:bg-black/70"
            >
              x
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserImageGallery;
