
import React from 'react';
import { Eye, Trash2 } from 'lucide-react';
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
        <div className="space-y-3">
            {attachments.map((file) => (
                <div key={file.id} className="bg-white rounded-xl border border-gray-100 p-3 shadow-sm flex items-start gap-3">
                    {/* Icon */}
                    <div className="shrink-0 mt-1">
                        <FileIcon fileName={file.file_name} size={28} />
                    </div>

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-gray-900 truncate text-sm" title={file.file_name}>
                            {file.file_name}
                        </h4>
                        <div className="flex items-center gap-2 mt-1 flex-wrap">
                            <span className="inline-flex items-center rounded-md bg-blue-50 px-1.5 py-0.5 text-[10px] font-medium text-blue-700">
                                {file.category || 'Khác'}
                            </span>
                            <span className="text-[10px] text-gray-400">•</span>
                            <span className="text-[10px] text-gray-500">
                                {(file.file_size ? file.file_size / 1024 : 0).toFixed(1)} KB
                            </span>
                            <span className="text-[10px] text-gray-400">•</span>
                            <span className="text-[10px] text-gray-400">
                                {file.created_at ? new Date(file.created_at).toLocaleDateString('vi-VN') : 'N/A'}
                            </span>
                        </div>
                    </div>

                    {/* Actions - Always Visible */}
                    <div className="flex flex-col gap-1 shrink-0">
                        <button
                            onClick={() => onPreview(file)}
                            className="p-2 bg-gray-50 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
                            aria-label="Xem trước"
                        >
                            <Eye size={18} />
                        </button>
                        <button
                            onClick={() => onDelete(file.id)}
                            className="p-2 bg-gray-50 text-red-600 rounded-lg hover:bg-red-50 transition-colors"
                            aria-label="Xóa"
                        >
                            <Trash2 size={18} />
                        </button>
                    </div>
                </div>
            ))}
        </div>
    );
};
