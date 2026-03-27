import React from 'react';
import Link from 'next/link';
import Layout from '@/components/Layout';
import { Construction, Home } from 'lucide-react';

export default function NghienCuuPage() {
  return (
    <Layout>
      <section className="relative min-h-[calc(100vh-12rem)] overflow-hidden border-b border-slate-200/80 bg-gradient-to-br from-slate-50 via-white to-red-50/40">
        <div
          className="pointer-events-none absolute inset-0 opacity-[0.35]"
          aria-hidden
        >
          <div className="absolute -left-24 top-24 h-72 w-72 rounded-full bg-red-600/20 blur-3xl" />
          <div className="absolute -right-16 bottom-32 h-80 w-80 rounded-full bg-[#1E3A5F]/15 blur-3xl" />
        </div>

        <div className="container relative z-10 mx-auto flex min-h-[calc(100vh-12rem)] flex-col items-center justify-center px-4 py-16 md:py-24">
          <div className="w-full max-w-xl">
            <div className="rounded-3xl border border-slate-200/90 bg-white/90 p-8 shadow-[0_24px_60px_-12px_rgba(15,23,42,0.12)] backdrop-blur-md md:p-10">
              <div className="mx-auto mb-6 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-red-700 to-[#1E3A5F] text-white shadow-lg shadow-red-900/25">
                <Construction className="h-7 w-7" aria-hidden />
              </div>

              <p className="text-center text-xs font-semibold uppercase tracking-[0.2em] text-red-800/80">
                Nghiên cứu
              </p>
              <h1 className="mt-2 text-center text-2xl font-black tracking-tight text-slate-900 md:text-3xl">
                Trang đang được hoàn thiện
              </h1>

              <p className="mt-6 text-center text-base leading-relaxed text-slate-600 md:text-lg">
                Trang thông tin này của nhà trường hiện đang được xây dựng và hoàn
                thiện. Nội dung sẽ được triển khai trong thời gian sớm nhất.
                Kính mong quý thầy/cô và các bạn theo dõi, cập nhật trong thời
                gian tới.
              </p>

              <div className="mt-8 flex flex-col items-stretch gap-3 sm:flex-row sm:justify-center">
                <Link
                  href="/"
                  className="inline-flex items-center justify-center gap-2 rounded-full bg-gradient-to-r from-red-700 to-red-800 px-6 py-3 text-sm font-bold text-white shadow-md transition hover:from-red-800 hover:to-red-900 hover:shadow-lg"
                >
                  <Home className="h-4 w-4" aria-hidden />
                  Về trang chủ
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </Layout>
  );
}
