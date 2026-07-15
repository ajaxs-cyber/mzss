import { useRef, type ReactNode, type MouseEvent } from 'react';

interface LiquidGlassProps {
  children: ReactNode;
  className?: string;
  strong?: boolean;
}

export default function LiquidGlass({
  children,
  className = '',
  strong = false,
}: LiquidGlassProps) {
  const elRef = useRef<HTMLDivElement>(null);

  function handleMouseMove(e: MouseEvent<HTMLDivElement>) {
    const el = elRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    el.style.setProperty('--x', `${x}px`);
    el.style.setProperty('--y', `${y}px`);
    el.style.setProperty(
      '--angle',
      `${(Math.atan2(y - rect.height / 2, x - rect.width / 2) * 180) / Math.PI}deg`
    );
  }

  return (
    <div
      ref={elRef}
      className={`${strong ? 'liquid-glass-strong' : 'liquid-glass'} ${className}`}
      onMouseMove={handleMouseMove}
    >
      {children}
    </div>
  );
}
