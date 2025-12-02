'use client';

import React, { useState } from 'react';
import { ZoomIn, ZoomOut, X, Download, ExternalLink } from 'lucide-react';
import Image from 'next/image';

export interface ImageData {
  src: string; // URL hoặc base64
  alt?: string;
  caption?: string;
  source_file?: string;
  page_number?: number;
}

interface ImageRendererProps {
  images: ImageData[];
  className?: string;
}

const ImageRenderer: React.FC<ImageRendererProps> = ({ images, className = '' }) => {
  const [selectedImage, setSelectedImage] = useState<ImageData | null>(null);
  const [zoom, setZoom] = useState(1);

  if (!images || images.length === 0) {
    return null;
  }

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 0.25, 3));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 0.25, 0.5));
  };

  const handleDownload = (image: ImageData) => {
    const link = document.createElement('a');
    link.href = image.src;
    link.download = image.alt || 'image';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const isBase64 = (src: string) => src.startsWith('data:image');

  return (
    <>
      <div className={`my-3 ${className}`}>
        {images.length === 1 ? (
          // Single image
          <div 
            className="relative rounded-lg overflow-hidden border border-gray-200 cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => setSelectedImage(images[0])}
          >
            <img
              src={images[0].src}
              alt={images[0].alt || 'Hình ảnh'}
              className="w-full h-auto max-h-[400px] object-contain bg-gray-50"
            />
            {images[0].caption && (
              <p className="text-xs text-gray-500 p-2 bg-gray-50 text-center italic">
                {images[0].caption}
              </p>
            )}
            {images[0].source_file && (
              <p className="text-xs text-gray-400 px-2 pb-2 bg-gray-50 text-center">
                Nguồn: {images[0].source_file}
                {images[0].page_number && ` - Trang ${images[0].page_number}`}
              </p>
            )}
          </div>
        ) : (
          // Multiple images - grid layout
          <div className="grid grid-cols-2 gap-2">
            {images.map((image, index) => (
              <div
                key={index}
                className="relative rounded-lg overflow-hidden border border-gray-200 cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => setSelectedImage(image)}
              >
                <img
                  src={image.src}
                  alt={image.alt || `Hình ${index + 1}`}
                  className="w-full h-32 object-cover bg-gray-50"
                />
                {image.caption && (
                  <p className="text-xs text-gray-500 p-1 bg-gray-50 text-center truncate">
                    {image.caption}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Image Modal/Lightbox */}
      {selectedImage && (
        <div 
          className="fixed inset-0 z-50 bg-black bg-opacity-90 flex items-center justify-center"
          onClick={() => {
            setSelectedImage(null);
            setZoom(1);
          }}
        >
          <div 
            className="relative max-w-[90vw] max-h-[90vh]"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Controls */}
            <div className="absolute top-0 right-0 transform -translate-y-full flex items-center gap-2 p-2">
              <button
                onClick={handleZoomOut}
                className="p-2 bg-white rounded-full shadow-md hover:bg-gray-100 transition-colors"
                title="Thu nhỏ"
              >
                <ZoomOut className="w-5 h-5 text-gray-700" />
              </button>
              <span className="text-white text-sm bg-black bg-opacity-50 px-2 py-1 rounded">
                {Math.round(zoom * 100)}%
              </span>
              <button
                onClick={handleZoomIn}
                className="p-2 bg-white rounded-full shadow-md hover:bg-gray-100 transition-colors"
                title="Phóng to"
              >
                <ZoomIn className="w-5 h-5 text-gray-700" />
              </button>
              <button
                onClick={() => handleDownload(selectedImage)}
                className="p-2 bg-white rounded-full shadow-md hover:bg-gray-100 transition-colors"
                title="Tải xuống"
              >
                <Download className="w-5 h-5 text-gray-700" />
              </button>
              <button
                onClick={() => {
                  setSelectedImage(null);
                  setZoom(1);
                }}
                className="p-2 bg-white rounded-full shadow-md hover:bg-gray-100 transition-colors"
                title="Đóng"
              >
                <X className="w-5 h-5 text-gray-700" />
              </button>
            </div>

            {/* Image */}
            <div className="overflow-auto max-w-[90vw] max-h-[85vh]">
              <img
                src={selectedImage.src}
                alt={selectedImage.alt || 'Hình ảnh'}
                style={{ transform: `scale(${zoom})`, transformOrigin: 'center center' }}
                className="transition-transform duration-200"
              />
            </div>

            {/* Caption */}
            {(selectedImage.caption || selectedImage.source_file) && (
              <div className="absolute bottom-0 left-0 right-0 transform translate-y-full p-2 text-center">
                {selectedImage.caption && (
                  <p className="text-white text-sm">{selectedImage.caption}</p>
                )}
                {selectedImage.source_file && (
                  <p className="text-gray-300 text-xs">
                    Nguồn: {selectedImage.source_file}
                    {selectedImage.page_number && ` - Trang ${selectedImage.page_number}`}
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default ImageRenderer;
