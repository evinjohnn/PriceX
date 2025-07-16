// components/ui/scroll-stack.tsx

"use client"

import { cn } from "@/lib/utils"
import { motion, useScroll, useTransform } from "framer-motion"
import { ReactNode, useRef } from "react"

interface ScrollStackProps {
  children: ReactNode[]
  className?: string
}

export function ScrollStack({ children, className }: ScrollStackProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"]
  })

  return (
    <div ref={containerRef} className={cn("relative", className)}>
      {children.map((child, index) => {
        const start = 0
        const end = (index + 1) / children.length
        
        return (
          <Card 
            key={index} 
            i={index} 
            progress={scrollYProgress} 
            range={[start, end]}
            targetScale={0.85}
          >
            {child}
          </Card>
        )
      })}
    </div>
  )
}

interface CardProps {
  i: number
  progress: any
  range: [number, number]
  targetScale: number
  children: ReactNode
}

const Card = ({ i, progress, range, targetScale, children }: CardProps) => {
  const scale = useTransform(progress, range, [1, targetScale])
  const y = useTransform(progress, range, [0, -200])
  const top = `${i * 30}px`;

  return (
    <motion.div
      style={{
        scale,
        y,
        top,
        rotate: 0,
        filter: 'blur(0px)'
      }}
      className="sticky h-screen flex items-center justify-center z-30"
    >
      <div className="w-full max-w-2xl bg-white/10 backdrop-blur-xl border border-white/20 rounded-3xl shadow-lg shadow-black/10 p-0">
        {children}
      </div>
    </motion.div>
  )
}