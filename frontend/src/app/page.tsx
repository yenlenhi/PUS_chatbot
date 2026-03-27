import Layout from '@/components/Layout';
import Banner from '@/components/Banner';
import QuickStats from '@/components/QuickStats';
import NewsSectionLive from '@/components/NewsSectionLive';
import HistoryTimeline from '@/components/HistoryTimeline';
import MissionVision from '@/components/MissionVision';

export default function Home() {
  return (
    <Layout>
      <Banner />
      <QuickStats />
      <MissionVision />
      <HistoryTimeline />
      <NewsSectionLive />
    </Layout>
  );
}
