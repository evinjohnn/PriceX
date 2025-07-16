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
        const start = index / children.length
        const end = (index + 1) / children.length
        
        return (
          <Card 
            key={index} 
            i={index} 
            progress={scrollYProgress} 
            range={[start, end]}
            targetScale={1 - ((children.length - index) * 0.05)}
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
  const y = useTransform(progress, range, [0, -25])

  return (
    <motion.div
      style={{
        scale,
        y,
        top: `calc(-5vh + ${i * 25}px)`,
      }}
      className="sticky h-screen flex items-center justify-center"
    >
      {children}
    </motion.div>
  )
}