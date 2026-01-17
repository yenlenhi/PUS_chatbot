import { NextResponse } from 'next/server';
import * as cheerio from 'cheerio';

// Fallback Mock Data (in case scraping fails)
const FALLBACK_DATA = {
  mainNews: [
    {
      id: 1,
      title: "Hội nghị thông báo quyết định của Ban Thường vụ Đảng ủy Công an Trung ương về công tác cán bộ",
      excerpt: "Ngày 12/12/2024, Trường Đại học An ninh nhân dân tổ chức Hội nghị thông báo quyết định của Ban Thường vụ Đảng ủy Công an Trung ương...",
      date: "12/12/2024",
      image: "https://dhannd.bocongan.gov.vn/image/cache/catalog/Congdoan/260113_z7-505x337.jpg", // Example real image link if possible or keep placeholder
      category: "TIN TỨC",
      source: "dhannd.bocongan.gov.vn",
      url: "https://dhannd.bocongan.gov.vn/"
    }
  ],
  sidebarNews: [],
  lastUpdated: new Date().toISOString()
};

export async function GET() {
  try {
    const url = 'https://dhannd.bocongan.gov.vn/';

    // 1. Fetch HTML
    // Use headers to mimic a browser
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      },
      next: { revalidate: 300 } // Cache for 5 minutes
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch website: ${response.status}`);
    }

    const html = await response.text();
    const $ = cheerio.load(html);

    const mainNews: any[] = [];
    const sidebarNews: any[] = [];

    // Helper to fix relative URLs
    const fixUrl = (link: string | undefined): string => {
      if (!link) return '';
      if (link.startsWith('http')) return link;
      if (link.startsWith('/')) return `https://dhannd.bocongan.gov.vn${link}`;
      return `https://dhannd.bocongan.gov.vn/${link}`;
    };

    // Helper to extract date from link or text if possible, otherwise use current date
    const getDate = () => {
      const today = new Date();
      return `${today.getDate()}/${today.getMonth() + 1}/${today.getFullYear()}`;
    };

    // 2. Extract Main News (Block: .news-list-main-home first instance - usually "Tin tức")
    const mainBlock = $('.news-list-main-home').first();

    if (mainBlock.length > 0) {
      // Big Item
      const bigItem = mainBlock.find('.main-news');
      if (bigItem.length > 0) {
        const linkTag = bigItem.find('a').first();
        const imgTag = bigItem.find('img').first();
        const titleTag = bigItem.find('.caption h4');
        const excerptTag = bigItem.find('.caption p');

        mainNews.push({
          id: Date.now(), // Random ID
          title: titleTag.text().trim() || imgTag.attr('title') || imgTag.attr('alt') || 'Tin tức nổi bật',
          excerpt: excerptTag.text().trim(),
          date: getDate(),
          image: fixUrl(imgTag.attr('src')),
          category: 'NỔI BẬT',
          source: 'dhannd.bocongan.gov.vn',
          url: fixUrl(linkTag.attr('href'))
        });
      }

      // Sub Items (Right sidebar of main block)
      mainBlock.find('.news-list-other-div .news-brief').each((i, el) => {
        const item = $(el);
        const linkTag = item.find('a').first();
        const imgTag = item.find('img').first();

        // Use alt as title if available
        const title = imgTag.attr('alt') || linkTag.text().trim() || 'Tin tức';

        mainNews.push({
          id: Date.now() + i + 1,
          title: title,
          excerpt: '',
          date: getDate(),
          image: fixUrl(imgTag.attr('src')),
          category: 'TIN TỨC',
          source: 'dhannd.bocongan.gov.vn',
          url: fixUrl(linkTag.attr('href'))
        });
      });
    }

    // 3. Extract Sidebar News from other blocks (e.g., "Tuyển sinh", "Đào tạo")
    // We look for other .news-list-main-home blocks
    $('.news-list-main-home').slice(1).each((idx, block) => {
      const $block = $(block);
      const categoryTitle = $block.find('.groupnews-title h5 a').text().trim() || 'TIN KHÁC';

      // Take the main item from this block as a sidebar item
      const bigItem = $block.find('.main-news');
      if (bigItem.length > 0) {
        const linkTag = bigItem.find('a').first();
        const imgTag = bigItem.find('img').first();
        const titleTag = bigItem.find('.caption h4');

        sidebarNews.push({
          id: Date.now() + 100 + idx,
          title: titleTag.text().trim() || imgTag.attr('alt') || categoryTitle,
          date: getDate(), // Fallback date
          category: categoryTitle.toUpperCase(),
          source: 'dhannd.bocongan.gov.vn',
          image: fixUrl(imgTag.attr('src')),
          url: fixUrl(linkTag.attr('href'))
        });
      }

      // Take some sub-items too
      $block.find('.news-list-other-div .news-brief').slice(0, 2).each((i, el) => {
        const item = $(el);
        const linkTag = item.find('a').first();
        const imgTag = item.find('img').first();

        sidebarNews.push({
          id: Date.now() + 200 + idx + i,
          title: imgTag.attr('alt') || linkTag.text().trim(),
          date: getDate(),
          category: categoryTitle.toUpperCase(),
          source: 'dhannd.bocongan.gov.vn',
          url: fixUrl(linkTag.attr('href'))
        });
      });
    });

    // If no news found (parsing error), use fallback
    if (mainNews.length === 0 && sidebarNews.length === 0) {
      console.warn('Scraper found no items, using fallback data');
      return NextResponse.json({
        success: true,
        data: FALLBACK_DATA,
        message: "Dữ liệu mẫu (không lấy được tin thực tế)"
      });
    }

    return NextResponse.json({
      success: true,
      data: {
        mainNews,
        sidebarNews,
        lastUpdated: new Date().toISOString()
      },
      message: "Tin tức cập nhật từ dhannd.bocongan.gov.vn"
    });

  } catch (error) {
    console.error('Error scraping news:', error);
    // Return fallback data on error
    return NextResponse.json({
      success: true,
      data: FALLBACK_DATA,
      message: "Dữ liệu mẫu (Lỗi kết nối đến website trường)"
    });
  }
}
