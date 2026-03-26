'use client';

import React from 'react';
import { ExternalLink, PlayCircle, Quote, Sparkles } from 'lucide-react';

const VIDEO_ID = 'vYhVOvHbbBE';
const VIDEO_URL = `https://www.youtube.com/watch?v=${VIDEO_ID}`;
const EMBED_URL = `https://www.youtube-nocookie.com/embed/${VIDEO_ID}?rel=0`;

const SUPPORT_POINTS = [
  'Tra cứu thông tin tuyển sinh chính thức và thống nhất.',
  'Hướng dẫn nhanh về thủ tục, lịch thi và chương trình đào tạo.',
  'Đồng hành cùng học sinh, cán bộ, chiến sĩ và người học có nhu cầu.',
];

const FeaturedVideoSection = () => {
  return (
    <section className="relative overflow-hidden border-t border-slate-200 bg-[radial-gradient(circle_at_top,_rgba(248,113,113,0.18),_transparent_26%),linear-gradient(135deg,_#0b1220_0%,_#132645_48%,_#761d28_100%)] py-16 text-white md:py-20">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-[-4rem] top-16 h-48 w-48 rounded-full bg-red-400/20 blur-3xl md:h-72 md:w-72" />
        <div className="absolute right-[-3rem] top-10 h-44 w-44 rounded-full bg-amber-300/15 blur-3xl md:h-64 md:w-64" />
        <div className="absolute bottom-0 left-1/2 h-56 w-56 -translate-x-1/2 rounded-full bg-sky-400/10 blur-3xl md:h-72 md:w-72" />
      </div>

      <div className="container relative z-10 mx-auto px-4">
        <div className="mx-auto max-w-6xl">
          <div className="mx-auto max-w-4xl text-center">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/8 px-4 py-2 text-xs font-semibold uppercase tracking-[0.28em] text-red-100 backdrop-blur-sm">
              <PlayCircle className="h-4 w-4 text-amber-300" />
              Video giới thiệu
            </div>

            <h2 className="mt-6 text-4xl font-black leading-tight text-white md:text-5xl">
              Khám phá môi trường đào tạo
              <span className="mt-3 block bg-gradient-to-r from-amber-300 via-yellow-200 to-white bg-clip-text text-transparent">
                của Trường Đại học An ninh nhân dân
              </span>
            </h2>

            <p className="mx-auto mt-5 max-w-3xl text-base leading-8 text-slate-200 md:text-lg">
              Video được đặt làm điểm nhấn trung tâm để người xem tiếp cận nhanh hình ảnh, khí chất và định hướng
              tuyển sinh của nhà trường ngay tại trang chủ.
            </p>
          </div>

          <div className="mt-10 overflow-hidden rounded-[32px] border border-white/12 bg-slate-950/55 p-4 shadow-[0_28px_90px_rgba(2,6,23,0.45)] backdrop-blur-sm md:mt-12 md:p-5">
            <div className="mb-4 flex flex-col gap-3 rounded-[24px] border border-white/10 bg-white/5 px-4 py-4 text-sm text-slate-300 md:flex-row md:items-center md:justify-between md:px-5">
              <div className="flex items-center gap-3">
                <div className="rounded-full bg-red-500/15 p-2 text-amber-300">
                  <PlayCircle className="h-4 w-4" />
                </div>
                <div>
                  <p className="font-medium text-white">Phim giới thiệu chính thức</p>
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-400">People&apos;s Security University</p>
                </div>
              </div>

              <a
                href={VIDEO_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex min-h-11 items-center justify-center gap-2 rounded-full bg-white px-5 py-3 font-semibold text-slate-900 transition-all duration-300 hover:-translate-y-0.5 hover:bg-amber-300"
              >
                Xem trên YouTube
                <ExternalLink className="h-4 w-4" />
              </a>
            </div>

            <div className="overflow-hidden rounded-[28px] border border-white/10 bg-black shadow-inner">
              <div className="aspect-[16/9] w-full">
                <iframe
                  src={EMBED_URL}
                  title="Trường Đại học An ninh nhân dân - Nơi ươm mầm sĩ quan an ninh tương lai"
                  className="h-full w-full"
                  loading="lazy"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  referrerPolicy="strict-origin-when-cross-origin"
                  allowFullScreen
                />
              </div>
            </div>
          </div>

          <div className="relative z-20 mx-auto mt-6 max-w-5xl md:-mt-8">
            <div className="overflow-hidden rounded-[30px] border border-white/14 bg-[linear-gradient(140deg,_rgba(255,255,255,0.14),_rgba(255,255,255,0.05))] shadow-[0_24px_80px_rgba(15,23,42,0.35)] backdrop-blur-xl">
              <div className="relative p-6 md:p-8 lg:p-10">
                <div className="absolute left-0 top-0 h-full w-1 bg-gradient-to-b from-amber-300 via-orange-400 to-red-500" />

                <div className="grid gap-8 xl:grid-cols-[minmax(0,1.15fr)_minmax(0,0.85fr)] xl:items-start">
                  <div>
                    <div className="flex items-center gap-3 text-amber-200">
                    <Quote className="h-5 w-5" />
                    <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-200">Thông điệp nổi bật</p>
                    </div>

                    <div className="mt-5 space-y-3">
                      <p className="slogan-line text-2xl font-black leading-tight text-white md:text-3xl">
                        Kênh tuyển sinh chính thức giúp người học tiếp cận thông tin nhanh, rõ và đúng nguồn.
                      </p>
                      <p className="slogan-line slogan-delay-1 max-w-2xl text-base leading-8 text-slate-100 md:text-lg">
                        Tập trung giải đáp thủ tục đăng ký, lịch thi, ngành học, chương trình đào tạo và các mốc
                        thời gian quan trọng ngay trên một điểm chạm duy nhất.
                      </p>
                    </div>

                    <div className="mt-6 inline-flex items-center rounded-full border border-white/12 bg-white/8 px-4 py-2 text-sm text-slate-100">
                      Trọng tâm là hỗ trợ tra cứu tuyển sinh cho thí sinh và người quan tâm đến trường.
                    </div>
                  </div>

                  <div>
                    <div className="inline-flex items-center gap-2 rounded-full bg-amber-300/12 px-3 py-2 text-xs font-semibold uppercase tracking-[0.24em] text-amber-200">
                      <Sparkles className="h-4 w-4" />
                      Vai trò kênh
                    </div>

                    <div className="mt-5 grid gap-4 sm:grid-cols-3 xl:grid-cols-1">
                      {SUPPORT_POINTS.map((item, index) => (
                        <article
                          key={item}
                          className="support-item rounded-2xl border border-white/10 bg-white/6 px-4 py-4 text-sm leading-7 text-slate-100"
                          style={{ animationDelay: `${index * 140}ms` }}
                        >
                          <span className="mb-3 inline-flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-amber-300 to-red-400 text-xs font-bold text-slate-950">
                            {index + 1}
                          </span>
                          <p>{item}</p>
                        </article>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .slogan-line,
        .support-item {
          opacity: 0;
          transform: translateY(18px);
          animation: riseIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        .slogan-delay-1 {
          animation-delay: 0.14s;
        }

        @keyframes riseIn {
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </section>
  );
};

export default FeaturedVideoSection;
