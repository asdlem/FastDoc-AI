"use client";

import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import rehypeRaw from "rehype-raw";
import { Check, Copy } from "lucide-react";
import { cn } from "@/lib/utils";

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

// 代码块组件，支持复制功能和语法高亮
const CodeBlock = ({ node, inline, className, children, ...props }: any) => {
  // 修复：明确检测代码块和内联代码的区别
  const isInlineCode = inline || !className;

  // 内联代码直接返回
  if (isInlineCode) {
    return (
      <code className={cn("px-1 py-0.5 rounded text-sm bg-muted font-mono", className)} {...props}>
        {children}
      </code>
    );
  }

  const match = /language-(\w+)/.exec(className || "");
  const [copied, setCopied] = useState(false);
  
  // 获取代码内容
  const codeString = String(children).replace(/\n$/, "");

  // 复制代码到剪贴板
  const copyCode = async () => {
    try {
      await navigator.clipboard.writeText(codeString);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("复制失败: ", err);
    }
  };
  
  // 检查是否是真正的代码块而不是被误识别的内联代码
  if (codeString.length < 80 && !codeString.includes("\n") && !match) {
    // 可能是被误识别为代码块的内联代码
    return (
      <code className="px-1 py-0.5 rounded text-sm bg-muted font-mono" {...props}>
        {children}
      </code>
    );
  }
  
  return (
    <div className="relative my-4 rounded-md border bg-muted overflow-hidden not-prose">
      <div className="flex items-center justify-between border-b bg-muted px-4 py-2">
        <span className="text-xs text-muted-foreground">
          {match?.[1] || "文本"}
        </span>
        <button
          onClick={copyCode}
          className="inline-flex items-center rounded-md p-1 text-muted-foreground hover:bg-accent hover:text-accent-foreground"
          aria-label={copied ? "已复制!" : "复制代码"}
        >
          {copied ? (
            <Check className="h-4 w-4" />
          ) : (
            <Copy className="h-4 w-4" />
          )}
        </button>
      </div>
      <pre className="overflow-x-auto p-4 text-sm m-0 font-mono border-0">
        <code className={className} {...props}>
          {children}
        </code>
      </pre>
    </div>
  );
};

// 组件映射
const components = {
  // 代码块
  code: CodeBlock,
  
  // 链接组件
  a: ({ node, href, children, className, ...props }: any) => {
    const isUserMessage = className?.includes("user-message-content") || false;
    
    return (
      <a 
        href={href} 
        className={cn(
          "no-underline",
          isUserMessage 
            ? "bg-blue-100 dark:bg-blue-900/30 px-1.5 py-0.5 rounded" 
            : "text-primary hover:opacity-90"
        )}
        target={href?.startsWith("http") ? "_blank" : undefined}
        rel={href?.startsWith("http") ? "noopener noreferrer" : undefined}
        {...props}
      >
        {children}
      </a>
    );
  },
  
  // 段落组件，处理嵌套问题
  p: ({ node, children, ...props }: any) => {
    // 检查是否包含代码块、预格式化文本或div
    const hasComplexContent = React.Children.toArray(children).some(
      (child: any) => 
        (child?.props?.node?.tagName === 'code' && !child?.props?.inline) || 
        child?.type === 'pre' ||
        child?.type === 'div'
    );
    
    // 如果包含这些复杂元素，用div代替p，避免嵌套错误
    if (hasComplexContent) {
      return <div className="my-4" {...props}>{children}</div>;
    }
    
    return <p className="mb-4" {...props}>{children}</p>;
  },
  
  // 处理列表项，避免列表项内的代码块嵌套问题
  li: ({ node, children, ...props }: any) => {
    // 检查列表项中是否包含代码块
    const hasComplexContent = React.Children.toArray(children).some(
      (child: any) => 
        (child?.props?.node?.tagName === 'code' && !child?.props?.inline) || 
        child?.type === 'pre' ||
        child?.type === 'div'
    );
    
    if (hasComplexContent) {
      return (
        <li {...props}>
          <div className="my-2">{children}</div>
        </li>
      );
    }
    
    return <li {...props}>{children}</li>;
  },
  
  // 处理pre标签，避免与代码块重复嵌套
  pre: ({ node, children, ...props }: any) => {
    // 如果pre直接包含code，我们已经在CodeBlock处理了
    if (node && node.children && node.children.length === 1 && node.children[0].tagName === 'code') {
      // 检查是否是误判的内联代码
      const codeNode = node.children[0];
      if (codeNode.properties && !codeNode.properties.className) {
        const textContent = codeNode.children[0]?.value || '';
        if (textContent.length < 80 && !textContent.includes("\n")) {
          return (
            <code className="px-1 py-0.5 rounded text-sm bg-muted font-mono">
              {textContent}
            </code>
          );
        }
      }
      return children;
    }
    
    // 其他pre标签正常渲染
    return <pre className="my-4 p-4 bg-muted rounded-md overflow-x-auto" {...props}>{children}</pre>;
  }
};

// 前处理Markdown内容，修复常见格式问题
const preprocessMarkdown = (content: string): string => {
  if (!content) return '';
  
  // 修复内联代码被错误解析为代码块的问题
  // 例如：使用 `curl` 或 `Spring CLI` 这样的语法
  // 确保所有的单行内联代码使用正确的语法
  return content.replace(/`([^`\n]+)`/g, (match, code) => {
    // 确保内联代码使用单个反引号而不是被识别为代码块
    if (code.length < 80 && !code.includes('\n')) {
      return '`' + code + '`';
    }
    return match;
  });
};

export function MarkdownRenderer({ content, className }: MarkdownRendererProps) {
  if (!content) return null;
  
  // 预处理Markdown内容
  const processedContent = preprocessMarkdown(content);

  return (
    <div className={cn("prose dark:prose-invert max-w-none break-words", className)}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight, rehypeRaw]}
        components={components}
        skipHtml={false}
      >
        {processedContent}
      </ReactMarkdown>
    </div>
  );
} 