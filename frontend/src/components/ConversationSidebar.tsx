'use client';

import React, { useState } from 'react';
import { PlusCircle, Trash2, MessageSquare } from 'lucide-react';

interface ConversationSummary {
  id: string;
  title: string;
  createdAt: string;
}

interface ConversationSidebarProps {
  conversations: ConversationSummary[];
  currentConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
  onDeleteConversation: (id: string) => void;
}

const ConversationSidebar: React.FC<ConversationSidebarProps> = ({
  conversations,
  currentConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <div className={`bg-gray-100 border-r border-gray-200 transition-all duration-300 ${isCollapsed ? 'w-16' : 'w-64'}`}>
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          {!isCollapsed && <h2 className="text-lg font-semibold">Cuộc hội thoại</h2>}
          <button 
            onClick={onNewConversation}
            className="p-2 rounded-full hover:bg-gray-200 transition-colors"
            title="Tạo cuộc hội thoại mới"
          >
            <PlusCircle size={20} />
          </button>
        </div>
        
        {/* Conversation list */}
        <div className="flex-1 overflow-y-auto">
          {conversations.length === 0 ? (
            <div className="p-4 text-center text-gray-500">
              {!isCollapsed && "Chưa có cuộc hội thoại nào"}
            </div>
          ) : (
            <ul>
              {conversations.map((conv) => (
                <li key={conv.id} className="relative">
                  <button
                    onClick={() => onSelectConversation(conv.id)}
                    className={`w-full text-left p-3 flex items-center gap-3 hover:bg-gray-200 transition-colors ${
                      currentConversationId === conv.id ? 'bg-gray-200' : ''
                    }`}
                  >
                    <MessageSquare size={18} />
                    {!isCollapsed && (
                      <div className="flex-1 overflow-hidden">
                        <div className="truncate">{conv.title}</div>
                        <div className="text-xs text-gray-500">
                          {new Date(conv.createdAt).toLocaleDateString()}
                        </div>
                      </div>
                    )}
                  </button>
                  {!isCollapsed && currentConversationId === conv.id && (
                    <button
                      onClick={() => onDeleteConversation(conv.id)}
                      className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-full hover:bg-gray-300 transition-colors"
                      title="Xóa cuộc hội thoại"
                    >
                      <Trash2 size={16} />
                    </button>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
        
        {/* Collapse button */}
        <div className="p-4 border-t border-gray-200">
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="w-full p-2 text-sm text-center rounded bg-gray-200 hover:bg-gray-300 transition-colors"
          >
            {isCollapsed ? '>' : 'Thu gọn'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConversationSidebar;

