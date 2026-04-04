/**
 * Small ? icon that shows a plain-English explanation on hover/focus.
 * For Z-Score, SHAP, distress probability, etc.
 */
import { useState, useRef, useEffect } from 'react';
import { HelpCircle } from 'lucide-react';

interface TooltipProps {
  content: string;
  title?: string;
  side?: 'top' | 'bottom' | 'left' | 'right';
  className?: string;
}

export default function Tooltip({ content, title, side = 'top', className = '' }: TooltipProps) {
  const [visible, setVisible] = useState(false);
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (!visible) return;
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setVisible(false);
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [visible]);

  const positionClasses = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  };

  return (
    <span
      ref={ref}
      className={`relative inline-flex align-middle ${className}`}
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
      onFocus={() => setVisible(true)}
      onBlur={() => setVisible(false)}
    >
      <button
        type="button"
        className="inline-flex items-center justify-center w-5 h-5 rounded-full text-slate-400 hover:text-primary-500 dark:text-dark-400 dark:hover:text-primary-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500/50"
        aria-label="What does this mean?"
      >
        <HelpCircle className="w-4 h-4" />
      </button>
      {visible && (
        <span
          role="tooltip"
          className={`absolute z-50 w-64 px-3 py-2 text-sm text-left rounded-lg shadow-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-dark-800 text-slate-700 dark:text-dark-200 ${positionClasses[side]}`}
        >
          {title && <span className="font-semibold block mb-1 text-slate-800 dark:text-white">{title}</span>}
          <span className="block">{content}</span>
        </span>
      )}
    </span>
  );
}
