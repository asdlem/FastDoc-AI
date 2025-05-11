"use client"

import * as React from "react"
import { Check, X } from "lucide-react"
import { cn } from "@/lib/utils"
import { useState } from "react"

export interface CustomToastProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "success" | "error"
  visible: boolean
  onClose: () => void
}

export const CustomToast = React.forwardRef<HTMLDivElement, CustomToastProps>(
  ({ className, variant = "default", visible, onClose, children, ...props }, ref) => {
    const [isExiting, setIsExiting] = useState(false);
    const timerRef = React.useRef<NodeJS.Timeout | null>(null);

    React.useEffect(() => {
      if (visible) {
        // 自动关闭定时器
        timerRef.current = setTimeout(() => {
          handleClose();
        }, 3000);
      }
      
      return () => {
        if (timerRef.current) {
          clearTimeout(timerRef.current);
        }
      };
    }, [visible]);
    
    const handleClose = () => {
      setIsExiting(true);
      // 等待动画完成后真正关闭
      setTimeout(() => {
        setIsExiting(false);
        onClose();
      }, 300);
    };

    if (!visible) return null;

    return (
      <div
        ref={ref}
        className={cn(
          "fixed top-4 right-4 z-50 flex items-center gap-2 rounded-lg py-3 px-4 shadow-lg md:max-w-sm max-w-[calc(100%-2rem)]",
          variant === "success" && "bg-green-100 text-green-800 border border-green-200",
          variant === "error" && "bg-red-100 text-red-800 border border-red-200",
          variant === "default" && "bg-blue-100 text-blue-800 border border-blue-200",
          className
        )}
        style={{
          animation: isExiting ? "slideOut 0.3s ease-out" : "slideIn 0.3s ease-out"
        }}
        {...props}
      >
        <div className="shrink-0">
          {variant === "success" && (
            <Check className="h-5 w-5 text-green-600" />
          )}
          {variant === "error" && (
            <X className="h-5 w-5 text-red-600" />
          )}
          {variant === "default" && (
            <div className="h-5 w-5 rounded-full bg-blue-500 flex items-center justify-center">
              <div className="h-1.5 w-1.5 bg-white rounded-full" />
            </div>
          )}
        </div>
        <div className="flex-1 text-sm font-medium break-words">{children}</div>
        <button
          onClick={handleClose}
          className="ml-2 shrink-0 rounded-full p-1 hover:bg-black/10 transition-colors"
          aria-label="关闭通知"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    )
  }
)

CustomToast.displayName = "CustomToast" 