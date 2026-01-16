// Helper functions for Server-Sent Events parsing and handling

export interface SSEData {
  type: 'metadata' | 'status' | 'sources' | 'answer_chunk' | 'complete' | 'error';
  message?: string;
  content?: string;
  conversation_id?: string;
  sources?: any[];
  source_references?: any[];
  confidence?: number;
  attachments?: any[];
  chart_data?: any[];
  status?: string;
  [key: string]: any;
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
  } catch (error) {
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