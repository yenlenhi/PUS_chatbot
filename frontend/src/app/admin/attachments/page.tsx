'use client';

import React from 'react';
import AdminLayout from '@/components/admin/AdminLayout';
import AttachmentManager from '@/components/admin/AttachmentManager';

export default function AttachmentsPage() {
  return (
    <AdminLayout>
      <AttachmentManager />
    </AdminLayout>
  );
}
