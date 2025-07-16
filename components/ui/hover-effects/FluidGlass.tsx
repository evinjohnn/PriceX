"use client"

import React, { ReactNode, useRef, useEffect, useState } from 'react';

interface FluidGlassProps {
  children: ReactNode;
  className?: string;
  intensity?: number;
  speed?: number;
  disabled?: boolean;
}

const FluidGlass: React.FC<FluidGlassProps> = ({
  children,
  className = '',
  intensity = 0.5,
  speed = 0.3,
  disabled = false
}) => {
  const elementRef = useRef<HTMLDivElement>(null);
  const [isHovered, setIsHovered] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const element = elementRef.current;
    if (!element || disabled) return;

    const handleMouseMove = (e: MouseEvent) => {
      const rect = element.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      setMousePosition({ x, y });
    };

    const handleMouseEnter = () => {
      setIsHovered(true);
    };

    const handleMouseLeave = () => {
      setIsHovered(false);
    };

    element.addEventListener('mousemove', handleMouseMove);
    element.addEventListener('mouseenter', handleMouseEnter);
    element.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      element.removeEventListener('mousemove', handleMouseMove);
      element.removeEventListener('mouseenter', handleMouseEnter);
      element.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, [disabled]);

  const glassStyle = {
    position: 'relative' as const,
    overflow: 'hidden' as const,
    transition: `all ${speed}s ease-out`,
    transform: isHovered && !disabled ? 'scale(1.02)' : 'scale(1)',
    backdropFilter: isHovered && !disabled ? 'blur(1px)' : 'blur(0px)',
    background: isHovered && !disabled 
      ? `radial-gradient(circle at ${mousePosition.x}% ${mousePosition.y}%, rgba(255, 255, 255, ${intensity * 0.1}) 0%, rgba(255, 255, 255, ${intensity * 0.05}) 50%, transparent 100%)`
      : 'transparent',
  };

  const overlayStyle = {
    position: 'absolute' as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    pointerEvents: 'none' as const,
    opacity: isHovered && !disabled ? intensity : 0,
    transition: `opacity ${speed}s ease-out`,
    background: `radial-gradient(circle at ${mousePosition.x}% ${mousePosition.y}%, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 30%, transparent 70%)`,
    mixBlendMode: 'overlay' as const,
  };

  return (
    <div 
      ref={elementRef}
      className={`fluid-glass ${className}`}
      style={glassStyle}
    >
      <div style={overlayStyle} />
      {children}
    </div>
  );
};

export default FluidGlass;