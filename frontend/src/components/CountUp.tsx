/**
 * Animates a number from 0 (or from) to target value when in view. Used for "live demo" stats.
 */
import { useEffect, useState } from 'react';
import { useInView, useMotionValue, useMotionValueEvent, animate } from 'framer-motion';
import { useRef } from 'react';

interface CountUpProps {
  to: number;
  from?: number;
  suffix?: string;
  prefix?: string;
  duration?: number;
  className?: string;
  /** If true, format with locale (e.g. 1,842) */
  formatNumber?: boolean;
}

export default function CountUp({
  to,
  from = 0,
  suffix = '',
  prefix = '',
  duration = 1.2,
  className = '',
  formatNumber = false,
}: CountUpProps) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: '-50px' });
  const value = useMotionValue(from);
  const [displayValue, setDisplayValue] = useState(from);

  useMotionValueEvent(value, 'change', (v) => setDisplayValue(Math.round(v)));

  useEffect(() => {
    if (!inView) return;
    const controls = animate(value, to, {
      duration,
      ease: 'easeOut',
    });
    return () => controls.stop();
  }, [inView, to, from, duration, value]);

  const text = formatNumber
    ? displayValue.toLocaleString()
    : String(displayValue);

  return (
    <span ref={ref} className={className}>
      {prefix}{text}{suffix}
    </span>
  );
}
