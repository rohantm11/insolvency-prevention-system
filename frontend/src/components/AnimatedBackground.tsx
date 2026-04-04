import { useEffect, useRef } from 'react';

const NODES_COUNT = 28;
const GRID_SPACING = 48;
const DOT_RADIUS = 0.8;
const DOT_COLOR = 'rgba(0,200,212,0.045)';
const CONNECT_THRESHOLD = 220;
const CONNECT_OPACITY_FACTOR = 0.18;
const CONNECT_STROKE = '#00c8d4';
const CONNECT_LINEWIDTH = 0.7;
const PULSE_SPAWN_INTERVAL = 45;
const PULSE_GLOW_RADIUS = 10;
const PULSE_CORE_RADIUS = 2.5;

function getRiskColor(risk: number): string {
  if (risk < 0.35) return '#00e5a0';
  if (risk < 0.62) return '#ffb340';
  return '#ff3b5c';
}

/** Quadratic bezier: B(t) = (1-t)²P0 + 2(1-t)tP1 + t²P2 */
function bezierPoint(
  x0: number, y0: number,
  x1: number, y1: number,
  x2: number, y2: number,
  t: number
): { x: number; y: number } {
  const u = 1 - t;
  const uu = u * u;
  const tt = t * t;
  const ut2 = 2 * u * t;
  return {
    x: uu * x0 + ut2 * x1 + tt * x2,
    y: uu * y0 + ut2 * y1 + tt * y2,
  };
}

type Node = {
  x: number;
  y: number;
  vx: number;
  vy: number;
  risk: number;
  riskDrift: number;
};

type Pulse = {
  t: number;
  color: string;
  x0: number;
  y0: number;
  cpx: number;
  cpy: number;
  x2: number;
  y2: number;
};

function initNodes(width: number, height: number): Node[] {
  const nodes: Node[] = [];
  for (let i = 0; i < NODES_COUNT; i++) {
    nodes.push({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.8,
      vy: (Math.random() - 0.5) * 0.8,
      risk: Math.random(),
      riskDrift: (Math.random() - 0.5) * 0.002,
    });
  }
  return nodes;
}

function drawDotGrid(ctx: CanvasRenderingContext2D, width: number, height: number) {
  ctx.fillStyle = DOT_COLOR;
  for (let x = 0; x <= width + GRID_SPACING; x += GRID_SPACING) {
    for (let y = 0; y <= height + GRID_SPACING; y += GRID_SPACING) {
      ctx.beginPath();
      ctx.arc(x, y, DOT_RADIUS, 0, Math.PI * 2);
      ctx.fill();
    }
  }
}

function drawConnections(ctx: CanvasRenderingContext2D, nodes: Node[]) {
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i];
      const b = nodes[j];
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const dist = Math.hypot(dx, dy);
      if (dist > CONNECT_THRESHOLD) continue;
      const opacity = (1 - dist / CONNECT_THRESHOLD) * CONNECT_OPACITY_FACTOR;
      const cx = (a.x + b.x) / 2;
      const cy = (a.y + b.y) / 2;
      const nx = -dy / dist;
      const ny = dx / dist;
      const offset = Math.min(40, dist * 0.2);
      const cpx = cx + nx * offset;
      const cpy = cy + ny * offset;
      ctx.strokeStyle = CONNECT_STROKE;
      ctx.globalAlpha = opacity;
      ctx.lineWidth = CONNECT_LINEWIDTH;
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.quadraticCurveTo(cpx, cpy, b.x, b.y);
      ctx.stroke();
      ctx.globalAlpha = 1;
    }
  }
}

