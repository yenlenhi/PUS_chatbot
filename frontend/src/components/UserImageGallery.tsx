'use client';

import React, { useState, useEffect } from 'react';
import { Trash2, Eye, Download, RefreshCw } from 'lucide-react';
import { getUserImageUrl } from '@/lib/supabase';

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
  className = ''
}) => {
  const [images, setImages] = useState<UploadedImageInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fetchImages = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/upload/images');
      const result = await response.json();
      
      if (result.success) {
        setImages(result.files || []);
      } else {
        setError(result.error || 'Lỗi tải danh sách ảnh');
      }
    } catch (err) {
      console.error('Error fetching images:', err);
      setError('Lỗi kết nối khi tải ảnh');
    } finally {
      setLoading(false);
    }
  };

  const deleteImage = async (imageId: string, fileName: string) => {
    setDeletingId(imageId);
    
    try {
      const response = await fetch(`/api/upload/images/delete?fileName=${encodeURIComponent(fileName)}`, {
        method: 'DELETE'
      });
      
      const result = await response.json();
      
      if (result.success) {
        setImages(prev => prev.filter(img => img.id !== imageId));
      } else {
        alert(result.error || 'Lỗi xóa ảnh');
      }
    } catch (err) {
      console.error('Error deleting image:', err);
      alert('Lỗi kết nối khi xóa ảnh');
    } finally {
      setDeletingId(null);
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
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Ảnh đã tải lên ({images.length})
        </h3>
        <button
          onClick={fetchImages}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Làm mới
        </button>
      </div>

      {/* Error message */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="text-center py-8">
          <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-2"></div>
          <p className="text-gray-500">Đang tải ảnh...</p>
        </div>
      )}

      {/* Empty state */}
      {!loading && images.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <p>Chưa có ảnh nào được tải lên</p>
        </div>
      )}

      {/* Image grid */}
      {!loading && images.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {images.map((image) => (
            <div
              key={image.id}
              className="relative group bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow"
            >
              {/* Image */}
              <div className="aspect-square relative">
                <img
                  src={image.url}
                  alt={image.name}
                  className="w-full h-full object-cover cursor-pointer"
                  onClick={() => {
                    setSelectedImage(image.url);
                    onImageSelect?.(image.url);
                  }}
                />
                
                {/* Overlay controls */}
                {showControls && (
                  <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                    <button
                      onClick={() => setSelectedImage(image.url)}
                      className="p-2 bg-white/20 rounded-full hover:bg-white/40 transition-colors"
                      title="Xem ảnh"
                    >
                      <Eye className="w-4 h-4 text-white" />
                    </button>
                    
                    <a
                      href={image.url}
                      download={image.name}
                      className="p-2 bg-white/20 rounded-full hover:bg-white/40 transition-colors"
                      title="Tải xuống"
                    >
                      <Download className="w-4 h-4 text-white" />
                    </a>
                    
                    <button
                      onClick={() => deleteImage(image.id, image.name)}
                      disabled={deletingId === image.id}
                      className="p-2 bg-red-500/80 rounded-full hover:bg-red-600/80 transition-colors disabled:opacity-50"
                      title="Xóa ảnh"
                    >
                      <Trash2 className="w-4 h-4 text-white" />
                    </button>
                  </div>
                )}
              </div>
              
              {/* Info */}
              <div className="p-3">
                <p className="text-sm font-medium text-gray-900 truncate" title={image.name}>
                  {image.name}
                </p>
                <div className="text-xs text-gray-500 mt-1 space-y-1">
                  <p>{formatFileSize(image.size)}</p>
                  <p>{formatDate(image.uploadedAt)}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Image preview modal */}
      {selectedImage && (
        <div
          className="fixed inset-0 bg-black/75 z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedImage(null)}
        >
          <div className="relative max-w-4xl max-h-full">
            <img
              src={selectedImage}
              alt="Preview"
              className="max-w-full max-h-full object-contain"
              onClick={(e) => e.stopPropagation()}
            />
            <button
              onClick={() => setSelectedImage(null)}
              className="absolute top-4 right-4 p-2 bg-black/50 text-white rounded-full hover:bg-black/70 transition-colors"
            >
              ✕
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserImageGallery;