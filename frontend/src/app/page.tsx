import Layout from '@/components/Layout';
import Banner from '@/components/Banner';
import NewsSectionLive from '@/components/NewsSectionLive';
import QuickStats from '@/components/QuickStats';

export default function Home() {
  return (
    <Layout>
      <Banner />
      <QuickStats />
      <NewsSectionLive />
    </Layout>
  );
}
