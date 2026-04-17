import React from 'react';
import { motion, useMotionValue, useMotionTemplate } from 'motion/react';
import { cn } from '@/src/lib/utils';

interface GlowCardProps {
  children: React.ReactNode;
  className?: string;
  glowColor?: 'orange' | 'red' | 'green' | 'blue' | 'saffron';
  intensity?: 'low' | 'medium' | 'high';
}

export function GlowCard({
  children,
  className,
  glowColor = 'orange',
  intensity = 'medium',
}: GlowCardProps) {
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  function handleMouseMove({ currentTarget, clientX, clientY }: React.MouseEvent) {
    const { left, top } = currentTarget.getBoundingClientRect();
    mouseX.set(clientX - left);
    mouseY.set(clientY - top);
  }

  const glowColors = {
    orange: 'rgba(255, 122, 0, 0.15)',
    red: 'rgba(239, 68, 68, 0.15)',
    green: 'rgba(34, 197, 94, 0.15)',
    blue: 'rgba(59, 130, 246, 0.15)',
    saffron: 'rgba(255, 153, 51, 0.15)',
  };

  const intensities = {
    low: '250px',
    medium: '400px',
    high: '600px',
  };

  const selectedGlow = glowColors[glowColor];
  const selectedSize = intensities[intensity];

  return (
    <div
      onMouseMove={handleMouseMove}
      className={cn(
        'group relative rounded-2xl border border-card-border bg-card p-6 transition-all hover:scale-[1.01] shadow-lg overflow-hidden will-change-transform',
        className
      )}
    >
      <motion.div
        className="pointer-events-none absolute -inset-px rounded-2xl opacity-0 transition duration-300 group-hover:opacity-100 will-change-[background]"
        style={{
          background: useMotionTemplate`
            radial-gradient(
              ${selectedSize} circle at ${mouseX}px ${mouseY}px,
              ${selectedGlow},
              transparent 80%
            )
          `,
        }}
      />
      <div className="relative z-10">{children}</div>
    </div>
  );
}
