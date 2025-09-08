import Layout from '@/components/Layout';
import ChatInterface from '@/components/ChatInterface';

export default function ChatsPage() {
  return (
    <Layout>
      <div className="container mx-auto px-4 py-8 flex flex-col items-center">
        <h1 className="text-4xl font-bold text-center text-blue-900 mb-8">Trợ lý Tuyển sinh AI</h1>
        <div className="w-full max-w-4xl h-[70vh] min-h-[500px]">
          <ChatInterface />
        </div>
      </div>
    </Layout>
  );
}
