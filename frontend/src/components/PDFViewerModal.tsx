'use client';

import React, { useCallback, useEffect, useRef, useState } from 'react';
import { X, Download, ChevronLeft, ChevronRight, Loader2, RefreshCw, ZoomIn, ZoomOut } from 'lucide-react';

interface PDFViewerModalProps {
  isOpen: boolean;
  onClose: () => void;
  filename: string;
  initialPage?: number;
  backendUrl?: string;
}

const MIN_ZOOM = 0.75;
const MAX_ZOOM = 2;
const ZOOM_STEP = 0.2;
const VIEWER_HORIZONTAL_PADDING = 48;

type PdfRenderTask = {
  promise: Promise<void>;
  cancel: () => void;
};

type PdfViewport = {
  width: number;
  height: number;
};

type PdfPage = {
  getViewport: (options: { scale: number }) => PdfViewport;
  render: (options: {
    canvas: HTMLCanvasElement | null;
    canvasContext?: CanvasRenderingContext2D;
    viewport: PdfViewport;
    transform?: number[];
    background?: string;
  }) => PdfRenderTask;
  cleanup: () => void;
};

type PdfDocument = {
  numPages: number;
  getPage: (pageNumber: number) => Promise<PdfPage>;
  destroy: () => Promise<void> | void;
};

type PdfLoadingTask = {
  promise: Promise<PdfDocument>;
  destroy: () => void;
};

type PdfJsModule = {
  GlobalWorkerOptions: {
    workerSrc: string;
  };
  getDocument: (options: { url: string; withCredentials: boolean }) => PdfLoadingTask;
};

