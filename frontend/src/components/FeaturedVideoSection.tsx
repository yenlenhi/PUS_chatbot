'use client';

import React from 'react';
import { ExternalLink, PlayCircle, Sparkles } from 'lucide-react';

const VIDEO_ID = 'vYhVOvHbbBE';
const VIDEO_URL = `https://www.youtube.com/watch?v=${VIDEO_ID}`;
const EMBED_URL = `https://www.youtube-nocookie.com/embed/${VIDEO_ID}?rel=0`;

const SLOGAN_LINES = [
  'Kênh thông tin tuyển sinh của Trường Đại học An ninh nhân dân ra đời nhằm tiếp nhận và hỗ trợ tra cứu thông tin chính thức.',
  'Hệ thống hướng dẫn, giải đáp thủ tục đăng ký, lịch thi, thông tin ngành học, chương trình đào tạo và thời gian nhập học.',
  'Đồng thời phục vụ học sinh THPT, cán bộ, chiến sĩ và các cá nhân có nhu cầu, mong muốn học tập tại Trường.',
];

const FeaturedVideoSection = () => {
  return (
    <section className="relative overflow-hidden border-t border-slate-200 bg-[linear-gradient(135deg,_#0f172a_0%,_#12233f_44%,_#7f1d1d_100%)] py-16 text-white">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -left-24 top-12 h-64 w-64 rounded-full bg-red-500/20 blur-3xl" />
        <div className="absolute right-0 top-0 h-80 w-80 rounded-full bg-sky-400/10 blur-3xl" />
        <div className="absolute bottom-0 left-1/3 h-56 w-56 rounded-full bg-amber-300/10 blur-3xl" />
      </div>

      <div className="container relative z-10 mx-auto px-4">
        <div className="grid items-center gap-8 lg:grid-cols-[0.92fr_1.08fr] lg:gap-12">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/8 px-4 py-2 text-xs font-semibold uppercase tracking-[0.28em] text-red-100 backdrop-blur-sm">
              <PlayCircle className="h-4 w-4 text-amber-300" />
              Video giới thiệu
            </div>

            <h2 className="mt-6 text-3xl font-black leading-tight text-white md:text-4xl">
              Trường Đại học An ninh nhân dân
              <span className="mt-2 block bg-gradient-to-r from-amber-300 via-yellow-200 to-white bg-clip-text text-transparent">
                Nơi ươm mầm sĩ quan an ninh tương lai
              </span>
            </h2>

            <div className="mt-6 overflow-hidden rounded-[30px] border border-white/10 bg-white/8 p-5 shadow-[0_18px_60px_rgba(15,23,42,0.24)] backdrop-blur-sm">
              <div className="mb-4 flex items-center gap-3">
                <div className="rounded-2xl bg-amber-300/15 p-2 text-amber-300">
                  <Sparkles className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.28em] text-slate-300">
                    Thông điệp nổi bật
                  </p>
                  <p className="mt-1 text-sm text-slate-200">
                    Kênh tuyển sinh được thiết kế để hướng dẫn nhanh, rõ và đúng nguồn.
                  </p>
                </div>
              </div>

              <div className="space-y-3">
                {SLOGAN_LINES.map((line, index) => (
                  <div
                    key={line}
                    className="slogan-line flex items-start gap-3 rounded-2xl border border-white/8 bg-slate-950/25 px-4 py-3"
                    style={{ animationDelay: `${index * 220}ms` }}
                  >
                    <span className="mt-2 h-2.5 w-2.5 flex-none rounded-full bg-gradient-to-br from-amber-300 to-red-400 shadow-[0_0_14px_rgba(252,211,77,0.65)]" />
                    <p className="leading-7 text-slate-100">{line}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-8">
              <a
                href={VIDEO_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 rounded-full bg-white px-6 py-3 font-semibold text-slate-900 transition-all duration-300 hover:-translate-y-0.5 hover:bg-amber-300"
              >
                Xem trên YouTube
                <ExternalLink className="h-4 w-4" />
              </a>
            </div>
          </div>

          <div className="relative">
            <div className="absolute -inset-3 rounded-[32px] bg-gradient-to-r from-amber-300/20 via-red-400/15 to-sky-300/15 blur-2xl" />
            <div className="relative overflow-hidden rounded-[32px] border border-white/15 bg-slate-950/70 p-3 shadow-[0_24px_80px_rgba(2,6,23,0.45)] backdrop-blur-sm">
              <div className="mb-3 flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-300">
                <span className="font-medium">Phim giới thiệu chính thức</span>
                <span className="rounded-full bg-red-500/15 px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-red-100">
                  PSU
                </span>
              </div>

              <div className="overflow-hidden rounded-[24px] border border-white/10 bg-black shadow-inner">
                <div className="aspect-video">
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
          </div>
        </div>
      </div>

      <style jsx>{`
        .slogan-line {
          opacity: 0;
          transform: translateY(14px);
          animation: sloganReveal 0.75s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        .slogan-line::after {
          content: '';
          position: absolute;
          inset: 0;
          border-radius: 1rem;
          background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.08), transparent);
          transform: translateX(-120%);
          animation: sloganSheen 3.4s ease-in-out infinite;
          animation-delay: 1s;
          pointer-events: none;
        }

        @keyframes sloganReveal {
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes sloganSheen {
          0%,
          75%,
          100% {
            transform: translateX(-120%);
          }

          35% {
            transform: translateX(120%);
          }
        }
      `}</style>
    </section>
  );
};

export default FeaturedVideoSection;
