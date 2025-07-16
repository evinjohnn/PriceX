// components/deal-card.tsx

"use client"

import { motion } from "framer-motion"
import { ExternalLink, Heart, Share2, Zap } from "lucide-react"
import { cn } from "@/lib/utils"

interface DealCardProps {
  deal: {
    id: string
    text: string
    created_at: string
    url: string | null
    likes: number
    retweets: number
    price: string | null
    discount: string | null
    product_name: string | null
    image_url: string | null
  }
  className?: string
}

export function DealCard({ deal, className }: DealCardProps) {
  const handleClick = () => {
    if (deal.url) {
      window.open(deal.url, '_blank', 'noopener,noreferrer')
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02, rotateY: 5 }}
      transition={{ duration: 0.3 }}
      className={cn(
        "group relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-1",
        "hover:from-purple-900 hover:via-blue-900 hover:to-slate-900",
        "transition-all duration-500",
        className
      )}
    >
      {/* Holographic border effect */}
      <div className="absolute inset-0 rounded-3xl bg-gradient-to-r from-cyan-500/20 via-purple-500/20 to-pink-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
      
      {/* Neon glow */}
      <div className="absolute inset-0 rounded-3xl bg-gradient-to-r from-cyan-400/10 via-purple-400/10 to-pink-400/10 blur-xl opacity-0 group-hover:opacity-60 transition-opacity duration-500 -z-10" />
      
      <div className="relative rounded-3xl bg-black/40 backdrop-blur-xl border border-white/10 p-6 h-full">
        <div className="flex gap-4 h-full">
          {/* Product Image */}
          <div className="flex-shrink-0">
            <motion.div
              whileHover={{ scale: 1.1, rotateZ: 5 }}
              className="relative w-20 h-20 rounded-2xl overflow-hidden bg-gradient-to-br from-purple-500/20 to-cyan-500/20 border border-white/20"
            >
              {deal.image_url ? (
                <img 
                  src={deal.image_url} 
                  alt={deal.product_name || 'Deal image'} 
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <Zap className="w-8 h-8 text-cyan-400" />
                </div>
              )}
              
              {/* Shimmer effect */}
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -skew-x-12 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
            </motion.div>
          </div>
          
          {/* Deal Content */}
          <div className="flex-1 min-w-0">
            <div className="space-y-3">
              {/* Product Name */}
              {deal.product_name && (
                <motion.h3 
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="text-lg font-bold text-white/90 line-clamp-2 leading-tight"
                >
                  {deal.product_name}
                </motion.h3>
              )}
              
              {/* Price and Discount */}
              <div className="flex items-center gap-3 flex-wrap">
                {deal.price && (
                  <motion.span 
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="px-3 py-1 rounded-full bg-gradient-to-r from-emerald-500/20 to-teal-500/20 border border-emerald-500/30 text-emerald-400 text-sm font-semibold"
                  >
                    {deal.price}
                  </motion.span>
                )}
                {deal.discount && (
                  <motion.span 
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.1 }}
                    className="px-3 py-1 rounded-full bg-gradient-to-r from-red-500/20 to-pink-500/20 border border-red-500/30 text-red-400 text-sm font-semibold"
                  >
                    {deal.discount}
                  </motion.span>
                )}
              </div>
              
              {/* Tweet Text */}
              <p className="text-gray-300 text-sm leading-relaxed line-clamp-3">
                {deal.text}
              </p>
              
              {/* Engagement Stats */}
              <div className="flex items-center gap-4 text-xs text-gray-400">
                <div className="flex items-center gap-1">
                  <Heart className="w-3 h-3" />
                  <span>{deal.likes}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Share2 className="w-3 h-3" />
                  <span>{deal.retweets}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Action Button */}
        {deal.url && (
          <motion.button
            onClick={handleClick}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="absolute top-4 right-4 p-2 rounded-full bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-blue-500/30 text-blue-400 hover:from-blue-500/30 hover:to-purple-500/30 transition-all duration-300"
          >
            <ExternalLink className="w-4 h-4" />
          </motion.button>
        )}
        
        {/* Particle effects */}
        <div className="absolute inset-0 pointer-events-none">
          {[...Array(6)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 bg-cyan-400 rounded-full opacity-0 group-hover:opacity-100"
              style={{
                top: `${Math.random() * 100}%`,
                left: `${Math.random() * 100}%`,
              }}
              animate={{
                y: [0, -20, 0],
                opacity: [0, 1, 0],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: i * 0.3,
              }}
            />
          ))}
        </div>
      </div>
    </motion.div>
  )
}