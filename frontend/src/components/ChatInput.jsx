import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '../context/ChatContext';

const ChatInput = () => {
  const [inputValue, setInputValue] = useState('');
  const { sendMessage, loading } = useChat();
  const textareaRef = useRef(null);

  // 处理发送消息
  const handleSendMessage = (e) => {
    e.preventDefault();
    if (inputValue.trim() && !loading) {
      sendMessage(inputValue);
      setInputValue('');
    }
  };

  // 处理按键事件（按Enter发送，Shift+Enter换行）
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  // 自动调整输入框高度
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [inputValue]);

  return (
    <div className="input-container">
      <form onSubmit={handleSendMessage} className="input-box">
        <textarea
          ref={textareaRef}
          className="input-field"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入消息..."
          disabled={loading}
          rows={1}
        />
        <button
          type="submit"
          className="send-button"
          disabled={!inputValue.trim() || loading}
        >
          发送
        </button>
      </form>
    </div>
  );
};

export default ChatInput; 