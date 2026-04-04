import { useEffect, useRef, useState } from 'react';

interface Particle {
  bx: number; by: number; bz: number;
  vx: number; vy: number; vz: number;
  color: string; opacity: number;
}

const COLORS = { solvent: '#00e5a0', stressed: '#ffb340', insolvent: '#ff3b5c' };
const COUNT = 8000;
const FOCAL = 400;

export default function LandingBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [mounted, setMounted] = useState(false);
  const mouse = useRef({ x: 0, y: 0 });

  useEffect(() => {
    setMounted(true);
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let W = 0, H = 0;
    let particles: Particle[] = [];
    let raf: number;

    function init() {
      const dpr = window.devicePixelRatio || 1;
      const fullHeight = document.documentElement.scrollHeight;
      W = window.innerWidth;
      H = fullHeight;
      canvas!.width = W * dpr;
      canvas!.height = H * dpr;
      canvas!.style.width = W + 'px';
      canvas!.style.height = H + 'px';
      ctx!.scale(dpr, dpr);

      particles = Array.from({ length: COUNT }, (_, i) => {
        const color = i < 2666 ? '#00e5a0' : i < 5333 ? '#ffb340' : '#ff3b5c';
        return {
          bx: Math.random() * W,
          by: Math.random() * H,
          bz: (Math.random() - 0.5) * 600,
          vx: (Math.random() - 0.5) * 0.06,
          vy: (Math.random() - 0.5) * 0.06,
          vz: (Math.random() - 0.5) * 0.06,
          color,
          opacity: Math.random() * 0.35 + 0.15,
        };
      });
    }

    function draw() {
      ctx!.clearRect(0, 0, W, H);

      const mx = mouse.current.x;
      const my = mouse.current.y;
      const viewportH = window.innerHeight;
      const rotX = ((my / viewportH) - 0.5) * 0.06;
      const rotY = ((mx / W) - 0.5) * 0.06;

      for (const p of particles) {
        p.bx += p.vx; p.by += p.vy; p.bz += p.vz;
        if (p.bx < 0 || p.bx > W) p.vx *= -1;
        if (p.by < 0 || p.by > H) p.vy *= -1;
        if (p.bz < -400 || p.bz > 400) p.vz *= -1;

        const scale = FOCAL / (FOCAL + p.bz);
        const sx = (p.bx - W / 2) * scale + W / 2;
        const sy = (p.by - H / 2) * scale + H / 2;

        // apply mouse rotation
        const dx = sx - W / 2;
        const dy = sy - H / 2;
        const rx = dx * Math.cos(rotY) - dy * Math.sin(rotX);
        const ry = dy * Math.cos(rotX) + dx * Math.sin(rotY);
        const fx = rx + W / 2;
        const fy = ry + H / 2;

        const r = Math.max(0.3, 1.1 * scale);
        const alpha = Math.max(0.08, Math.min(0.55, p.opacity * scale));

        ctx!.beginPath();
        ctx!.arc(fx, fy, r, 0, Math.PI * 2);
        ctx!.fillStyle = p.color;
        ctx!.globalAlpha = alpha;
        ctx!.fill();
      }

      ctx!.globalAlpha = 1;

      raf = requestAnimationFrame(draw);
    }

    const onResize = () => init();
    const onMouse = (e: MouseEvent) => { mouse.current.x = e.clientX; mouse.current.y = e.clientY; };

    window.addEventListener('resize', onResize);
    window.addEventListener('mousemove', onMouse);

    init();
    draw();

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener('resize', onResize);
      window.removeEventListener('mousemove', onMouse);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'absolute',
        inset: 0,
        zIndex: 0,
        pointerEvents: 'none',
        opacity: mounted ? 1 : 0,
        transition: 'opacity 1.2s ease-out',
      }}
    />
  );
}
