import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import 'github-markdown-css/github-markdown-light.css';
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Trường Đại học An ninh Nhân dân - People's Security University",
  description: "Trường Đại học An ninh Nhân dân - Cơ sở đào tạo cán bộ an ninh chất lượng cao, đáp ứng yêu cầu bảo vệ an ninh quốc gia trong tình hình mới",
  keywords: "Trường Đại học An ninh Nhân dân, PSU, tuyển sinh, an ninh quốc gia, đào tạo cán bộ",
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon.ico',
    apple: '/favicon.ico',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
