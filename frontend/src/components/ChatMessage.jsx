import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { a11yDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { MESSAGE_TYPES } from '../context/ChatContext';

const ChatMessage = ({ message }) => {
  const isUser = message.role === MESSAGE_TYPES.USER;

  // 对消息内容进行安全处理，确保它是一个字符串
  const safeContent = typeof message.content === 'string' 
    ? message.content 
    : String(message.content || '');

  return (
    <div className={`message-container ${isUser ? 'user-message' : 'bot-message'}`}>
      <div className={`message-bubble ${isUser ? 'user-bubble' : 'bot-bubble'}`}>
        {isUser ? (
          <div>{safeContent}</div>
        ) : (
          <div className="markdown-content">
            <ReactMarkdown
              components={{
                code({ inline, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '');
                  return !inline && match ? (
                    <SyntaxHighlighter
                      style={a11yDark}
                      language={match[1]}
                      PreTag="div"
                      {...props}
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  ) : (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  );
                },
              }}
            >
              {safeContent}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage; 