"use client"

import { Navbar } from "@/components/navbar"
import { Search } from "@/components/search"
import { ShoppingCart, Shield, Zap } from "lucide-react"
import { motion } from "framer-motion"
import { cn } from "@/lib/utils"
import dynamic from "next/dynamic"
const Dither = dynamic(() => import("@/components/ui/backgrounds/Dither/Dither"), { ssr: false })

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col">
      <Navbar />
      <Dither />
      <section className="flex-1 flex flex-col items-center justify-center px-4 pb-32 pt-32 relative overflow-hidden">

        <div className="flex flex-col items-center justify-center w-full mb-0 mt-0">
          <div className="flex justify-center w-full h-28">
            <span className="font-logo text-8xl text-gray-900 dark:text-white tracking-tight select-none">PriceX</span>
          </div>
        </div>

        <Search />

        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-24 max-w-5xl mx-auto px-4"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.8 }}
        >
          {[
            {
              icon: <Zap className="h-8 w-8 transition-all duration-300 group-hover:h-11 group-hover:w-11" />,
              title: "Lightning Fast",
              description: "Get real-time price comparisons across multiple platforms instantly",
              bgColor: "bg-blue-50",
              glowColor: "group-hover:shadow-[0_0_30px_-5px_rgba(59,130,246,0.5)]",
              iconColor: "text-blue-500",
            },
            {
              icon: <ShoppingCart className="h-8 w-8 transition-all duration-300 group-hover:h-11 group-hover:w-11" />,
              title: "Best Deals",
              description: "Find the lowest prices and best deals from trusted retailers",
              bgColor: "bg-green-50",
              glowColor: "group-hover:shadow-[0_0_30px_-5px_rgba(34,197,94,0.5)]",
              iconColor: "text-green-500",
            },
            {
              icon: <Shield className="h-8 w-8 transition-all duration-300 group-hover:h-11 group-hover:w-11" />,
              title: "Trusted Reviews",
              description: "Verify authenticity with our AI-powered fake review detection",
              bgColor: "bg-purple-50",
              glowColor: "group-hover:shadow-[0_0_30px_-5px_rgba(147,51,234,0.5)]",
              iconColor: "text-purple-500",
            },
          ].map((feature, index) => (
            <motion.div
              key={index}
              className="flex flex-col items-center text-center space-y-4 group"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.8 + index * 0.1 }}
            >
              <motion.div
                className={cn("p-6 rounded-2xl transition-all duration-300", feature.bgColor, feature.glowColor)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <div className={feature.iconColor}>{feature.icon}</div>
              </motion.div>
              <h3 className="font-semibold">{feature.title}</h3>
              <p className="text-gray-500">{feature.description}</p>
            </motion.div>
          ))}
        </motion.div>
        
        {/* Bottom Curved Banner */}
      </section>
    </main>
  )
}