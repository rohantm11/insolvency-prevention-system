/**
 * useTilt — 3D tilt effect on hover with mouse-following spotlight.
 * Uses Framer Motion's useMotionValue + useSpring for smooth physics.
 */
import { useRef, useCallback } from 'react';
import { useMotionValue, useSpring, useTransform, type MotionStyle } from 'framer-motion';

interface UseTiltOptions {
  maxTilt?: number;    // max degrees of rotation (default 6)
  perspective?: number; // CSS perspective in px (default 800)
  scale?: number;      // hover scale (default 1.02)
  speed?: number;      // spring speed - higher = snappier
}

export default function useTilt({
  maxTilt = 6,
  perspective = 800,
  scale: hoverScale = 1.02,
  speed = 300,
}: UseTiltOptions = {}) {
  const ref = useRef<HTMLDivElement>(null);

  const x = useMotionValue(0.5);
  const y = useMotionValue(0.5);

  const springConfig = { stiffness: speed, damping: 20, mass: 0.5 };
  const xSpring = useSpring(x, springConfig);
  const ySpring = useSpring(y, springConfig);

  const rotateX = useTransform(ySpring, [0, 1], [maxTilt, -maxTilt]);
  const rotateY = useTransform(xSpring, [0, 1], [-maxTilt, maxTilt]);
  const scaleVal = useMotionValue(1);
  const scaleSpring = useSpring(scaleVal, { stiffness: 260, damping: 20 });

  // Spotlight gradient position (percentage)
  const spotlightX = useTransform(xSpring, [0, 1], [0, 100]);
  const spotlightY = useTransform(ySpring, [0, 1], [0, 100]);

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (!ref.current) return;
      const rect = ref.current.getBoundingClientRect();
      x.set((e.clientX - rect.left) / rect.width);
      y.set((e.clientY - rect.top) / rect.height);
    },
    [x, y]
  );

  const handleMouseEnter = useCallback(() => {
    scaleVal.set(hoverScale);
  }, [scaleVal, hoverScale]);

  const handleMouseLeave = useCallback(() => {
    x.set(0.5);
    y.set(0.5);
    scaleVal.set(1);
  }, [x, y, scaleVal]);

  const style: MotionStyle = {
    rotateX,
    rotateY,
    scale: scaleSpring,
    transformPerspective: perspective,
    transformStyle: 'preserve-3d' as any,
  };

  return {
    ref,
    style,
    spotlightX,
    spotlightY,
    handlers: {
      onMouseMove: handleMouseMove,
      onMouseEnter: handleMouseEnter,
      onMouseLeave: handleMouseLeave,
    },
  };
}
