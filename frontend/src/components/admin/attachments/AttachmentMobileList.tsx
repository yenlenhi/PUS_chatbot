
import React from 'react';
import { Eye, Trash2, Calendar, HardDrive } from 'lucide-react';
import { FileIcon } from './FileIcon';

interface Attachment {
    id: number;
    file_name: string;
    file_type: string;
    file_path: string;
    file_size?: number;
    description?: string;
    keywords?: string[];
    download_url: string;
    category?: string;
    is_active: boolean;
    created_at?: string;
    public_url?: string;
}

interface AttachmentMobileListProps {
    attachments: Attachment[];
    onPreview: (file: Attachment) => void;
    onDelete: (id: number) => void;
}

export const AttachmentMobileList: React.FC<AttachmentMobileListProps> = ({ attachments, onPreview, onDelete }) => {
    return (
        <div className="space-y-4 pb-20">
            {attachments.map((file) => (
                <div
                    key={file.id}
                    className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm active:scale-[0.99] transition-transform duration-200"
                >
                    {/* Header: Icon + Name */}
                    <div className="flex items-start gap-3 mb-3">
                        <div className="shrink-0">
                            <FileIcon fileName={file.file_name} size={40} />
                        </div>
                        <div className="flex-1 min-w-0">
                            <h4 className="text-sm font-semibold text-gray-900 leading-snug line-clamp-2 break-words">
                                {file.file_name}
                            </h4>

                            {/* Metadata Badges */}
                            <div className="flex flex-wrap gap-2 mt-2">
                                <span className="inline-flex items-center rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10">
                                    {file.category || 'Khác'}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Footer Info */}
                    <div className="flex items-center gap-4 text-xs text-gray-500 mb-4 px-1">
                        <div className="flex items-center gap-1.5">
                            <HardDrive size={14} className="text-gray-400" />
                            <span>{(file.file_size ? file.file_size / 1024 : 0).toFixed(1)} KB</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                            <Calendar size={14} className="text-gray-400" />
                            <span>{file.created_at ? new Date(file.created_at).toLocaleDateString('vi-VN') : 'N/A'}</span>
                        </div>
                    </div>

                    {/* Action Grid */}
                    <div className="grid grid-cols-2 gap-3 border-t border-gray-100 pt-3">
                        <button
                            onClick={() => onPreview(file)}
                            className="flex items-center justify-center gap-2 px-3 py-2.5 bg-blue-50 text-blue-600 rounded-lg font-medium text-sm hover:bg-blue-100 active:bg-blue-200 transition-colors"
                        >
                            <Eye size={16} />
                            <span>Xem</span>
                        </button>
                        <button
                            onClick={() => onDelete(file.id)}
                            className="flex items-center justify-center gap-2 px-3 py-2.5 bg-white border border-gray-200 text-red-600 rounded-lg font-medium text-sm hover:bg-red-50 active:bg-red-100 transition-colors"
                        >
                            <Trash2 size={16} />
                            <span>Xóa</span>
                        </button>
                    </div>
                </div>
            ))}
        </div>
    );
};
