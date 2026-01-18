import React from 'react';
import { Eye, Trash2, Download } from 'lucide-react';
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

interface AttachmentTableProps {
    attachments: Attachment[];
    onPreview: (file: Attachment) => void;
    onDelete: (id: number) => void;
}

export const AttachmentTable: React.FC<AttachmentTableProps> = ({ attachments, onPreview, onDelete }) => {
    return (
        <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
            <table className="w-full text-left text-sm text-gray-500">
                <thead className="bg-gray-50 text-xs uppercase text-gray-700">
                    <tr>
                        <th className="px-6 py-3 font-medium">Tên tài liệu</th>
                        <th className="px-6 py-3 font-medium">Danh mục</th>
                        <th className="px-6 py-3 font-medium">Kích thước</th>
                        <th className="px-6 py-3 font-medium">Ngày tạo</th>
                        <th className="px-6 py-3 font-medium text-right">Hành động</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                    {attachments.map((file) => (
                        <tr key={file.id} className="hover:bg-gray-50/50 transition-colors group">
                            <td className="px-6 py-4">
                                <div className="flex items-center gap-3">
                                    <FileIcon fileName={file.file_name} size={20} className="shrink-0" />
                                    <div className="font-medium text-gray-900 truncate max-w-[300px]" title={file.file_name}>
                                        {file.file_name}
                                    </div>
                                </div>
                            </td>
                            <td className="px-6 py-4">
                                <span className="inline-flex items-center rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700">
                                    {file.category || 'Khác'}
                                </span>
                            </td>
                            <td className="px-6 py-4">
                                {(file.file_size ? file.file_size / 1024 : 0).toFixed(1)} KB
                            </td>
                            <td className="px-6 py-4">
                                {file.created_at ? new Date(file.created_at).toLocaleDateString('vi-VN') : 'N/A'}
                            </td>
                            <td className="px-6 py-4 text-right">
                                <div className="flex justify-end gap-2">
                                    <button
                                        onClick={() => onPreview(file)}
                                        className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 hover:text-blue-600 transition-colors"
                                        title="Xem trước"
                                    >
                                        <Eye size={18} />
                                    </button>
                                    <button
                                        onClick={() => onDelete(file.id)}
                                        className="rounded-lg p-2 text-gray-500 hover:bg-red-50 hover:text-red-600 transition-colors"
                                        title="Xóa"
                                    >
                                        <Trash2 size={18} />
                                    </button>
                                </div>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};
