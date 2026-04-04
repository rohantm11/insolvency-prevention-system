/**
 * Button with ripple, glow on hover, and optional loading/success morph.
 */
import { useRef, useState } from 'react';
import { motion } from 'framer-motion';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'success';

interface AnimatedButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  children: React.ReactNode;
  loading?: boolean;
  success?: boolean;
  className?: string;
  /** Show ripple on click */
  ripple?: boolean;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary: 'bg-primary-600 hover:bg-primary-500 text-white focus-visible:ring-primary-500 shadow-primary-glow',
  secondary: 'bg-dark-700 hover:bg-dark-600 text-white focus-visible:ring-dark-500',
  ghost: 'bg-transparent hover:bg-dark-800 text-dark-200 focus-visible:ring-dark-500',
  danger: 'bg-red-600 hover:bg-red-500 text-white focus-visible:ring-red-500',
  success: 'bg-green-600 hover:bg-green-500 text-white focus-visible:ring-green-500',
};

export default function AnimatedButton({
  variant = 'primary',
  children,
  loading = false,
  success = false,
  className = '',
  ripple = true,
  disabled,
  onClick,
}: AnimatedButtonProps) {
  const [ripples, setRipples] = useState<{ id: number; x: number; y: number }[]>([]);
  const btnRef = useRef<HTMLButtonElement>(null);
  const nextId = useRef(0);

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (ripple && btnRef.current) {
      const rect = btnRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const id = nextId.current++;
      setRipples((prev) => [...prev, { id, x, y }]);
      setTimeout(() => setRipples((prev) => prev.filter((r) => r.id !== id)), 600);
    }
    onClick?.(e);
  };

  const isDisabled = disabled || loading;

  return (
    <motion.button
      ref={btnRef}
      type="button"
      className={`
        relative overflow-hidden px-4 py-2 rounded-lg font-medium
        transition-colors duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-dark-900
        ${variantClasses[variant]}
        ${className}
      `}
      disabled={isDisabled}
      onClick={handleClick}
      whileHover={!isDisabled ? { scale: 1.03, y: -1, boxShadow: '0 0 28px rgba(6, 182, 212, 0.35), 0 10px 30px -10px rgba(0,0,0,0.3)' } : undefined}
      whileTap={!isDisabled ? { scale: 0.97, y: 1, boxShadow: '0 0 10px rgba(6, 182, 212, 0.15)' } : undefined}
    >
      {/* Ripple layers */}
      {ripple && ripples.map((r) => (
        <motion.span
          key={r.id}
          className="absolute rounded-full bg-white/30 pointer-events-none"
          style={{
            left: r.x,
            top: r.y,
            width: 20,
            height: 20,
            x: -10,
            y: -10,
          }}
          initial={{ scale: 0, opacity: 1 }}
          animate={{ scale: 15, opacity: 0 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
        />
      ))}

      {loading ? (
        <span className="inline-flex items-center gap-2">
          <motion.span
            animate={{ rotate: 360 }}
            transition={{ repeat: Infinity, duration: 0.8, ease: 'linear' }}
            className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
          />
          Loading…
        </span>
      ) : success ? (
        <motion.span
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 400, damping: 20 }}
        >
          ✓ Done
        </motion.span>
      ) : (
        children
      )}
    </motion.button>
  );
}