function drawPulseAlongBezier(ctx: CanvasRenderingContext2D, pulse: Pulse) {
  const pt = bezierPoint(
    pulse.x0, pulse.y0,
    pulse.cpx, pulse.cpy,
    pulse.x2, pulse.y2,
    pulse.t
  );

  const gradient = ctx.createRadialGradient(
    pt.x, pt.y, 0,
    pt.x, pt.y, PULSE_GLOW_RADIUS
  );
  gradient.addColorStop(0, pulse.color + '99');
  gradient.addColorStop(0.5, pulse.color + '33');
  gradient.addColorStop(1, pulse.color + '00');
  ctx.fillStyle = gradient;
  ctx.beginPath();
  ctx.arc(pt.x, pt.y, PULSE_GLOW_RADIUS, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = pulse.color;
  ctx.beginPath();
  ctx.arc(pt.x, pt.y, PULSE_CORE_RADIUS, 0, Math.PI * 2);
  ctx.fill();
}

function drawNode(
  ctx: CanvasRenderingContext2D,
  node: Node,
  time: number
) {
  const color = getRiskColor(node.risk);
  const ringScale = 1 + Math.sin(time * 0.003 + node.x * 0.01) * 0.15;
  const ringRadius = 6 * ringScale;

  const gradient = ctx.createRadialGradient(
    node.x, node.y, 0,
    node.x, node.y, ringRadius * 2
  );
  gradient.addColorStop(0, color + '66');
  gradient.addColorStop(0.5, color + '22');
  gradient.addColorStop(1, color + '00');
  ctx.fillStyle = gradient;
  ctx.beginPath();
  ctx.arc(node.x, node.y, ringRadius * 2, 0, Math.PI * 2);
  ctx.fill();

  ctx.strokeStyle = color;
  ctx.globalAlpha = 0.4 + Math.sin(time * 0.003 + node.x * 0.01) * 0.2;
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.arc(node.x, node.y, ringRadius, 0, Math.PI * 2);
  ctx.stroke();
  ctx.globalAlpha = 1;

  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(node.x, node.y, 3, 0, Math.PI * 2);
  ctx.fill();
}

export default function AnimatedBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let width = window.innerWidth;
    let height = window.innerHeight;
    let nodes = initNodes(width, height);
    let pulses: Pulse[] = [];
    let frameCount = 0;
    let rafId: number;

    function setSize() {
      canvas.width = width;
      canvas.height = height;
    }

    function getConnectedPairs(): { from: number; to: number }[] {
      const pairs: { from: number; to: number }[] = [];
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dist = Math.hypot(nodes[j].x - nodes[i].x, nodes[j].y - nodes[i].y);
          if (dist <= CONNECT_THRESHOLD) pairs.push({ from: i, to: j });
        }
      }
      return pairs;
    }

    function tick() {
      width = window.innerWidth;
      height = window.innerHeight;

      for (const node of nodes) {
        node.x += node.vx;
        node.y += node.vy;
        if (node.x <= 0 || node.x >= width) node.vx *= -1;
        if (node.y <= 0 || node.y >= height) node.vy *= -1;
        node.x = Math.max(0, Math.min(width, node.x));
        node.y = Math.max(0, Math.min(height, node.y));
        node.risk += node.riskDrift;
        if (node.risk <= 0 || node.risk >= 1) node.riskDrift *= -1;
        node.risk = Math.max(0, Math.min(1, node.risk));
      }

      frameCount++;
      if (frameCount % PULSE_SPAWN_INTERVAL === 0) {
        const pairs = getConnectedPairs();
        if (pairs.length > 0) {
          const { from, to } = pairs[Math.floor(Math.random() * pairs.length)];
          const a = nodes[from];
          const b = nodes[to];
          const dx = b.x - a.x;
          const dy = b.y - a.y;
          const dist = Math.hypot(dx, dy);
          const nx = dist ? -dy / dist : 0;
          const ny = dist ? dx / dist : 0;
          const offset = Math.min(40, dist * 0.2);
          const cpx = (a.x + b.x) / 2 + nx * offset;
          const cpy = (a.y + b.y) / 2 + ny * offset;
          const color = getRiskColor((a.risk + b.risk) / 2);
          pulses.push({
            t: 0,
            color,
            x0: a.x,
            y0: a.y,
            cpx,
            cpy,
            x2: b.x,
            y2: b.y,
          });
        }
      }

      pulses = pulses.filter((p) => {
        p.t += 0.012;
        return p.t <= 1;
      });

      ctx.clearRect(0, 0, width, height);
      drawDotGrid(ctx, width, height);
      drawConnections(ctx, nodes);
      for (const pulse of pulses) {
        drawPulseAlongBezier(ctx, pulse);
      }
      const time = performance.now();
      for (const node of nodes) {
        drawNode(ctx, node, time);
      }

      rafId = requestAnimationFrame(tick);
    }

    setSize();
    rafId = requestAnimationFrame(tick);

    const onResize = () => {
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width;
      canvas.height = height;
      nodes = initNodes(width, height);
      pulses = [];
    };
    window.addEventListener('resize', onResize);

    return () => {
      cancelAnimationFrame(rafId);
      window.removeEventListener('resize', onResize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        inset: 0,
        width: '100%',
        height: '100%',
        zIndex: 0,
        pointerEvents: 'none',
        background: 'linear-gradient(135deg, #050e1a 0%, #071524 50%, #04111e 100%)',
      }}
      aria-hidden
    />
  );
}
