import Layout from '@/components/Layout';
import Banner from '@/components/Banner';
import QuickStats from '@/components/QuickStats';
import FeaturedVideoSection from '@/components/FeaturedVideoSection';
import NewsSectionLive from '@/components/NewsSectionLive';
import HistoryTimeline from '@/components/HistoryTimeline';
import MissionVision from '@/components/MissionVision';

export default function Home() {
  return (
    <Layout>
      <Banner />
      <QuickStats />
      <FeaturedVideoSection />
      <MissionVision />
      <HistoryTimeline />
      <NewsSectionLive />
    </Layout>
  );
}
