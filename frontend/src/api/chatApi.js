import axios from 'axios';

// 创建Axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 发送聊天消息
export const sendMessage = async (message, conversationId = null) => {
  try {
    console.log("发送请求到后端:", message);
    const response = await api.post('/query', { 
      query: message
    });
    
    console.log("接收到后端响应:", response.data);
    
    // 根据实际响应格式调整返回值
    let messageContent = '';
    if (typeof response.data === 'string') {
      messageContent = response.data;
    } else if (typeof response.data === 'object') {
      // 尝试解析常见的响应格式
      messageContent = response.data.message || response.data.content || response.data.answer || JSON.stringify(response.data);
    } else {
      messageContent = String(response.data);
    }
    
    return {
      message: messageContent,
      conversation_id: conversationId || 'new-conversation'
    };
  } catch (error) {
    console.error('发送消息错误:', error);
    console.error('详细错误信息:', error.response ? error.response.data : error.message);
    throw error;
  }
};

// 获取对话历史 (模拟，因为后端API可能不支持)
export const getConversations = async () => {

    // 模拟API响应
    return [];
 
};

// 获取特定对话的消息 (模拟，因为后端API可能不支持)
export const getConversationMessages = async (conversationId) => {
  try {
    // 使用conversationId参数(虽然是模拟的)
    console.log('获取对话ID:', conversationId);
    // 模拟API响应
    return { messages: [] };
  } catch (error) {
    console.error('获取对话消息错误:', error);
    throw error;
  }
};

// 创建新对话 (模拟，因为后端API可能不支持)
export const createConversation = async () => {
  try {
    // 模拟API响应
    return { id: 'new-conversation-' + Date.now() };
  } catch (error) {
    console.error('创建对话错误:', error);
    throw error;
  }
};

// 删除对话 (模拟，因为后端API可能不支持)
export const deleteConversation = async (conversationId) => {
  try {
    // 使用conversationId参数(虽然是模拟的)
    console.log('删除对话ID:', conversationId);
    // 模拟API响应
    return { success: true };
  } catch (error) {
    console.error('删除对话错误:', error);
    throw error;
  }
};

export default {
  sendMessage,
  getConversations,
  getConversationMessages,
  createConversation,
  deleteConversation,
}; 