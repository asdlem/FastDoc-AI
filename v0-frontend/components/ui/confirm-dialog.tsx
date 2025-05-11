"use client"

import * as React from "react"
import { X, AlertTriangle } from "lucide-react"
import { cn } from "@/lib/utils"

export interface ConfirmDialogProps extends React.HTMLAttributes<HTMLDivElement> {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  variant?: "default" | "danger" | "warning"
}

export const ConfirmDialog = React.forwardRef<HTMLDivElement, ConfirmDialogProps>(
  ({ 
    className, 
    isOpen, 
    onClose, 
    onConfirm, 
    title, 
    message, 
    confirmText = "确定", 
    cancelText = "取消", 
    variant = "default",
    ...props 
  }, ref) => {
    // 关闭时的背景点击处理
    const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
      if (e.target === e.currentTarget) {
        onClose();
      }
    };

    if (!isOpen) return null;

    return (
      <div 
        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        onClick={handleBackdropClick}
      >
        <div
          ref={ref}
          className={cn(
            "bg-white rounded-lg p-6 shadow-xl max-w-md w-full animate-in fade-in zoom-in-95 duration-200",
            className
          )}
          {...props}
        >
          <div className="flex items-center gap-3 mb-4">
            {variant === "danger" && (
              <div className="shrink-0 w-10 h-10 bg-red-100 rounded-full flex items-center justify-center text-red-600">
                <AlertTriangle size={20} />
              </div>
            )}
            {variant === "warning" && (
              <div className="shrink-0 w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center text-amber-600">
                <AlertTriangle size={20} />
              </div>
            )}
            <h3 className="text-lg font-semibold">{title}</h3>
            <button 
              onClick={onClose}
              className="ml-auto rounded-full p-1 hover:bg-gray-100 text-gray-500"
              aria-label="关闭"
            >
              <X size={18} />
            </button>
          </div>
          <div className="mb-6 text-gray-600">{message}</div>
          <div className="flex justify-end gap-3">
            <button 
              onClick={onClose}
              className="px-4 py-2 rounded-md border border-gray-200 bg-white hover:bg-gray-50 text-sm font-medium transition-colors"
            >
              {cancelText}
            </button>
            <button 
              onClick={() => {
                onConfirm();
                onClose();
              }}
              className={cn(
                "px-4 py-2 rounded-md text-white text-sm font-medium transition-colors",
                variant === "danger" && "bg-red-600 hover:bg-red-700",
                variant === "warning" && "bg-amber-600 hover:bg-amber-700",
                variant === "default" && "bg-blue-600 hover:bg-blue-700"
              )}
            >
              {confirmText}
            </button>
          </div>
        </div>
      </div>
    );
  }
);

ConfirmDialog.displayName = "ConfirmDialog"; 