import { createContext, useContext, useState, useEffect } from 'react';
import * as chatApi from '../api/chatApi';

// 创建聊天上下文
const ChatContext = createContext();

// 自定义钩子，用于方便访问上下文
export const useChat = () => useContext(ChatContext);

// 消息类型定义
export const MESSAGE_TYPES = {
  USER: 'user',
  ASSISTANT: 'assistant',
};

// 从localStorage读取消息
const getLocalMessages = () => {
  try {
    const savedMessages = localStorage.getItem('chat_messages');
    return savedMessages ? JSON.parse(savedMessages) : [];
  } catch (e) {
    console.error("读取本地消息失败:", e);
    return [];
  }
};

// 保存消息到localStorage
const saveLocalMessages = (messages) => {
  try {
    localStorage.setItem('chat_messages', JSON.stringify(messages));
  } catch (e) {
    console.error("保存消息到本地失败:", e);
  }
};

export function ChatProvider({ children }) {
  // 当前对话ID
  const [currentConversationId, setCurrentConversationId] = useState(null);
  // 对话历史列表
  const [conversations, setConversations] = useState([]);
  // 当前对话消息 - 从localStorage初始化
  const [messages, setMessages] = useState(getLocalMessages());
  // 加载状态
  const [loading, setLoading] = useState(false);
  // 错误信息
  const [error, setError] = useState(null);
  // 标记是否是新创建的对话，避免清除现有消息
  const [isNewConversation, setIsNewConversation] = useState(false);

  // 安全地更新消息状态
  const updateMessages = (newMessages) => {
    console.log("更新消息状态:", newMessages);
    // 检查是否是函数式更新
    if (typeof newMessages === 'function') {
      // 获取当前消息状态并应用函数
      const currentMessages = [...messages];
      const updatedMessages = newMessages(currentMessages);
      setMessages(updatedMessages);
      saveLocalMessages(updatedMessages);
    } else {
      setMessages(newMessages);
      saveLocalMessages(newMessages);
    }
  };

  // 加载对话历史
  const fetchConversations = async () => {
    try {
      setLoading(true);
      const data = await chatApi.getConversations();
      setConversations(data);
      setLoading(false);
    } catch (err) {
      setError('无法加载对话历史');
      setLoading(false);
    }
  };

  // 加载指定对话的消息
  const fetchMessages = async (conversationId) => {
    if (!conversationId) return;
    
    // 如果是新创建的对话，不要清空现有消息
    if (isNewConversation) {
      console.log("新创建的对话，保留现有消息");
      setIsNewConversation(false);
      return;
    }
    
    try {
      setLoading(true);
      const data = await chatApi.getConversationMessages(conversationId);
      const fetchedMessages = data.messages || [];
      updateMessages(fetchedMessages);
      setCurrentConversationId(conversationId);
      setLoading(false);
    } catch (err) {
      setError('无法加载对话消息');
      setLoading(false);
    }
  };

  // 发送消息
  const sendMessage = async (content) => {
    if (!content.trim()) return;
    
    console.log("开始发送消息:", content);

    // 添加用户消息到本地状态
    const userMessage = {
      id: Date.now().toString(),
      content,
      role: MESSAGE_TYPES.USER,
    };
    
    const updatedMessages = [...messages, userMessage];
    console.log("添加用户消息后状态:", updatedMessages);
    updateMessages(updatedMessages);
    
    try {
      setLoading(true);
      setError(null);
      
      // 调用API发送消息
      console.log("调用API发送消息...");
      const response = await chatApi.sendMessage(content, currentConversationId);
      console.log("API响应:", response);
      
      // 如果是新对话，更新当前对话ID
      if (!currentConversationId && response.conversation_id) {
        // 标记为新创建的对话，避免清空消息
        setIsNewConversation(true);
        setCurrentConversationId(response.conversation_id);
        // 更新对话列表
        fetchConversations();
      }
      
      // 添加助手回复到本地状态
      const assistantMessage = {
        id: Date.now().toString() + '-response',
        content: response.message || '',
        role: MESSAGE_TYPES.ASSISTANT,
      };
      
      console.log("添加助手回复:", assistantMessage);
      // 确保使用最新的消息状态，只添加助手回复，不重复添加用户消息
      const newMessages = [...messages, assistantMessage];
      console.log("更新后的消息列表:", newMessages);
      updateMessages(newMessages);
      setLoading(false);
    } catch (err) {
      console.error("消息发送失败详情:", err);
      if (err.response) {
        console.error("服务器响应:", err.response.data);
        console.error("状态码:", err.response.status);
      }
      setError('发送消息失败：' + (err.message || '未知错误'));
      setLoading(false);
    }
  };

  // 创建新对话
  const createNewConversation = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await chatApi.createConversation();
      setCurrentConversationId(response.id);
      updateMessages([]);
      
      // 更新对话列表
      fetchConversations();
      
      setLoading(false);
    } catch (err) {
      setError('创建新对话失败');
      setLoading(false);
    }
  };

  // 切换到指定对话
  const switchConversation = (conversationId) => {
    setCurrentConversationId(conversationId);
    fetchMessages(conversationId);
  };

  // 删除对话
  const deleteConversation = async (conversationId) => {
    try {
      await chatApi.deleteConversation(conversationId);
      
      // 如果删除的是当前对话，则清空消息
      if (conversationId === currentConversationId) {
        updateMessages([]);
        setCurrentConversationId(null);
      }
      
      // 更新对话列表
      fetchConversations();
    } catch (err) {
      setError('删除对话失败');
    }
  };

  // 初始加载对话历史
  useEffect(() => {
    fetchConversations();
  }, []);

  // 当前对话ID变更时加载消息
  useEffect(() => {
    if (currentConversationId) {
      fetchMessages(currentConversationId);
    }
  }, [currentConversationId]);

  // 提供的上下文值
  const contextValue = {
    currentConversationId,
    conversations,
    messages,
    loading,
    error,
    sendMessage,
    createNewConversation,
    switchConversation,
    deleteConversation,
    clearError: () => setError(null),
  };

  return (
    <ChatContext.Provider value={contextValue}>
      {children}
    </ChatContext.Provider>
  );
}

export default ChatContext; 