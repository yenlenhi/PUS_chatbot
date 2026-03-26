import { NextResponse } from 'next/server';
import * as cheerio from 'cheerio';

const TUYEN_SINH_URL = 'https://dhannd.bocongan.gov.vn/tuyensinh';
const TUYEN_SINH_PATH_MARKER = '/thong-tin-tuyen-sinh-74/';

type NewsItem = {
  id: number;
  title: string;
  excerpt?: string;
  date: string;
  image?: string;
  category: string;
  source: string;
  url: string;
};

const FALLBACK_DATA = {
  mainNews: [
    {
      id: 1,
      title: 'Thông báo tuyển sinh đào tạo trình độ đại học chính quy tuyển mới năm 2025',
      excerpt: 'Thông tin tuyển sinh được đồng bộ từ Kênh tuyển sinh của Trường Đại học An ninh nhân dân.',
      date: new Date().toLocaleDateString('vi-VN'),
      image: 'https://i.ytimg.com/vi/vYhVOvHbbBE/hqdefault.jpg',
      category: 'TUYỂN SINH',
      source: 'dhannd.bocongan.gov.vn/tuyensinh',
      url: TUYEN_SINH_URL,
    },
  ],
  sidebarNews: [] as NewsItem[],
  lastUpdated: new Date().toISOString(),
};

const browserHeaders = {
  'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
  Accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
};

const normalizeUrl = (value: string | undefined): string => {
  if (!value) return '';
  if (value.startsWith('http')) return value;
  if (value.startsWith('/')) return `https://dhannd.bocongan.gov.vn${value}`;
  return `https://dhannd.bocongan.gov.vn/${value}`;
};

const isTuyenSinhUrl = (value: string): boolean => {
  return value.includes(TUYEN_SINH_PATH_MARKER) || value === TUYEN_SINH_URL;
};

const extractDate = (text: string): string => {
  const match = text.match(/\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b/);
  if (match) {
    return match[0].replace(/-/g, '/');
  }
  return new Date().toLocaleDateString('vi-VN');
};

const buildNewsItem = (
  $: cheerio.CheerioAPI,
  element: Parameters<cheerio.CheerioAPI>[0],
  id: number,
  category: string,
  excerptFromCaption = false
): NewsItem | null => {
  const node = $(element);
  const link = normalizeUrl(node.find('a').first().attr('href'));

  if (!link || !isTuyenSinhUrl(link)) {
    return null;
  }

  const imageNode = node.find('img').first();
  const titleNode = node.find('.caption h4, .caption a, h4 a').first();
  const captionText = node.find('.caption').text().trim().replace(/\s+/g, ' ');
  const title =
    titleNode.text().trim() ||
    imageNode.attr('alt')?.trim() ||
    imageNode.attr('title')?.trim() ||
    '';

  if (!title) {
    return null;
  }

  return {
    id,
    title,
    excerpt: excerptFromCaption ? captionText.replace(title, '').trim() : '',
    date: extractDate(captionText),
    image: normalizeUrl(imageNode.attr('src')),
    category,
    source: 'dhannd.bocongan.gov.vn/tuyensinh',
    url: link,
  };
};

export async function GET() {
  try {
    const response = await fetch(TUYEN_SINH_URL, {
      headers: browserHeaders,
      next: { revalidate: 300 },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch tuyen sinh page: ${response.status}`);
    }

    const html = await response.text();
    const $ = cheerio.load(html);

    const primaryBlock = $('.tuyensinh-news-list-main-home').first();
    const mainNews: NewsItem[] = [];
    const sidebarNews: NewsItem[] = [];

    if (primaryBlock.length > 0) {
      const featuredItem = buildNewsItem(
        $,
        primaryBlock.find('.main-news').first().get(0),
        Date.now(),
        'TUYỂN SINH',
        true
      );

      if (featuredItem) {
        mainNews.push(featuredItem);
      }

      primaryBlock.find('.news-brief').each((index, element) => {
        const item = buildNewsItem(
          $,
          element,
          Date.now() + index + 1,
          'TUYỂN SINH'
        );

        if (!item) {
          return;
        }

        if (mainNews.length < 3) {
          mainNews.push(item);
        } else {
          sidebarNews.push(item);
        }
      });
    }

    if (mainNews.length === 0 && sidebarNews.length === 0) {
      return NextResponse.json({
        success: true,
        data: FALLBACK_DATA,
        message: 'Dữ liệu mẫu tuyển sinh',
      });
    }

    return NextResponse.json({
      success: true,
      data: {
        mainNews,
        sidebarNews,
        lastUpdated: new Date().toISOString(),
      },
      message: 'Tin tuyển sinh cập nhật từ dhannd.bocongan.gov.vn/tuyensinh',
    });
  } catch (error) {
    console.error('Error scraping tuyen sinh news:', error);

    return NextResponse.json({
      success: true,
      data: FALLBACK_DATA,
      message: 'Dữ liệu mẫu tuyển sinh do không thể kết nối tới trang nguồn',
    });
  }
}
