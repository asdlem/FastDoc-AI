"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  RefreshCw,
  ThumbsUp,
  ThumbsDown,
  Copy,
  Send,
  Paperclip,
  LogOut,
  Menu,
  X,
  MessageSquare,
  User,
  Settings,
  Trash2,
  Eraser,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { useMobile } from "@/hooks/use-mobile"
import { useAuth } from "@/lib/auth-context"
import { createMessage, createSession, deleteSession, getSessions, getSessionDetail, sendQuery, deleteMessage, clearSessionMessages } from "@/lib/api"
import { CustomToast } from "@/components/ui/custom-toast"
import { ConfirmDialog } from "@/components/ui/confirm-dialog"
import { MarkdownRenderer } from '@/components/ui/markdown-renderer'

// 格式化日期函数
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    month: 'numeric',
    day: 'numeric'
  })
}

// 检查日期是否为今天
const isToday = (dateString: string) => {
  const date = new Date(dateString)
  const today = new Date()
  return date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()
}

// 检查日期是否为本周
const isThisWeek = (dateString: string) => {
  const date = new Date(dateString)
  const today = new Date()
  const firstDayOfWeek = new Date(today.setDate(today.getDate() - today.getDay()))
  firstDayOfWeek.setHours(0, 0, 0, 0)
  const lastDayOfWeek = new Date(firstDayOfWeek)
  lastDayOfWeek.setDate(lastDayOfWeek.getDate() + 6)
  lastDayOfWeek.setHours(23, 59, 59, 999)
  
  return date >= firstDayOfWeek && date <= lastDayOfWeek
}

// 检查日期是否为本月
const isThisMonth = (dateString: string) => {
  const date = new Date(dateString)
  const today = new Date()
  return date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()
}

// 获取会话分类
const getSessionCategory = (dateString: string) => {
  if (isToday(dateString)) return "today"
  if (isThisWeek(dateString)) return "week"
  if (isThisMonth(dateString)) return "month"
  return "earlier"
}

// 会话类型
type Session = {
  id: number
  title: string
  created_at: string
  updated_at: string
  message_count?: number
  category?: string
}

// 消息类型
type Message = {
  id: number
  role: "user" | "assistant"
  content: string
  created_at: string
  session_id: number
}

// 格式化时间函数
const formatTime = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

