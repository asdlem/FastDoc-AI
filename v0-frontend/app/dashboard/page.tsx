import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function DashboardPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b border-gray-200 bg-white">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center">
            <Link href="/dashboard" className="text-xl font-bold text-blue-600">
              FastAgent
            </Link>
          </div>
          <div className="flex items-center space-x-4">
            <Button asChild variant="ghost">
              <Link href="/profile">个人信息</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/">退出登录</Link>
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto flex-1 px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">欢迎使用 FastAgent</h1>
          <p className="mt-2 text-gray-600">您的智能技术助手已准备就绪</p>
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-xl font-semibold text-gray-900">开始新对话</h2>
            <p className="mb-4 text-gray-600">向 FastAgent 提问任何技术问题，获取即时解答</p>
            <Button asChild className="w-full bg-blue-600 hover:bg-blue-700">
              <Link href="/chat/new">开始对话</Link>
            </Button>
          </div>

          <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-xl font-semibold text-gray-900">历史会话</h2>
            <p className="mb-4 text-gray-600">查看您之前的所有对话记录</p>
            <Button asChild variant="outline" className="w-full">
              <Link href="/chat/history">查看历史</Link>
            </Button>
          </div>

          <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-xl font-semibold text-gray-900">帮助中心</h2>
            <p className="mb-4 text-gray-600">了解如何更好地使用 FastAgent</p>
            <Button asChild variant="outline" className="w-full">
              <Link href="/help">查看帮助</Link>
            </Button>
          </div>
        </div>
      </main>

      <footer className="border-t border-gray-200 bg-white py-6">
        <div className="container mx-auto px-4 text-center text-sm text-gray-500">
          <p>
            浙ICP备20230258号 ·{" "}
            <Link href="/contact" className="text-blue-600 hover:underline">
              联系我们
            </Link>
          </p>
        </div>
      </footer>
    </div>
  )
}
