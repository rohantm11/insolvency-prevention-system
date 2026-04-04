interface SkeletonProps {
  className?: string;
  height?: string;
  width?: string;
  variant?: 'rect' | 'circle';
}

/**
 * Skeleton placeholder with shimmer effect for premium loading states.
 */
export default function Skeleton({
  className = '',
  height,
  width,
  variant = 'rect',
}: SkeletonProps) {
  return (
    <div
      className={`skeleton-shimmer ${variant === 'circle' ? 'rounded-full' : 'rounded'} ${height || ''} ${width || ''} ${className}`}
      aria-hidden
    />
  );
}

/** Skeleton for a stat card: icon area + two lines of text */
export function SkeletonStatCard() {
  return (
    <div className="stat-card space-y-3">
      <div className="flex items-center gap-3">
        <Skeleton className="h-10 w-10 rounded-lg" variant="rect" />
        <Skeleton className="h-4 w-24" />
      </div>
      <Skeleton className="h-8 w-16" />
      <Skeleton className="h-3 w-20" />
    </div>
  );
}

/** Skeleton for a table row */
export function SkeletonTableRow({ columns = 5 }: { columns?: number }) {
  return (
    <tr>
      {Array.from({ length: columns }).map((_, i) => (
        <td key={i} className="px-4 py-3">
          <Skeleton className="h-4 w-full" />
        </td>
      ))}
    </tr>
  );
}
