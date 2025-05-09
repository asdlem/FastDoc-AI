import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '../context/ChatContext';
import Sidebar from '../components/Sidebar';
import ChatMessage from '../components/ChatMessage';
import ChatInput from '../components/ChatInput';
import LoadingIndicator from '../components/LoadingIndicator';
import ErrorMessage from '../components/ErrorMessage';
import WelcomeScreen from '../components/WelcomeScreen';

const ChatPage = () => {
  const { messages, loading, error, clearError, sendMessage } = useChat();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef(null);
  // 添加一个状态来跟踪用户是否已开始对话
  const [hasStartedChat, setHasStartedChat] = useState(false);
  // 添加调试状态
  const [debugInfo, setDebugInfo] = useState(null);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 检查localStorage中是否有保存的消息
  useEffect(() => {
    try {
      const savedMessages = localStorage.getItem('chat_messages');
      if (savedMessages && JSON.parse(savedMessages).length > 0) {
        setHasStartedChat(true);
        console.log("从本地存储加载了消息:", JSON.parse(savedMessages).length);
      }
    } catch (e) {
      console.error("读取本地消息状态失败:", e);
    }
  }, []);

  // 当消息变化时，更新对话状态
  useEffect(() => {
    console.log("消息状态更新，当前消息数:", messages.length);
    setDebugInfo({
      messageCount: messages.length,
      messageIds: messages.map(m => m.id),
      timestamp: new Date().toISOString()
    });
    
    if (messages.length > 0) {
      setHasStartedChat(true);
    }
  }, [messages]);

  // 处理建议选择
  const handleSuggestionSelect = (suggestion) => {
    console.log("点击预设问题:", suggestion);
    // 标记已开始对话
    setHasStartedChat(true);
    // 延迟处理，确保UI状态更新
    setTimeout(() => {
      sendMessage(suggestion);
    }, 50);
  };

  // 切换侧边栏
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className="app-container">
      <Sidebar isOpen={sidebarOpen} toggleSidebar={toggleSidebar} />
      
      <div className="main-content">
        <div className="chat-container">
          {!hasStartedChat ? (
            <WelcomeScreen onSelectSuggestion={handleSuggestionSelect} />
          ) : (
            <>
              {debugInfo && (
                <div style={{ 
                  padding: '5px 10px', 
                  fontSize: '12px', 
                  background: '#f0f0f0', 
                  margin: '5px', 
                  borderRadius: '4px',
                  display: 'none' // 正式环境隐藏
                }}>
                  消息数: {debugInfo.messageCount} | 
                  时间: {debugInfo.timestamp}
                </div>
              )}
              {messages.length > 0 ? (
                messages.map((message, index) => (
                  <ChatMessage key={message.id || index} message={message} />
                ))
              ) : (
                <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text-secondary)' }}>
                  开始新的对话...
                </div>
              )}
              {loading && <LoadingIndicator />}
              {error && (
                <ErrorMessage message={error} onDismiss={clearError} />
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
        
        <ChatInput />
      </div>
    </div>
  );
};

export default ChatPage; 