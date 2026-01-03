import { FeedbackRequest, FeedbackResponse } from '@/types/feedback';

export async function submitFeedback(request: FeedbackRequest): Promise<FeedbackResponse> {
  // Use Next.js API route instead of calling backend directly
  const url = '/api/feedback';
  const resp = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`Feedback API error: ${resp.status} - ${text}`);
  }

  return resp.json();
}
