import React from 'react';

const WelcomeScreen = ({ onSelectSuggestion }) => {
  const suggestions = [
    "如何用React开发一个待办事项应用？",
    "Python中如何处理JSON数据？",
    "解释Docker的基本概念和用法",
    "如何用JavaScript实现防抖和节流函数？",
    "Node.js中如何读写文件？",
    "什么是RESTful API设计原则？"
  ];

  // 添加安全的点击处理函数
  const handleButtonClick = (suggestion) => (e) => {
    e.preventDefault();
    console.log("WelcomeScreen - 点击按钮:", suggestion);
    if (typeof onSelectSuggestion === 'function') {
      try {
        onSelectSuggestion(suggestion);
      } catch (error) {
        console.error("处理建议选择时出错:", error);
      }
    }
  };

  return (
    <div className="welcome-screen">
      <div style={{ maxWidth: '800px', margin: '0 auto', padding: '40px 20px' }}>
        <h1 style={{ fontSize: '2.5rem', fontWeight: '400', textAlign: 'center', color: 'var(--text-primary)', marginBottom: '32px' }}>
          FastAgent 聊天助手
        </h1>
        
        <p style={{ fontSize: '1.1rem', textAlign: 'center', color: 'var(--text-secondary)', marginBottom: '40px' }}>
          一个强大的技术助手，用于回答您的编程和开发问题
        </p>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px', marginBottom: '40px' }}>
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              onClick={handleButtonClick(suggestion)}
              style={{
                padding: '16px',
                background: 'var(--surface-color)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                textAlign: 'left',
                cursor: 'pointer',
                transition: 'background-color 0.2s',
              }}
              onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'var(--hover-color)'}
              onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'var(--surface-color)'}
            >
              {suggestion}
            </button>
          ))}
        </div>
        
        <div style={{ textAlign: 'center', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          <p>FastAgent 是一个基于人工智能的编程助手，能够帮助您解决技术问题和提供代码示例。</p>
          <p>请注意，FastAgent 可能偶尔会提供不完全准确的信息，请确保验证重要代码。</p>
        </div>
      </div>
    </div>
  );
};

export default WelcomeScreen; 