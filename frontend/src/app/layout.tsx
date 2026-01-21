import type { Metadata } from "next";
import { Inter, Playfair_Display } from "next/font/google"; // Premium fonts import
import 'github-markdown-css/github-markdown-light.css';
import "./globals.css";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin", "vietnamese"], // Ensure Vietnamese support
  display: 'swap',
});

const playfair = Playfair_Display({
  variable: "--font-serif",
  subsets: ["latin", "vietnamese"],
  display: 'swap',
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
        className={`${inter.variable} ${playfair.variable} font-sans antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