export default function ChatPage() {
  const router = useRouter()
  const { user, logout, isAuthenticated, loading: authLoading, checkAuth } = useAuth()
  const isMobile = useMobile()
  const [sidebarOpen, setSidebarOpen] = useState(!isMobile)
  const [input, setInput] = useState("")
  const [messages, setMessages] = useState<Message[]>([])
  const [sessions, setSessions] = useState<Session[]>([])
  const [activeSession, setActiveSession] = useState<number | null>(null)
  const [isTyping, setIsTyping] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [toast, setToast] = useState({ 
    visible: false, 
    message: "", 
    variant: "default" as "default" | "success" | "error" 
  })
  const [confirmDialog, setConfirmDialog] = useState({
    isOpen: false,
    sessionId: 0,
    messageId: 0,
    action: "" as "deleteSession" | "clearSession" | "deleteMessage",
    title: "",
    message: ""
  })
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const authChecked = useRef(false)

  // 检查是否已登录
  useEffect(() => {
    const verifyAuth = async () => {
      if (authChecked.current) return;
      
      console.log('Verifying auth in chat page');
      const isAuthed = await checkAuth();
      authChecked.current = true;
      
      if (!isAuthed) {
        console.log('Not authenticated, redirecting to login');
        router.push("/login");
      } else {
        console.log('Authentication verified, loading sessions');
        loadSessionsList();
      }
    };
    
    if (!authLoading) {
      verifyAuth();
    }
  }, [authLoading, checkAuth, router]);
  
  // 加载会话列表的函数
  const loadSessionsList = async () => {
    try {
      console.log('Loading sessions list');
      setLoading(true);
      const sessionsList = await getSessions();
      console.log(`Loaded ${sessionsList.length} sessions`);
      
      // 为每个会话添加category属性
      const sessionsWithCategory = sessionsList.map((session: Session) => ({
        ...session,
        category: getSessionCategory(session.updated_at || session.created_at)
      }));
      
      setSessions(sessionsWithCategory);
      
      // 如果有会话，选择第一个作为活动会话
      if (sessionsWithCategory.length > 0) {
        console.log(`Loading first session: ${sessionsWithCategory[0].id}`);
        await loadSessionMessages(sessionsWithCategory[0].id);
      } else {
        console.log('No sessions found');
        setLoading(false);
      }
    } catch (error) {
      console.error("加载会话失败", error);
      setError("加载会话失败");
      setLoading(false);
      
      // 检查是否是认证错误
      if (error instanceof Error && error.message.includes('登录')) {
        console.log('Auth error while loading sessions, rechecking auth');
        const isAuthed = await checkAuth();
        if (!isAuthed) {
          router.push("/login");
        }
      }
    }
  };

  // 加载会话消息
  const loadSessionMessages = async (sessionId: number) => {
    try {
      console.log(`Loading messages for session ${sessionId}`);
      setLoading(true);
      setError(""); // 清除之前的错误
      const sessionData = await getSessionDetail(sessionId);
      console.log(`Loaded ${sessionData.messages?.length || 0} messages`);
      setMessages(sessionData.messages || []);
      setActiveSession(sessionId);
    } catch (error) {
      console.error("加载消息失败", error);
      setError("加载消息失败");
      
      // 检查是否是认证错误
      if (error instanceof Error && error.message.includes('登录')) {
        console.log('Auth error while loading messages, rechecking auth');
        const isAuthed = await checkAuth();
        if (!isAuthed) {
          router.push("/login");
        }
      }
    } finally {
      setLoading(false);
    }
  }

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // 响应式处理
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) {
        setSidebarOpen(false)
      } else {
        setSidebarOpen(true)
      }
    }

    window.addEventListener("resize", handleResize)
    return () => window.removeEventListener("resize", handleResize)
  }, [])

  // 发送消息
  const handleSendMessage = async () => {
    if (!input.trim() || !activeSession) return

    const messageText = input.trim()
    setInput("")

    try {
      // 先添加用户消息到UI
      const tempUserMessage: Message = {
        id: Date.now(),
        role: "user",
        content: messageText,
        created_at: new Date().toISOString(),
        session_id: activeSession
      }
      
      setMessages(prev => [...prev, tempUserMessage])
      
      // 发送用户消息到后端
      await createMessage(activeSession, "user", messageText)
      
      // 显示AI正在输入
    setIsTyping(true)
      
      // 发送查询获取AI回复
      const queryResult = await sendQuery(messageText, activeSession)
      
      // 添加AI回复到UI
      const assistantMessage: Message = {
        id: Date.now() + 1,
        role: "assistant",
        content: queryResult.answer || queryResult.result || queryResult.response || queryResult,
        created_at: new Date().toISOString(),
        session_id: activeSession
      }
      
      setMessages(prev => [...prev, assistantMessage])
      setIsTyping(false)
      
      // 刷新会话列表以更新最新的会话标题
      refreshSessions()
    } catch (error) {
      console.error("发送消息失败", error)
      setError("发送消息失败")
      setIsTyping(false)
    }
  }

  // 刷新会话列表
  const refreshSessions = async () => {
    try {
      const sessionsList = await getSessions()
      
      // 为每个会话添加category属性
      const sessionsWithCategory = sessionsList.map((session: Session) => ({
        ...session,
        category: getSessionCategory(session.updated_at || session.created_at)
      }))
      
      setSessions(sessionsWithCategory)
    } catch (error) {
      console.error("刷新会话列表失败", error)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  // 开始新会话
  const startNewChat = async () => {
    try {
      const date = new Date();
      const formattedDate = date.toLocaleDateString('zh-CN', {
        month: '2-digit',
        day: '2-digit'
      });
      const formattedTime = date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
      });
      
      const newSession = await createSession(`新会话 ${formattedDate} ${formattedTime}`);
      
      // 刷新会话列表
      await refreshSessions()
      
      // 设置新会话为活动会话
    setActiveSession(newSession.id)
      setMessages([])

    // 在移动设备上，创建新会话后关闭侧边栏
    if (isMobile) {
      setSidebarOpen(false)
    }

    // 聚焦输入框
    setTimeout(() => {
      inputRef.current?.focus()
    }, 100)
    } catch (error) {
      console.error("创建会话失败", error)
      setError("创建会话失败")
    }
  }

  // 删除会话
  const handleDeleteSession = async (sessionId: number, e?: React.MouseEvent) => {
    // 如果有事件对象，阻止事件冒泡
    if (e && typeof e.stopPropagation === 'function') {
      e.stopPropagation();
    }
    
    try {
      setToast({
        visible: true,
        message: "正在删除会话...",
        variant: "default"
      });
      
      await deleteSession(sessionId);
      
      // 如果删除的是当前活动会话，清空消息列表
      if (sessionId === activeSession) {
        setMessages([]);
        setActiveSession(null);
      }
      
      // 刷新会话列表
      await refreshSessions();
      
      setToast({
        visible: true,
        message: "会话已删除",
        variant: "success"
      });
    } catch (error) {
      console.error("删除会话失败", error);
      setToast({
        visible: true,
        message: "删除会话失败",
        variant: "error"
      });
    }
  }

  // 删除消息
  const handleDeleteMessage = async (messageId: number, sessionId: number, e?: React.MouseEvent) => {
    // 如果有事件对象，阻止事件冒泡
    if (e && typeof e.stopPropagation === 'function') {
      e.stopPropagation();
    }
    
    try {
      setToast({
        visible: true,
        message: "正在删除消息...",
        variant: "default"
      });
      
      await deleteMessage(sessionId, messageId);
      
      // 从界面上移除消息
      setMessages(prev => prev.filter(msg => msg.id !== messageId));
      
      setToast({
        visible: true,
        message: "消息已删除",
        variant: "success"
      });
    } catch (error) {
      console.error("删除消息失败", error);
      setToast({
        visible: true,
        message: "删除消息失败",
        variant: "error"
      });
    }
  }

  // 清空会话消息
  const handleClearSessionMessages = async (sessionId: number) => {
    try {
      setToast({
        visible: true,
        message: "正在清空会话...",
        variant: "default"
      });
      
      await clearSessionMessages(sessionId);
      
      // 清空界面上的消息
      setMessages([]);
      
      setToast({
        visible: true,
        message: "会话已清空",
        variant: "success"
      });
    } catch (error) {
      console.error("清空会话失败", error);
      setToast({
        visible: true,
        message: "清空会话失败",
        variant: "error"
      });
    }
  }

  // 确认删除会话
  const confirmDeleteSession = (sessionId: number, e: React.MouseEvent) => {
    e.stopPropagation()
    
    setConfirmDialog({
      isOpen: true,
      sessionId: sessionId,
      messageId: 0,
      action: "deleteSession",
      title: "删除会话",
      message: "确定要删除这个会话吗？此操作不可撤销。"
    })
  }

  // 确认清空会话
  const confirmClearSession = (sessionId: number, e: React.MouseEvent) => {
    e.stopPropagation()
    
    setConfirmDialog({
      isOpen: true,
      sessionId: sessionId,
      messageId: 0,
      action: "clearSession",
      title: "清空会话",
      message: "确定要清空这个会话中的所有消息吗？此操作不可撤销，但会保留会话本身。"
    })
  }

  // 确认删除消息
  const confirmDeleteMessage = (messageId: number, sessionId: number, e: React.MouseEvent) => {
    e.stopPropagation()
    
    setConfirmDialog({
      isOpen: true,
      sessionId: sessionId,
      messageId: messageId,
      action: "deleteMessage",
      title: "删除消息",
      message: "确定要删除这条消息吗？此操作不可撤销。"
    })
  }

  // 关闭确认对话框
  const closeConfirmDialog = () => {
    setConfirmDialog(prev => ({ ...prev, isOpen: false }))
  }

  // 执行确认的操作
  const executeConfirmedAction = () => {
    switch (confirmDialog.action) {
      case "deleteSession":
        if (confirmDialog.sessionId) {
          handleDeleteSession(confirmDialog.sessionId);
        }
        break;
      case "clearSession":
        if (confirmDialog.sessionId) {
          handleClearSessionMessages(confirmDialog.sessionId);
        }
        break;
      case "deleteMessage":
        if (confirmDialog.messageId && confirmDialog.sessionId) {
          handleDeleteMessage(confirmDialog.messageId, confirmDialog.sessionId);
        }
        break;
    }
    closeConfirmDialog();
  }

  // 复制消息内容
  const copyMessageContent = (content: string) => {
    navigator.clipboard.writeText(content)
      .then(() => {
        setToast({
          visible: true,
          message: "已复制到剪贴板",
          variant: "success"
        })
      })
      .catch(err => {
        console.error("复制失败", err)
        setToast({
          visible: true,
          message: "复制失败",
          variant: "error"
        })
      })
  }

  // 关闭通知
  const closeToast = () => {
    setToast(prev => ({ ...prev, visible: false }))
  }

  // 获取会话标题的截断版本
  const getTruncatedTitle = (title: string, maxLength = 25) => {
    if (!title) return "新会话";
    
    // 尝试提取和美化会话标题
    const match = title.match(/新会话\s+([\d/]+)\s+([\d:]+)/);
    if (match && match[1] && match[2]) {
      // 如果标题符合"新会话 日期 时间"的格式，美化显示
      return `新会话 ${match[1]} ${match[2]}`;
    }
    
    return title.length > maxLength ? `${title.substring(0, maxLength)}...` : title;
  }

  // 渲染消息内容，支持Markdown
  const renderMessageContent = (content: string) => {
    return <MarkdownRenderer content={content} className="markdown-content" />;
  }

  // 检查是否需要刷新认证
  useEffect(() => {
    // 每10秒检查一次认证状态
    const interval = setInterval(async () => {
      console.log('Periodic auth check');
      if (isAuthenticated) {
        await checkAuth();
      }
    }, 10000);
    
    return () => clearInterval(interval);
  }, [isAuthenticated, checkAuth]);

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Toast通知 */}
      <CustomToast
        visible={toast.visible}
        onClose={closeToast}
        variant={toast.variant as "default" | "success" | "error"}
      >
        {toast.message}
      </CustomToast>

      {/* 确认对话框 */}
      <ConfirmDialog
        isOpen={confirmDialog.isOpen}
        onClose={closeConfirmDialog}
        onConfirm={executeConfirmedAction}
        title={confirmDialog.title}
        message={confirmDialog.message}
        variant="danger"
        confirmText={confirmDialog.action === "deleteSession" ? "删除" : 
                     confirmDialog.action === "clearSession" ? "清空" : "删除"}
      />

      {/* 移动端菜单按钮 */}
      {isMobile && (
        <button
          className="fixed top-4 left-4 z-50 p-2 bg-white rounded-md shadow-md"
          onClick={() => setSidebarOpen(!sidebarOpen)}
        >
          {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      )}

      {/* 侧边栏 */}
      <div
        className={cn(
          "fixed inset-y-0 left-0 z-40 w-64 bg-white border-r border-gray-200 transition-transform duration-300 ease-in-out",
          isMobile ? (sidebarOpen ? "translate-x-0" : "-translate-x-full") : "translate-x-0",
        )}
      >
        <div className="flex flex-col h-full">
          {/* 侧边栏头部 */}
          <div className="p-4 border-b border-gray-200 flex items-center justify-between">
            <Link href="/" className="text-xl font-bold text-blue-600">
              FastAgent
            </Link>
            {isMobile && (
              <button onClick={() => setSidebarOpen(false)}>
                <X size={20} />
              </button>
            )}
          </div>

          {/* 新建对话按钮 */}
          <div className="p-4">
            <Button
              onClick={startNewChat}
              className="w-full bg-blue-50 text-blue-600 hover:bg-blue-100 flex items-center justify-center gap-2"
              variant="outline"
            >
              <MessageSquare size={16} />
              开启新对话
            </Button>
          </div>

          {/* 会话列表 */}
          <ScrollArea className="flex-1 px-3">
            {sessions.length === 0 ? (
              <div className="text-center py-8 text-gray-500">暂无历史会话</div>
            ) : (
              <div className="space-y-6 py-4">
                {/* 今天的会话 */}
                {sessions.some(session => session.category === "today") && (
                  <div>
                    <h3 className="text-xs font-medium text-gray-500 mb-2 px-2">今天</h3>
                    <div className="space-y-1">
                      {sessions
                        .filter(session => session.category === "today")
                        .map(session => (
                          <div
                            key={session.id}
                            className={cn(
                              "flex items-center justify-between group p-2 rounded-md cursor-pointer relative",
                              session.id === activeSession
                                ? "bg-blue-50 text-blue-600"
                                : "hover:bg-gray-100"
                            )}
                            onClick={() => loadSessionMessages(session.id)}
                          >
                            <div className={cn(
                              "flex items-center space-x-2 w-full overflow-hidden transition-opacity duration-200",
                              session.id === activeSession 
                                ? "" 
                                : "group-hover:opacity-60"
                            )}>
                              <MessageSquare size={16} className="flex-shrink-0" />
                              <span className="truncate">{getTruncatedTitle(session.title, 20)}</span>
                            </div>
                            <div className={cn(
                              "absolute right-2 flex items-center space-x-1 transition-all duration-200",
                              session.id === activeSession 
                                ? "opacity-80 hover:opacity-100" 
                                : "opacity-0 group-hover:opacity-80"
                            )}>
                              <button
                                className="text-gray-400 hover:text-blue-500 transition-all duration-200 p-1 rounded-full hover:bg-blue-50 flex-shrink-0"
                                onClick={(e) => confirmClearSession(session.id, e)}
                                title="清空会话"
                              >
                                <Eraser size={14} />
                              </button>
                              <button
                                className="text-gray-400 hover:text-red-500 transition-all duration-200 p-1 rounded-full hover:bg-red-50 flex-shrink-0"
                                onClick={(e) => confirmDeleteSession(session.id, e)}
                                title="删除会话"
                              >
                                <X size={14} />
                              </button>
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>
                )}

                {/* 本周的会话 */}
                {sessions.some(session => session.category === "week") && (
                  <div>
                    <h3 className="text-xs font-medium text-gray-500 mb-2 px-2">本周</h3>
                    <div className="space-y-1">
                      {sessions
                        .filter(session => session.category === "week")
                        .map(session => (
                          <div
                            key={session.id}
                            className={cn(
                              "flex items-center justify-between group p-2 rounded-md cursor-pointer relative",
                              session.id === activeSession
                                ? "bg-blue-50 text-blue-600"
                                : "hover:bg-gray-100"
                            )}
                            onClick={() => loadSessionMessages(session.id)}
                          >
                            <div className={cn(
                              "flex items-center space-x-2 w-full overflow-hidden transition-opacity duration-200",
                              session.id === activeSession 
                                ? "" 
                                : "group-hover:opacity-60"
                            )}>
                              <MessageSquare size={16} className="flex-shrink-0" />
                              <span className="truncate">{getTruncatedTitle(session.title, 20)}</span>
                            </div>
                            <div className={cn(
                              "absolute right-2 flex items-center space-x-1 transition-all duration-200",
                              session.id === activeSession 
                                ? "opacity-80 hover:opacity-100" 
                                : "opacity-0 group-hover:opacity-80"
                            )}>
                              <button
                                className="text-gray-400 hover:text-blue-500 transition-all duration-200 p-1 rounded-full hover:bg-blue-50 flex-shrink-0"
                                onClick={(e) => confirmClearSession(session.id, e)}
                                title="清空会话"
                              >
                                <Eraser size={14} />
                              </button>
                              <button
                                className="text-gray-400 hover:text-red-500 transition-all duration-200 p-1 rounded-full hover:bg-red-50 flex-shrink-0"
                                onClick={(e) => confirmDeleteSession(session.id, e)}
                                title="删除会话"
                              >
                                <X size={14} />
                              </button>
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>
                )}

                {/* 本月的会话 */}
                {sessions.some(session => session.category === "month") && (
                  <div>
                    <h3 className="text-xs font-medium text-gray-500 mb-2 px-2">本月</h3>
                  <div className="space-y-1">
                      {sessions
                        .filter(session => session.category === "month")
                        .map(session => (
                          <div
                            key={session.id}
                            className={cn(
                              "flex items-center justify-between group p-2 rounded-md cursor-pointer relative",
                              session.id === activeSession
                                ? "bg-blue-50 text-blue-600"
                                : "hover:bg-gray-100"
                            )}
                            onClick={() => loadSessionMessages(session.id)}
                          >
                            <div className={cn(
                              "flex items-center space-x-2 w-full overflow-hidden transition-opacity duration-200",
                              session.id === activeSession 
                                ? "" 
                                : "group-hover:opacity-60"
                            )}>
                              <MessageSquare size={16} className="flex-shrink-0" />
                              <span className="truncate">{getTruncatedTitle(session.title, 20)}</span>
                            </div>
                            <div className={cn(
                              "absolute right-2 flex items-center space-x-1 transition-all duration-200",
                              session.id === activeSession 
                                ? "opacity-80 hover:opacity-100" 
                                : "opacity-0 group-hover:opacity-80"
                            )}>
                              <button
                                className="text-gray-400 hover:text-blue-500 transition-all duration-200 p-1 rounded-full hover:bg-blue-50 flex-shrink-0"
                                onClick={(e) => confirmClearSession(session.id, e)}
                                title="清空会话"
                              >
                                <Eraser size={14} />
                              </button>
                      <button
                                className="text-gray-400 hover:text-red-500 transition-all duration-200 p-1 rounded-full hover:bg-red-50 flex-shrink-0"
                                onClick={(e) => confirmDeleteSession(session.id, e)}
                                title="删除会话"
                              >
                                <X size={14} />
                              </button>
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>
                )}

                {/* 更早的会话 */}
                {sessions.some(session => session.category === "earlier") && (
                  <div>
                    <h3 className="text-xs font-medium text-gray-500 mb-2 px-2">更早</h3>
                    <div className="space-y-1">
                      {sessions
                        .filter(session => session.category === "earlier")
                        .map(session => (
                          <div
                        key={session.id}
                        className={cn(
                              "flex items-center justify-between group p-2 rounded-md cursor-pointer relative",
                              session.id === activeSession
                                ? "bg-blue-50 text-blue-600"
                                : "hover:bg-gray-100"
                            )}
                            onClick={() => loadSessionMessages(session.id)}
                          >
                            <div className={cn(
                              "flex items-center space-x-2 w-full overflow-hidden transition-opacity duration-200",
                              session.id === activeSession 
                                ? "" 
                                : "group-hover:opacity-60"
                            )}>
                              <MessageSquare size={16} className="flex-shrink-0" />
                              <span className="truncate">{getTruncatedTitle(session.title, 20)}</span>
                            </div>
                            <div className={cn(
                              "absolute right-2 flex items-center space-x-1 transition-all duration-200",
                              session.id === activeSession 
                                ? "opacity-80 hover:opacity-100" 
                                : "opacity-0 group-hover:opacity-80"
                            )}>
                              <button
                                className="text-gray-400 hover:text-blue-500 transition-all duration-200 p-1 rounded-full hover:bg-blue-50 flex-shrink-0"
                                onClick={(e) => confirmClearSession(session.id, e)}
                                title="清空会话"
                              >
                                <Eraser size={14} />
                              </button>
                              <button
                                className="text-gray-400 hover:text-red-500 transition-all duration-200 p-1 rounded-full hover:bg-red-50 flex-shrink-0"
                                onClick={(e) => confirmDeleteSession(session.id, e)}
                                title="删除会话"
                              >
                                <X size={14} />
                      </button>
                            </div>
                          </div>
                    ))}
                    </div>
                  </div>
                )}
                </div>
            )}
          </ScrollArea>

          {/* 底部用户信息 */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="h-8 w-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center">
                  <User size={16} />
                </div>
                <div className="text-sm">
                  <div className="font-medium">{user?.username || "用户"}</div>
                  <div className="text-xs text-gray-500">{user?.email || ""}</div>
                </div>
              </div>
              <div className="flex space-x-1">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button size="icon" variant="ghost" className="h-8 w-8">
                        <Settings size={16} />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>设置</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button size="icon" variant="ghost" className="h-8 w-8" onClick={logout}>
                        <LogOut size={16} />
              </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>登出</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 主要内容区域 */}
      <div
        className={cn(
          "flex flex-col flex-1 h-screen",
          isMobile ? "ml-0" : "ml-64"
        )}
      >
        {/* 聊天主体 */}
        <div className="flex-1 overflow-hidden bg-gray-50">
          {error ? (
            <div className="flex h-full items-center justify-center">
              <div className="text-center p-6 max-w-md">
                <div className="mb-4 text-red-500">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-12 w-12 mx-auto"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    />
                  </svg>
                </div>
                <h3 className="text-xl font-medium text-gray-900 mb-2">发生错误</h3>
                <p className="text-gray-600 mb-4">{error}</p>
                <Button onClick={() => setError("")}>重试</Button>
              </div>
            </div>
          ) : loading ? (
            <div className="flex h-full items-center justify-center">
              <div className="text-center">
                <RefreshCw className="h-10 w-10 mx-auto animate-spin text-blue-600 mb-4" />
                <p className="text-gray-600">加载中...</p>
              </div>
            </div>
          ) : !activeSession ? (
            <div className="flex h-full items-center justify-center">
              <div className="text-center p-6 max-w-md">
                <div className="mb-4 text-blue-600">
                  <MessageSquare className="h-12 w-12 mx-auto" />
                </div>
                <h3 className="text-xl font-medium text-gray-900 mb-2">欢迎使用 FastAgent</h3>
                <p className="text-gray-600 mb-4">选择一个现有的会话，或者开始一个新的对话。</p>
                <Button onClick={startNewChat}>开启新对话</Button>
              </div>
            </div>
          ) : (
            <ScrollArea className="h-full pb-24 pt-4 px-4">
              <div className="max-w-4xl mx-auto">
                {messages.length === 0 ? (
                  <div className="flex h-full items-center justify-center min-h-[60vh]">
                    <div className="text-center max-w-md">
                      <MessageSquare className="h-12 w-12 mx-auto text-blue-600 mb-4" />
                      <h3 className="text-xl font-medium text-gray-900 mb-2">开始一个新的对话</h3>
                      <p className="text-gray-600">
                        在下方输入您的问题，FastAgent将为您提供所需的答案和帮助。
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-8 py-4">
                    {/* 添加清空会话按钮 */}
                    <div className="flex justify-center">
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-gray-600 hover:bg-red-50 hover:text-red-600 border-gray-300"
                        onClick={(e) => confirmClearSession(activeSession, e as any)}
                      >
                        <Eraser size={14} className="mr-2" />
                        清空会话
                  </Button>
          </div>

                    {messages.map((message) => {
                      // 不再处理URL格式，保留原始形式方便复制
                      const processedContent = message.content;
                      
                      return (
                <div
                        key={message.id}
                  className={cn(
                          "flex items-start gap-3 group",
                          message.role === "user" ? "justify-end" : "justify-start"
                  )}
                >
                  {message.role === "assistant" && (
                          <div className="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 shadow-sm">
                            <MessageSquare size={20} />
                          </div>
                        )}
                        <div
                          className={cn(
                            "rounded-2xl p-4 shadow-sm relative",
                            message.role === "user" 
                              ? "bg-blue-600 text-white max-w-[70%]"
                              : "bg-white text-gray-800 max-w-[75%] border border-gray-100"
                          )}
                        >
                          {/* 删除消息按钮 */}
                          <button
                            className={cn(
                              "absolute -top-2 -right-2 p-1 rounded-full transition-opacity duration-200 z-10",
                              message.role === "user" ? "bg-blue-700 text-white" : "bg-gray-100 text-gray-500",
                              "opacity-0 group-hover:opacity-100 hover:bg-red-500 hover:text-white"
                            )}
                            onClick={(e) => confirmDeleteMessage(message.id, activeSession, e)}
                            title="删除消息"
                          >
                            <Trash2 size={14} />
                          </button>
                          
                            <div className={cn(
                              "prose max-w-none",
                              message.role === "user" ? "user-message-content" : ""
                            )}>
                              {renderMessageContent(processedContent)}
                      </div>
                          <div className={cn(
                              "mt-2 flex items-center text-xs opacity-70",
                              message.role === "user" ? "justify-start" : "justify-between"
                            )}>
                            <span className={message.role === "user" ? "text-blue-100" : "text-gray-500"}>
                              {formatTime(message.created_at)}
                            </span>
                            
                  {message.role === "assistant" && (
                              <div className="flex items-center gap-2">
                                <button
                                  className="rounded-md p-1 hover:bg-gray-200"
                                  onClick={() => copyMessageContent(message.content)}
                                  title="复制内容"
                                >
                              <Copy size={14} />
                                </button>
                                <button className="rounded-md p-1 hover:bg-gray-200" title="有帮助">
                              <ThumbsUp size={14} />
                                </button>
                                <button className="rounded-md p-1 hover:bg-gray-200" title="没帮助">
                              <ThumbsDown size={14} />
                                </button>
                    </div>
                  )}
                </div>
                        </div>
                        {message.role === "user" && (
                          <div className="flex-shrink-0 w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white">
                            <User size={20} />
                          </div>
                        )}
              </div>
                      );
                    })}
                    
            {isTyping && (
                      <div className="flex items-start gap-3 justify-start">
                        <div className="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 shadow-sm">
                          <MessageSquare size={20} />
                        </div>
                        <div className="bg-white border border-gray-100 rounded-2xl p-4 max-w-[75%] shadow-sm">
                          <div className="flex space-x-2">
                            <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce"></div>
                            <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                            <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                  </div>
                </div>
              </div>
            )}
                  </div>
                )}
                
            <div ref={messagesEndRef} />
          </div>
            </ScrollArea>
          )}
        </div>

        {/* 输入区域 */}
        {activeSession && (
          <div className="border-t border-gray-200 bg-white p-4 shadow-sm relative">
            <div className="max-w-4xl mx-auto">
              <form
                onSubmit={(e) => {
                  e.preventDefault()
                  handleSendMessage()
                }}
                className="relative"
              >
              <Input
                ref={inputRef}
                  placeholder="输入消息..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                  className="pr-24 pl-12 py-6 bg-gray-50 border-gray-200 rounded-3xl shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  disabled={isTyping || loading}
              />
                <button
                  type="button"
                  className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                        <Paperclip size={18} />
                </button>
                <div className="absolute right-4 top-1/2 transform -translate-y-1/2 flex space-x-1">
                <Button
                    type="submit"
                  size="icon"
                    className="h-8 w-8 rounded-full bg-blue-600 hover:bg-blue-700"
                    disabled={!input.trim() || isTyping || loading}
                >
                    <Send size={16} className="text-white" />
                </Button>
                </div>
              </form>
              <div className="text-xs text-center text-gray-500 mt-2">
                以上对话由 FastAgent 提供支持
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
