'use client';

import React, { useState, useEffect, useRef } from 'react';
import ConversationSidebar from './ConversationSidebar';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import { Message, Conversation } from '@/types';
import { generateUniqueId } from '@/utils/helpers';
import { chatAPI } from '../services/api';

const DEBUG = process.env.NODE_ENV !== 'production';

const debugLog = (...args: any[]) => {
  if (DEBUG) {
    console.log(...args);
  }
};

const ChatInterface: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const streamingMessageRef = useRef<string>('');

  // Initialize on first load
  useEffect(() => {
    const savedConversations = localStorage.getItem('conversations');
    if (savedConversations) {
      try {
        const parsed = JSON.parse(savedConversations);
        setConversations(parsed);
        
        // Set current conversation to the most recent one
        if (parsed.length > 0) {
          setCurrentConversationId(parsed[0].id);
        }
      } catch (e) {
        console.error('Failed to parse saved conversations', e);
      }
    } else {
      // Create a new conversation if none exist
      createNewConversation();
    }
  }, []);

  // Save conversations to localStorage whenever they change
  useEffect(() => {
    if (conversations.length > 0) {
      localStorage.setItem('conversations', JSON.stringify(conversations));
    }
  }, [conversations]);

  const createNewConversation = () => {
    const newId = generateUniqueId();
    const newConversation: Conversation = {
      id: newId,
      title: 'Cuộc hội thoại mới',
      messages: [],
      createdAt: new Date().toISOString(),
    };
    
    setConversations([newConversation, ...conversations]);
    setCurrentConversationId(newId);
    return newId;
  };

  const deleteConversation = (id: string) => {
    const updatedConversations = conversations.filter(conv => conv.id !== id);
    setConversations(updatedConversations);
    
    if (currentConversationId === id) {
      if (updatedConversations.length > 0) {
        setCurrentConversationId(updatedConversations[0].id);
      } else {
        createNewConversation();
      }
    }
    
    if (updatedConversations.length === 0) {
      localStorage.removeItem('conversations');
    }
  };

  const updateConversationTitle = (id: string, title: string) => {
    setConversations(conversations.map(conv => 
      conv.id === id ? { ...conv, title } : conv
    ));
  };

  const getCurrentConversation = () => {
    return conversations.find(conv => conv.id === currentConversationId) || null;
  };

  const getConversationSummaries = () => {
    return conversations.map(({ id, title, createdAt }) => ({ id, title, createdAt }));
  };

  const sendMessage = async (content: string) => {
    if (!content.trim()) return;
    
    debugLog('Sending message:', content);
    
    let conversationId = currentConversationId;
    
    // If no current conversation, create a new one
    if (!conversationId) {
      conversationId = createNewConversation();
    }
    
    // Add user message
    const userMessage: Message = {
      id: generateUniqueId(),
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };
    
    // Update conversation with user message
    const updatedConversations = conversations.map(conv => {
      if (conv.id === conversationId) {
        return {
          ...conv,
          messages: [...conv.messages, userMessage],
        };
      }
      return conv;
    });
    
    setConversations(updatedConversations);
    setIsLoading(true);
    setError(null);
    
    // Tạo placeholder message cho bot
    const botMessageId = generateUniqueId();
    const botMessage: Message = {
      id: botMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
      isStreaming: true, // Đánh dấu đang streaming
    };
    
    // Thêm placeholder message vào conversation
    setConversations(prevConversations => 
      prevConversations.map(conv => {
        if (conv.id === conversationId) {
          return {
            ...conv,
            messages: [...conv.messages, botMessage],
          };
        }
        return conv;
      })
    );
    
    try {
      // Get conversation history for context
      const currentConv = updatedConversations.find(c => c.id === conversationId);
      const conversationHistory = currentConv ? currentConv.messages : [];
      
      // Bắt đầu streaming
      setIsStreaming(true);
      streamingMessageRef.current = '';
      
      // Gọi API với streaming
      console.log('Starting streaming request');
      const fullResponse = await chatAPI.sendMessageStream(
        {
          message: content,
          conversation_history: conversationHistory.map(msg => ({
            role: msg.role,
            content: msg.content,
          })),
        },
        (chunk) => {
          console.log('Received chunk:', chunk);
          // Cập nhật nội dung message khi nhận được chunk mới
          if (chunk) {
            streamingMessageRef.current += chunk;
            
            // Cập nhật message trong state
            setConversations(prevConversations => 
              prevConversations.map(conv => {
                if (conv.id === conversationId) {
                  return {
                    ...conv,
                    messages: conv.messages.map(msg => {
                      if (msg.id === botMessageId) {
                        return {
                          ...msg,
                          content: streamingMessageRef.current,
                        };
                      }
                      return msg;
                    }),
                  };
                }
                return conv;
              })
            );
          }
        }
      );
      
      console.log("Full response received:", fullResponse);
      
      // Khi streaming hoàn tất, cập nhật message cuối cùng
      setConversations(prevConversations => 
        prevConversations.map(conv => {
          if (conv.id === conversationId) {
            return {
              ...conv,
              messages: conv.messages.map(msg => {
                if (msg.id === botMessageId) {
                  return {
                    ...msg,
                    content: fullResponse.answer || streamingMessageRef.current || "Không nhận được câu trả lời",
                    sources: fullResponse.sources ? fullResponse.sources.map(source => ({ title: source })) : [],
                    confidence: fullResponse.confidence || 0,
                    isStreaming: false,
                  };
                }
                return msg;
              }),
            };
          }
          return conv;
        })
      );
    } catch (err) {
      console.error('Error sending message:', err);
      setError(err instanceof Error ? err.message : 'Đã xảy ra lỗi khi gửi tin nhắn');
      
      // Cập nhật message với lỗi
      setConversations(prevConversations => 
        prevConversations.map(conv => {
          if (conv.id === conversationId) {
            return {
              ...conv,
              messages: conv.messages.map(msg => {
                if (msg.id === botMessageId) {
                  return {
                    ...msg,
                    content: 'Đã xảy ra lỗi khi nhận câu trả lời.',
                    isStreaming: false,
                    error: true,
                  };
                }
                return msg;
              }),
            };
          }
          return conv;
        })
      );
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <ConversationSidebar
        conversations={getConversationSummaries()}
        currentConversationId={currentConversationId}
        onSelectConversation={setCurrentConversationId}
        onNewConversation={createNewConversation}
        onDeleteConversation={deleteConversation}
      />
      
      {/* Main chat area */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Message list */}
        <MessageList
          messages={getCurrentConversation()?.messages || []}
          isLoading={isLoading}
          error={error}
        />
        
        {/* Chat input */}
        <ChatInput 
          onSendMessage={sendMessage}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
};

export default ChatInterface;