const PDFViewerModal: React.FC<PDFViewerModalProps> = ({
  isOpen,
  onClose,
  filename,
  initialPage = 1,
  backendUrl = '',
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const viewerRef = useRef<HTMLDivElement | null>(null);
  const pdfJsRef = useRef<PdfJsModule | null>(null);
  const loadingTaskRef = useRef<PdfLoadingTask | null>(null);
  const renderTaskRef = useRef<PdfRenderTask | null>(null);
  const [pdfDocument, setPdfDocument] = useState<PdfDocument | null>(null);
  const [isDocumentLoading, setIsDocumentLoading] = useState(false);
  const [isPageRendering, setIsPageRendering] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [totalPages, setTotalPages] = useState<number | null>(null);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [containerWidth, setContainerWidth] = useState(0);
  const [retryToken, setRetryToken] = useState(0);
  const normalizedBackendUrl = backendUrl.replace(/\/$/, '');
  const documentApiUrl = `${normalizedBackendUrl}/api/documents/${encodeURIComponent(filename)}`;
  const isBusy = isDocumentLoading || isPageRendering;

  const getFriendlyError = (value: unknown) => {
    if (value && typeof value === 'object' && 'message' in value && typeof value.message === 'string') {
      if (value.message.includes('MissingPDFException')) {
        return 'Tài liệu không tồn tại hoặc đã bị xóa.';
      }
      return value.message;
    }
    return 'Không thể hiển thị tài liệu PDF lúc này.';
  };

  const isRenderCancellation = (value: unknown) =>
    value instanceof Error && value.name === 'RenderingCancelledException';

  const clampPage = useCallback(
    (page: number, pageCount: number | null = totalPages) => {
      if (!pageCount || pageCount < 1) {
        return Math.max(1, page);
      }
      return Math.min(Math.max(1, page), pageCount);
    },
    [totalPages],
  );

  const handlePrevPage = useCallback(() => {
    setCurrentPage((page) => clampPage(page - 1));
  }, [clampPage]);

  const handleNextPage = useCallback(() => {
    setCurrentPage((page) => clampPage(page + 1));
  }, [clampPage]);

  const handleRetry = () => {
    setError(null);
    setRetryToken((token) => token + 1);
  };

  const formatFileName = (name: string) => {
    return name.replace(/\.[^/.]+$/, '').replace(/_/g, ' ');
  };

  const ensurePdfJs = useCallback(async (): Promise<PdfJsModule> => {
    if (pdfJsRef.current) {
      return pdfJsRef.current;
    }

    const pdfjs = (await import('pdfjs-dist/legacy/build/pdf.mjs')) as unknown as PdfJsModule;
    if (!pdfjs.GlobalWorkerOptions.workerSrc) {
      pdfjs.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.mjs';
    }

    pdfJsRef.current = pdfjs;
    return pdfjs;
  }, []);

  const handleDownload = async () => {
    setIsDownloading(true);
    try {
      const response = await fetch(documentApiUrl, { cache: 'no-store' });
      if (!response.ok) {
        throw new Error('Không thể tải xuống tài liệu lúc này.');
      }

      const blob = await response.blob();
      const blobUrl = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(blobUrl);
    } catch (downloadError) {
      setError(getFriendlyError(downloadError));
    } finally {
      setIsDownloading(false);
    }
  };

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    setCurrentPage(initialPage);
    setZoomLevel(1);
    setError(null);
  }, [isOpen, initialPage, filename]);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    const container = viewerRef.current;
    if (!container || typeof ResizeObserver === 'undefined') {
      return;
    }

    const updateWidth = () => {
      setContainerWidth(container.clientWidth);
    };

    updateWidth();

    const observer = new ResizeObserver(() => updateWidth());
    observer.observe(container);

    return () => observer.disconnect();
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) {
      setPdfDocument(null);
      setTotalPages(null);
      return;
    }

    let disposed = false;
    let loadedDocument: PdfDocument | null = null;

    const loadDocument = async () => {
      setIsDocumentLoading(true);
      setError(null);
      setTotalPages(null);
      setPdfDocument(null);

      renderTaskRef.current?.cancel();
      renderTaskRef.current = null;
      loadingTaskRef.current?.destroy();

      try {
        const pdfjs = await ensurePdfJs();
        const loadingTask = pdfjs.getDocument({
          url: documentApiUrl,
          withCredentials: false,
        });

        loadingTaskRef.current = loadingTask;
        const pdf = await loadingTask.promise;
        loadedDocument = pdf;

        if (disposed) {
          await pdf.destroy();
          return;
        }

        const boundedInitialPage = Math.min(Math.max(1, initialPage), pdf.numPages);

        setPdfDocument(pdf);
        setTotalPages(pdf.numPages);
        setCurrentPage(boundedInitialPage);
      } catch (loadError) {
        if (disposed) {
          return;
        }

        setError(getFriendlyError(loadError));
      } finally {
        if (!disposed) {
          setIsDocumentLoading(false);
        }
      }
    };

    void loadDocument();

    return () => {
      disposed = true;
      renderTaskRef.current?.cancel();
      renderTaskRef.current = null;
      loadingTaskRef.current?.destroy();
      loadingTaskRef.current = null;

      if (loadedDocument) {
        void loadedDocument.destroy();
      }
    };
  }, [isOpen, documentApiUrl, initialPage, retryToken, ensurePdfJs]);

  useEffect(() => {
    if (!isOpen || !pdfDocument || !canvasRef.current || !containerWidth) {
      return;
    }

    let disposed = false;

    const renderPage = async () => {
      setIsPageRendering(true);
      setError(null);
      renderTaskRef.current?.cancel();
      renderTaskRef.current = null;

      try {
        const page = await pdfDocument.getPage(currentPage);
        const baseViewport = page.getViewport({ scale: 1 });
        const availableWidth = Math.max(containerWidth - VIEWER_HORIZONTAL_PADDING, 280);
        const scale = Math.max((availableWidth / baseViewport.width) * zoomLevel, 0.25);
        const viewport = page.getViewport({ scale });
        const canvas = canvasRef.current;

        if (!canvas) {
          page.cleanup();
          return;
        }

        const context = canvas.getContext('2d', { alpha: false });
        if (!context) {
          page.cleanup();
          throw new Error('Không khởi tạo được vùng hiển thị PDF.');
        }

        const outputScale = window.devicePixelRatio || 1;
        canvas.width = Math.floor(viewport.width * outputScale);
        canvas.height = Math.floor(viewport.height * outputScale);
        canvas.style.width = `${Math.floor(viewport.width)}px`;
        canvas.style.height = `${Math.floor(viewport.height)}px`;
        const transform = outputScale !== 1 ? [outputScale, 0, 0, outputScale, 0, 0] : undefined;

        const renderTask = page.render({
          canvas: null,
          canvasContext: context,
          viewport,
          transform,
          background: 'rgb(255,255,255)',
        });

        renderTaskRef.current = renderTask;
        await renderTask.promise;
        page.cleanup();
      } catch (renderError) {
        if (disposed || isRenderCancellation(renderError)) {
          return;
        }

        setError(getFriendlyError(renderError));
      } finally {
        if (!disposed) {
          setIsPageRendering(false);
        }
      }
    };

    void renderPage();

    return () => {
      disposed = true;
      renderTaskRef.current?.cancel();
      renderTaskRef.current = null;
    };
  }, [isOpen, pdfDocument, currentPage, containerWidth, zoomLevel]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (!isOpen) {
        return;
      }

      if (event.key === 'Escape') {
        onClose();
      }
      if (event.key === 'ArrowLeft') {
        handlePrevPage();
      }
      if (event.key === 'ArrowRight') {
        handleNextPage();
      }
      if ((event.key === '+' || event.key === '=') && !event.ctrlKey && !event.metaKey) {
        setZoomLevel((zoom) => Math.min(MAX_ZOOM, zoom + ZOOM_STEP));
      }
      if (event.key === '-' && !event.ctrlKey && !event.metaKey) {
        setZoomLevel((zoom) => Math.max(MIN_ZOOM, zoom - ZOOM_STEP));
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose, handlePrevPage, handleNextPage]);

  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />

      <div className="relative w-full max-w-6xl h-[90vh] mx-4 bg-white rounded-xl shadow-2xl flex flex-col overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-red-600 to-red-700 text-white">
          <div className="flex items-center gap-3">
            <h3 className="font-semibold truncate max-w-md" title={filename}>
              {formatFileName(filename)}
            </h3>
            {initialPage && (
              <span className="text-sm bg-white/20 px-2 py-0.5 rounded">
                Trang {initialPage}
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1 bg-white/20 rounded px-2 py-1">
              <button
                onClick={handlePrevPage}
                disabled={currentPage <= 1}
                className="p-1 hover:bg-white/20 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                title="Trang trước"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="text-sm min-w-[80px] text-center">
                {currentPage} {totalPages ? `/ ${totalPages}` : ''}
              </span>
              <button
                onClick={handleNextPage}
                disabled={totalPages !== null && currentPage >= totalPages}
                className="p-1 hover:bg-white/20 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                title="Trang sau"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>

            <div className="flex items-center gap-1 bg-white/20 rounded px-2 py-1">
              <button
                onClick={() => setZoomLevel((zoom) => Math.max(MIN_ZOOM, zoom - ZOOM_STEP))}
                disabled={zoomLevel <= MIN_ZOOM}
                className="p-1 hover:bg-white/20 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                title="Thu nhỏ"
              >
                <ZoomOut className="w-4 h-4" />
              </button>
              <span className="text-sm min-w-[56px] text-center">{Math.round(zoomLevel * 100)}%</span>
              <button
                onClick={() => setZoomLevel((zoom) => Math.min(MAX_ZOOM, zoom + ZOOM_STEP))}
                disabled={zoomLevel >= MAX_ZOOM}
                className="p-1 hover:bg-white/20 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                title="Phóng to"
              >
                <ZoomIn className="w-4 h-4" />
              </button>
            </div>

            <button
              onClick={() => void handleDownload()}
              disabled={isDownloading}
              className="p-2 hover:bg-white/20 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Tải xuống"
            >
              {isDownloading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Download className="w-4 h-4" />
              )}
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded transition-colors"
              title="Đóng (Esc)"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div ref={viewerRef} className="flex-1 relative bg-gray-200 overflow-auto">
          {isBusy && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-100/90 z-10">
              <div className="flex flex-col items-center gap-3">
                <Loader2 className="w-8 h-8 animate-spin text-red-600" />
                <p className="text-gray-600">
                  {isDocumentLoading ? 'Đang tải tài liệu...' : 'Đang dựng trang PDF...'}
                </p>
              </div>
            </div>
          )}

          {error && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-100/95 z-20">
              <div className="text-center p-6">
                <p className="text-red-600 font-medium mb-2">Không thể hiển thị tài liệu</p>
                <p className="text-gray-500 text-sm mb-4">{error}</p>
                <div className="flex flex-col sm:flex-row gap-2 justify-center">
                  <button
                    onClick={handleRetry}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                  >
                    <RefreshCw className="w-4 h-4" />
                    Thử lại
                  </button>
                  <button
                    onClick={() => void handleDownload()}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    Tải PDF
                  </button>
                </div>
              </div>
            </div>
          )}

          <div className="min-h-full flex items-start justify-center p-6">
            <div className="rounded-xl bg-white shadow-2xl ring-1 ring-black/5 overflow-hidden">
              <canvas ref={canvasRef} className="block max-w-full h-auto" aria-label={filename} />
            </div>
          </div>
        </div>

        <div className="px-4 py-2 bg-gray-50 border-t text-xs text-gray-500 flex justify-between">
          <span>Dùng ← → để chuyển trang, +/- để zoom, Esc để đóng</span>
          <span>{filename}</span>
        </div>
      </div>
    </div>
  );
};

export default PDFViewerModal;
