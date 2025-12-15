'use client';

import React from 'react';
import { LanguageProvider } from '@/i18n/LanguageContext';

export default function AdminRootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <LanguageProvider>
      {children}
    </LanguageProvider>
  );
}
