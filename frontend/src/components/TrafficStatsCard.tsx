'use client';

import React, { useEffect, useState } from 'react';
import { Activity, BarChart3, CalendarDays, Globe2 } from 'lucide-react';
import type { PublicTrafficSummary } from '@/types/analytics';

const numberFormatter = new Intl.NumberFormat('vi-VN');

const DEFAULT_SUMMARY: PublicTrafficSummary = {
  online_now: 0,
  today_views: 0,
  month_views: 0,
  total_views: 0,
  last_updated_at: new Date(0).toISOString(),
  data_source: 'fallback',
};

const TRAFFIC_ITEMS = [
  {
    key: 'online_now',
    label: 'Đang online',
    icon: Activity,
    accent: 'from-[#5f63d7] via-[#7a6ff0] to-[#8a8cf7]',
    pill: 'from-[#f3f1ff] to-[#ececff]',
  },
  {
    key: 'today_views',
    label: 'Hôm nay',
    icon: CalendarDays,
    accent: 'from-[#ff70b8] via-[#ff8cc3] to-[#ff9ad0]',
    pill: 'from-[#fff0f7] to-[#ffe6f3]',
  },
  {
    key: 'month_views',
    label: 'Trong tháng',
    icon: BarChart3,
    accent: 'from-[#1aa1ff] via-[#33b3ff] to-[#5fc7ff]',
    pill: 'from-[#edf9ff] to-[#e0f3ff]',
  },
  {
    key: 'total_views',
    label: 'Tổng pageview',
    icon: Globe2,
    accent: 'from-[#6d68d9] via-[#8a7bff] to-[#9d8fff]',
    pill: 'from-[#f1efff] to-[#ece8ff]',
  },
] as const;

const TrafficStatsCard = () => {
  const [summary, setSummary] = useState<PublicTrafficSummary>(DEFAULT_SUMMARY);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    const loadSummary = async () => {
      try {
        const response = await fetch('/api/analytics/traffic-summary', {
          cache: 'no-store',
        });

        if (!response.ok) {
          throw new Error(`Unable to fetch traffic summary: ${response.status}`);
        }

        const data: PublicTrafficSummary = await response.json();
        if (mounted) {
          setSummary(data);
        }
      } catch (error) {
        console.error('Traffic summary fetch failed:', error);
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    loadSummary();
    const intervalId = window.setInterval(loadSummary, 60000);

    return () => {
      mounted = false;
      window.clearInterval(intervalId);
    };
  }, []);

  const lastUpdated =
    summary.last_updated_at && summary.last_updated_at !== DEFAULT_SUMMARY.last_updated_at
      ? new Date(summary.last_updated_at).toLocaleTimeString('vi-VN', {
          hour: '2-digit',
          minute: '2-digit',
          timeZone: 'Asia/Ho_Chi_Minh',
        })
      : '--:--';

  return (
    <aside className="relative overflow-hidden rounded-[28px] border border-white/80 bg-white/90 p-5 shadow-[0_24px_70px_rgba(112,99,255,0.12)] backdrop-blur-sm">
      <div className="absolute inset-x-5 top-0 h-1 rounded-full bg-gradient-to-r from-[#5b63d5] via-[#6f8bff] to-[#f38be5]" />
      <div className="absolute -right-12 -top-12 h-32 w-32 rounded-full bg-[#eef3ff] blur-2xl" />
      <div className="absolute -bottom-14 -left-10 h-28 w-28 rounded-full bg-[#fff0f7] blur-2xl" />

      <div className="relative">
        <div className="mb-5 flex items-start justify-between gap-4">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-slate-400">
              Hệ thống
            </p>
            <h3 className="mt-2 text-[26px] font-semibold tracking-tight text-slate-800">
              Thống kê truy cập
            </h3>
          </div>
          <div className="rounded-full bg-gradient-to-br from-[#f2f5ff] to-[#fff0f8] p-3 text-slate-600 shadow-inner">
            <BarChart3 className="h-5 w-5" />
          </div>
        </div>

        <div className="space-y-3">
          {TRAFFIC_ITEMS.map((item) => {
            const Icon = item.icon;
            const value = summary[item.key];

            return (
              <div
                key={item.key}
                className={`relative flex items-center justify-between gap-3 rounded-full border border-white/90 bg-gradient-to-r ${item.pill} px-4 py-3 shadow-[inset_0_1px_0_rgba(255,255,255,0.95),0_10px_30px_rgba(148,163,184,0.08)]`}
              >
                <div className="flex min-w-0 items-center gap-3">
                  <span className={`h-8 w-8 flex-none rounded-full bg-gradient-to-br ${item.accent} p-[1px] shadow-sm`}>
                    <span className="flex h-full w-full items-center justify-center rounded-full bg-white/90">
                      <Icon className="h-4 w-4 text-slate-700" />
                    </span>
                  </span>
                  <span className="truncate text-sm font-medium text-slate-700">
                    {item.label}:
                  </span>
                </div>

                <span className={`text-right text-lg font-bold tracking-tight bg-gradient-to-r ${item.accent} bg-clip-text text-transparent`}>
                  {loading ? '...' : numberFormatter.format(value)}
                </span>
              </div>
            );
          })}
        </div>

        <div className="mt-4 flex items-center justify-between gap-3 text-xs text-slate-500">
          <span>Cập nhật lúc {lastUpdated}</span>
          <span className="rounded-full bg-slate-100 px-2.5 py-1 font-medium text-slate-600">
            {summary.data_source === 'access_logs' ? 'Live logs' : 'System data'}
          </span>
        </div>
      </div>
    </aside>
  );
};

export default TrafficStatsCard;
