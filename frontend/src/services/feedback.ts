import { FeedbackRequest, FeedbackResponse } from '@/types/feedback';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

export async function submitFeedback(request: FeedbackRequest): Promise<FeedbackResponse> {
  const url = `${API_BASE}/api/v1/feedback`;
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
