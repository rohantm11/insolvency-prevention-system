import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const MESSAGES = [
  'Analyzing data…',
  'Running model…',
  'Computing risk…',
  'Almost there…',
];

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
}

export default function LoadingSpinner({ size = 'md', message }: LoadingSpinnerProps) {
  const [typedMessage, setTypedMessage] = useState('');
  const [messageIndex, setMessageIndex] = useState(0);
  const [progress, setProgress] = useState(0);

  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  // Typing effect: use message or cycle through MESSAGES
  useEffect(() => {
    const full = message ?? MESSAGES[messageIndex % MESSAGES.length];
    let i = 0;
    setTypedMessage('');
    const id = setInterval(() => {
      i++;
      if (i <= full.length) {
        setTypedMessage(full.slice(0, i));
      } else {
        clearInterval(id);
        if (!message) setTimeout(() => setMessageIndex((j) => j + 1), 800);
      }
    }, 50);
    return () => clearInterval(id);
  }, [message, messageIndex]);

  // Indeterminate progress line
  useEffect(() => {
    const t = setInterval(() => {
      setProgress((p) => (p >= 95 ? 95 : p + Math.random() * 8 + 2));
    }, 400);
    return () => clearInterval(t);
  }, []);

  const smoothEase = [0.33, 1, 0.68, 1] as const;

  return (
    <motion.div
      className="flex flex-col items-center justify-center p-8"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.35, ease: smoothEase }}
    >
      <motion.div
        className={`${sizeClasses[size]} rounded-full border-2 border-primary-500/30 border-t-primary-400`}
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 1.1, ease: 'linear' }}
      />
      <div className="mt-4 min-h-[1.5rem] flex items-center gap-1">
        <span className="text-dark-300 text-sm font-medium">{typedMessage}</span>
        <motion.span
          className="inline-block w-0.5 h-4 bg-primary-400"
          animate={{ opacity: [1, 0.25, 1] }}
          transition={{ repeat: Infinity, duration: 1.2, ease: 'easeInOut' }}
        />
      </div>
      <div className="mt-4 w-48 h-1 bg-dark-700 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-gradient-to-r from-primary-600 to-primary-400 rounded-full"
          style={{ width: `${progress}%` }}
          transition={{ duration: 0.5, ease: smoothEase }}
        />
      </div>
    </motion.div>
  );
}
