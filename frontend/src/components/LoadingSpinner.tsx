import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Activity } from 'lucide-react';

const MESSAGES = [
  'Analyzing data\u2026',
  'Running model\u2026',
  'Computing risk\u2026',
  'Almost there\u2026',
];

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
}

export default function LoadingSpinner({ size = 'md', message }: LoadingSpinnerProps) {
  const [typedMessage, setTypedMessage] = useState('');
  const [messageIndex, setMessageIndex] = useState(0);
  const [progress, setProgress] = useState(0);

  const ringSize = { sm: 32, md: 52, lg: 72 }[size];
  const ringBorder = { sm: 2, md: 3, lg: 4 }[size];

  // Typing effect
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

  // Indeterminate progress
  useEffect(() => {
    const t = setInterval(() => {
      setProgress((p) => (p >= 95 ? 95 : p + Math.random() * 8 + 2));
    }, 400);
    return () => clearInterval(t);
  }, []);

  return (
    <motion.div
      className="flex flex-col items-center justify-center p-8"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95, filter: 'blur(4px)' }}
      transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
    >
      {/* Brand logo pulse */}
      <motion.div
        className="mb-4 w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center"
        animate={{ opacity: [0.5, 1, 0.5], scale: [0.95, 1.05, 0.95] }}
        transition={{ repeat: Infinity, duration: 2, ease: 'easeInOut' }}
        style={{ boxShadow: '0 0 30px rgba(6,182,212,0.25)' }}
      >
        <Activity className="w-5 h-5 text-white" />
      </motion.div>

      {/* Dual-ring spinner */}
      <div className="relative" style={{ width: ringSize, height: ringSize }}>
        <motion.div
          className="absolute inset-0 rounded-full"
          style={{
            border: `${ringBorder}px solid rgba(6,182,212,0.15)`,
            borderTopColor: 'rgba(6,182,212,0.8)',
          }}
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 1.1, ease: 'linear' }}
        />
        <motion.div
          className="absolute rounded-full"
          style={{
            inset: 5,
            border: `${Math.max(1, ringBorder - 1)}px solid rgba(59,130,246,0.1)`,
            borderBottomColor: 'rgba(59,130,246,0.6)',
          }}
          animate={{ rotate: -360 }}
          transition={{ repeat: Infinity, duration: 1.6, ease: 'linear' }}
        />
      </div>

      {/* Typing message */}
      <div className="mt-4 min-h-[1.5rem] flex items-center gap-1">
        <span className="text-dark-300 text-sm font-medium">{typedMessage}</span>
        <motion.span
          className="inline-block w-0.5 h-4 bg-primary-400"
          animate={{ opacity: [1, 0.2, 1] }}
          transition={{ repeat: Infinity, duration: 1.2, ease: 'easeInOut' }}
        />
      </div>

      {/* Progress bar */}
      <div className="mt-4 w-48 h-1 bg-dark-700 rounded-full overflow-hidden">
        <motion.div
          className="h-full rounded-full"
          style={{
            width: `${progress}%`,
            background: 'linear-gradient(90deg, #0891b2, #3b82f6, #0891b2)',
            backgroundSize: '200% 100%',
          }}
          animate={{ backgroundPosition: ['0% 0%', '200% 0%'] }}
          transition={{ repeat: Infinity, duration: 2, ease: 'linear' }}
        />
      </div>
    </motion.div>
  );
}
