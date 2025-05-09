import React from 'react';
import { useChat } from '../context/ChatContext';

const Sidebar = ({ isOpen, toggleSidebar }) => {
  const { 
    conversations, 
    currentConversationId, 
    switchConversation, 
    createNewConversation,
    deleteConversation
  } = useChat();

  // 格式化日期
  const formatDate = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleDateString('zh-CN', { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  // 提取对话标题（取第一条消息的前20个字符）
  const getConversationTitle = (conv) => {
    if (conv.title) return conv.title;
    if (conv.messages && conv.messages.length > 0) {
      return conv.messages[0].content.substring(0, 20) + '...';
    }
    return '新对话';
  };

  return (
    <div className={`sidebar ${!isOpen ? 'sidebar-collapsed' : ''}`}>
      <div className="sidebar-header">
        <button className="menu-button" onClick={toggleSidebar}>
          ≡
        </button>
        {isOpen && <div className="sidebar-title">聊天助手</div>}
      </div>

      {isOpen && (
        <>
          <button className="new-chat-button" onClick={createNewConversation}>
            + 新建对话
          </button>

          <div className="chat-history">
            {conversations.length === 0 ? (
              <div style={{ padding: '16px', textAlign: 'center', color: 'var(--text-secondary)' }}>
                没有历史对话
              </div>
            ) : (
              conversations.map((conv) => (
                <div 
                  key={conv.id} 
                  className={`history-item ${currentConversationId === conv.id ? 'active' : ''}`}
                  onClick={() => switchConversation(conv.id)}
                >
                  <div style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {getConversationTitle(conv)}
                    {conv.created_at && (
                      <div style={{ fontSize: '12px', opacity: 0.7 }}>
                        {formatDate(conv.created_at)}
                      </div>
                    )}
                  </div>
                  <button 
                    className="menu-button"
                    style={{ marginLeft: '8px' }}
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteConversation(conv.id);
                    }}
                  >
                    ×
                  </button>
                </div>
              ))
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default Sidebar; 