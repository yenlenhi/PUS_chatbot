import Layout from '@/components/Layout';
import Banner from '@/components/Banner';
import NewsSection from '@/components/NewsSection';
import QuickStats from '@/components/QuickStats';

export default function Home() {
  return (
    <Layout>
      <Banner />
      <QuickStats />
      <NewsSection />
    </Layout>
  );
}
