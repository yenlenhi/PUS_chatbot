import React from 'react';
import { FileText, FileCode, FileImage, FileSpreadsheet, File as FileIconGeneric } from 'lucide-react';

interface FileIconProps {
    fileName: string;
    size?: number;
    className?: string;
}

export const FileIcon: React.FC<FileIconProps> = ({ fileName, size = 24, className = '' }) => {
    const ext = fileName.split('.').pop()?.toLowerCase() || '';

    if (['pdf'].includes(ext)) {
        return (
            <div className={`p-2 bg-red-50 text-red-600 rounded-lg ${className}`}>
                <FileText size={size} />
            </div>
        );
    }

    if (['doc', 'docx'].includes(ext)) {
        return (
            <div className={`p-2 bg-blue-50 text-blue-600 rounded-lg ${className}`}>
                <FileText size={size} />
            </div>
        );
    }

    if (['xls', 'xlsx', 'csv'].includes(ext)) {
        return (
            <div className={`p-2 bg-green-50 text-green-600 rounded-lg ${className}`}>
                <FileSpreadsheet size={size} />
            </div>
        );
    }

    if (['ppt', 'pptx'].includes(ext)) {
        return (
            <div className={`p-2 bg-orange-50 text-orange-600 rounded-lg ${className}`}>
                <FileText size={size} />
            </div>
        );
    }

    if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext)) {
        return (
            <div className={`p-2 bg-purple-50 text-purple-600 rounded-lg ${className}`}>
                <FileImage size={size} />
            </div>
        );
    }

    if (['zip', 'rar', '7z'].includes(ext)) {
        return (
            <div className={`p-2 bg-yellow-50 text-yellow-600 rounded-lg ${className}`}>
                <FileCode size={size} />
            </div>
        );
    }

    return (
        <div className={`p-2 bg-gray-50 text-gray-600 rounded-lg ${className}`}>
            <FileIconGeneric size={size} />
        </div>
    );
};
