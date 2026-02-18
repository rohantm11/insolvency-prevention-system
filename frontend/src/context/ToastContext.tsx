/**
 * @fileoverview Toast notification system using React Context.
 * Provides success, error, warning, and info notifications.
 */

import { createContext, useContext, useState, useCallback } from 'react';
import type { ReactNode } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertTriangle, Info, AlertCircle } from 'lucide-react';

/** Available toast notification types */
type ToastType = 'success' | 'error' | 'warning' | 'info';

/**
 * Toast notification data structure.
 */
interface Toast {
  /** Unique identifier */
  id: string;
  /** Notification type determining icon and color */
  type: ToastType;
  /** Main toast title */
  title: string;
  /** Optional detailed message */
  message?: string;
  /** Display duration in ms (default 5000) */
  duration?: number;
}

/**
 * Context value providing toast management functions.
 */
interface ToastContextValue {
  /** Array of active toasts */
  toasts: Toast[];
  /** Add a custom toast */
  addToast: (toast: Omit<Toast, 'id'>) => void;
  /** Remove a toast by ID */
  removeToast: (id: string) => void;
  /** Show a success toast */
  success: (title: string, message?: string) => void;
  /** Show an error toast (8s duration) */
  error: (title: string, message?: string) => void;
  /** Show a warning toast */
  warning: (title: string, message?: string) => void;
  /** Show an info toast */
  info: (title: string, message?: string) => void;
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

/**
 * Toast provider component that wraps the app to provide toast notifications.
 * @param {{ children: ReactNode }} props - Component props
 * @returns {JSX.Element} Provider with toast container
 */
export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  const addToast = useCallback(
    (toast: Omit<Toast, 'id'>) => {
      const id = Math.random().toString(36).substring(2, 9);
      const newToast: Toast = { ...toast, id };
      setToasts((prev) => [...prev, newToast]);

      // Auto-remove after duration (default 5 seconds)
      const duration = toast.duration ?? 5000;
      if (duration > 0) {
        setTimeout(() => {
          removeToast(id);
        }, duration);
      }
    },
    [removeToast]
  );

  const success = useCallback(
    (title: string, message?: string) => {
      addToast({ type: 'success', title, message });
    },
    [addToast]
  );

  const error = useCallback(
    (title: string, message?: string) => {
      addToast({ type: 'error', title, message, duration: 8000 });
    },
    [addToast]
  );

  const warning = useCallback(
    (title: string, message?: string) => {
      addToast({ type: 'warning', title, message });
    },
    [addToast]
  );

  const info = useCallback(
    (title: string, message?: string) => {
      addToast({ type: 'info', title, message });
    },
    [addToast]
  );

  return (
    <ToastContext.Provider
      value={{ toasts, addToast, removeToast, success, error, warning, info }}
    >
      {children}
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </ToastContext.Provider>
  );
}

/**
 * Hook to access toast notification functions.
 * @returns {ToastContextValue} Toast context with notification methods
 * @throws {Error} If used outside of ToastProvider
 */
export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

/**
 * Container component that renders active toasts in the bottom-right corner.
 * @param {object} props - Component props
 * @returns {JSX.Element} Fixed position toast container
 */
function ToastContainer({
  toasts,
  removeToast,
}: {
  toasts: Toast[];
  removeToast: (id: string) => void;
}) {
  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
      <AnimatePresence>
        {toasts.map((toast) => (
          <ToastItem key={toast.id} toast={toast} onClose={() => removeToast(toast.id)} />
        ))}
      </AnimatePresence>
    </div>
  );
}

/**
 * Individual toast notification component with icon, title, message, and close button.
 * @param {object} props - Toast data and close handler
 * @returns {JSX.Element} Styled toast notification
 */
function ToastItem({ toast, onClose }: { toast: Toast; onClose: () => void }) {
  const icons = {
    success: CheckCircle,
    error: AlertCircle,
    warning: AlertTriangle,
    info: Info,
  };

  const colors = {
    success: {
      bg: 'bg-green-500/10 border-green-500/30',
      icon: 'text-green-400',
      title: 'text-green-400',
    },
    error: {
      bg: 'bg-red-500/10 border-red-500/30',
      icon: 'text-red-400',
      title: 'text-red-400',
    },
    warning: {
      bg: 'bg-yellow-500/10 border-yellow-500/30',
      icon: 'text-yellow-400',
      title: 'text-yellow-400',
    },
    info: {
      bg: 'bg-blue-500/10 border-blue-500/30',
      icon: 'text-blue-400',
      title: 'text-blue-400',
    },
  };

  const Icon = icons[toast.type];
  const colorClasses = colors[toast.type];

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: 24 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 24 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      className={`flex items-start gap-3 p-4 rounded-lg border backdrop-blur-sm shadow-lg ${colorClasses.bg}`}
    >
      <Icon className={`w-5 h-5 flex-shrink-0 mt-0.5 ${colorClasses.icon}`} />
      <div className="flex-1 min-w-0">
        <p className={`font-medium ${colorClasses.title}`}>{toast.title}</p>
        {toast.message && (
          <p className="text-dark-300 text-sm mt-1">{toast.message}</p>
        )}
      </div>
      <button
        onClick={onClose}
        className="flex-shrink-0 p-1 hover:bg-dark-700 rounded transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
      >
        <X className="w-4 h-4 text-dark-400" />
      </button>
    </motion.div>
  );
}

export default ToastContext;
