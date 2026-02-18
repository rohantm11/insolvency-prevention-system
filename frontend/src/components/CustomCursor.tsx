/**
 * Custom cursor: dot + ring, enlarges on interactive elements.
 */
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

const DOT_SIZE = 8;
const RING_SIZE = 32;
const DOT_SIZE_HOVER = 14;
const RING_SIZE_HOVER = 48;

export default function CustomCursor() {
  const [pos, setPos] = useState({ x: 0, y: 0 });
  const [hover, setHover] = useState(false);
  const [visible, setVisible] = useState(false);
  const [reduceMotion, setReduceMotion] = useState(false);

  useEffect(() => {
    const m = window.matchMedia('(prefers-reduced-motion: reduce)');
    setReduceMotion(m.matches);
    const fn = () => setReduceMotion(m.matches);
    m.addEventListener('change', fn);
    return () => m.removeEventListener('change', fn);
  }, []);

  useEffect(() => {
    if (visible && !reduceMotion) document.body.classList.add('cursor-none');
    else document.body.classList.remove('cursor-none');
    return () => document.body.classList.remove('cursor-none');
  }, [visible, reduceMotion]);

  useEffect(() => {
    const handleMove = (e: MouseEvent) => {
      setPos({ x: e.clientX, y: e.clientY });
      if (!visible) setVisible(true);
    };
    const handleLeave = () => setVisible(false);
    const handleOver = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      const interactive =
        target.closest('button') ||
        target.closest('a') ||
        target.closest('[data-cursor-hover]') ||
        target.closest('.btn') ||
        target.closest('input') ||
        target.closest('select') ||
        target.closest('[role="button"]');
      setHover(!!interactive);
    };

    window.addEventListener('mousemove', handleMove);
    window.addEventListener('mouseover', handleOver);
    document.body.addEventListener('mouseleave', handleLeave);

    return () => {
      window.removeEventListener('mousemove', handleMove);
      window.removeEventListener('mouseover', handleOver);
      document.body.removeEventListener('mouseleave', handleLeave);
    };
  }, [visible]);

  if (!visible || reduceMotion) return null;

  return (
    <div
      className="fixed inset-0 pointer-events-none z-[9999]"
      aria-hidden
    >
      {/* Ring */}
      <motion.div
        className="absolute rounded-full border-2 border-primary-500/60 bg-primary-500/5"
        style={{
          left: pos.x,
          top: pos.y,
          width: hover ? RING_SIZE_HOVER : RING_SIZE,
          height: hover ? RING_SIZE_HOVER : RING_SIZE,
          x: '-50%',
          y: '-50%',
        }}
        animate={{
          scale: hover ? 1.2 : 1,
          opacity: hover ? 0.9 : 0.6,
        }}
        transition={{ type: 'spring', stiffness: 400, damping: 25 }}
      />
      {/* Dot */}
      <motion.div
        className="absolute rounded-full bg-primary-400"
        style={{
          left: pos.x,
          top: pos.y,
          width: hover ? DOT_SIZE_HOVER : DOT_SIZE,
          height: hover ? DOT_SIZE_HOVER : DOT_SIZE,
          x: '-50%',
          y: '-50%',
          boxShadow: '0 0 12px rgba(6, 182, 212, 0.6)',
        }}
        animate={{
          scale: hover ? 1.5 : 1,
        }}
        transition={{ type: 'spring', stiffness: 400, damping: 25 }}
      />
    </div>
  );
}
