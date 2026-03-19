// Helper functions for Server-Sent Events parsing and handling

import type { ChartData, FileAttachment, SourceReference } from '@/types';

export interface SSEData {
  type: 'metadata' | 'status' | 'sources' | 'attachments' | 'answer_chunk' | 'complete' | 'error' | 'done';
  message?: string;
  content?: string;
  conversation_id?: string;
  sources?: string[];
  source_references?: SourceReference[];
  confidence?: number;
  attachments?: FileAttachment[];
  chart_data?: ChartData[];
  status?: string;
  [key: string]: unknown;
}

export function parseSSELine(line: string): SSEData | null {
  if (!line.startsWith('data: ')) {
    return null;
  }
  
  try {
    const jsonStr = line.slice(6); // Remove "data: " prefix
    if (jsonStr.trim() === '[DONE]') {
      return { type: 'complete' };
    }
    
    return JSON.parse(jsonStr);
  } catch {
    console.warn('Failed to parse SSE line:', line);
    return null;
  }
}

export class SSEParser {
  private buffer = '';
  
  addData(chunk: string): SSEData[] {
    this.buffer += chunk;
    const lines = this.buffer.split('\\n');
    this.buffer = lines.pop() || ''; // Keep the last incomplete line in buffer
    
    const events: SSEData[] = [];
    for (const line of lines) {
      const event = parseSSELine(line);
      if (event) {
        events.push(event);
      }
    }
    
    return events;
  }
  
  flush(): SSEData[] {
    if (this.buffer.trim()) {
      const event = parseSSELine(this.buffer);
      this.buffer = '';
      return event ? [event] : [];
    }
    return [];
  }
}
