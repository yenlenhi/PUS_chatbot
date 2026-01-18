'use client';

import React from 'react';
import { FileText, Download, FileSpreadsheet, File } from 'lucide-react';
import type { FileAttachment } from '@/types';

interface AttachmentListProps {
    attachments: FileAttachment[];
    className?: string;
}

const AttachmentList: React.FC<AttachmentListProps> = ({ attachments, className = '' }) => {
    if (!attachments || attachments.length === 0) {
        return null;
    }

    const getFileIcon = (filename: string) => {
        const extension = filename.split('.').pop()?.toLowerCase();

        switch (extension) {
            case 'pdf':
                return <FileText className="w-5 h-5 text-red-500" />;
            case 'doc':
            case 'docx':
                return <FileText className="w-5 h-5 text-blue-500" />;
            case 'xls':
            case 'xlsx':
                return <FileSpreadsheet className="w-5 h-5 text-green-500" />;
            default:
                return <File className="w-5 h-5 text-gray-500" />;
        }
    };

    const formatFileSize = (bytes?: number) => {
        if (!bytes) return '';
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    };

    return (
        <div className={`mt-3 ${className}`}>
            <p className="text-xs text-gray-500 mb-2 font-medium flex items-center gap-1">
                <Download className="w-3 h-3" />
                Tài liệu đính kèm:
            </p>
            <div className="grid gap-2 grid-cols-1 sm:grid-cols-2">
                {attachments.map((file, index) => (
                    <a
                        key={index}
                        href={file.download_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center space-x-3 p-3 bg-white/80 hover:bg-white border boundary-gray-200 hover:border-blue-300 rounded-lg shadow-sm hover:shadow transition-all duration-200 group no-underline"
                    >
                        <div className="flex-shrink-0 p-2 bg-gray-50 rounded-md group-hover:bg-blue-50 transition-colors">
                            {getFileIcon(file.file_name)}
                        </div>

                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 truncate group-hover:text-blue-600 transition-colors">
                                {file.file_name}
                            </p>
                            <div className="flex items-center space-x-2 mt-0.5">
                                {file.category && (
                                    <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                                        {file.category}
                                    </span>
                                )}
                                <span className="text-xs text-gray-500">
                                    {formatFileSize(file.file_size)}
                                </span>
                            </div>
                        </div>

                        <div className="flex-shrink-0 text-gray-400 group-hover:text-blue-500">
                            <Download className="w-4 h-4" />
                        </div>
                    </a>
                ))}
            </div>
        </div>
    );
};

export default AttachmentList;
