// components/navbar.tsx

"use client"

import Link from "next/link"
import { cn } from "@/lib/utils"
import { usePathname } from "next/navigation"
import { motion } from "framer-motion"
import TextPressure from "@/components/ui/text-animations/TextPressure" // Corrected: Default import

const navigation = [
  { name: "Home", href: "/" },
  { name: "Deals", href: "/deals" },
  { name: "About", href: "https://evinjohn.vercel.app/" },
]

export function Navbar() {
  const pathname = usePathname()

  return (
    <header className="fixed top-0 left-0 right-0 pt-6 pb-2 z-50 pointer-events-none">
      <nav className="absolute left-1/2 top-8 -translate-x-1/2 pointer-events-auto">
        <div className="flex items-center justify-center px-10 py-2 bg-white/5 backdrop-blur-xl border border-white/20 rounded-full shadow-lg shadow-black/5 hover:bg-white/15 hover:border-white/30 transition-all duration-300 ease-out mx-auto scale-125">
          <div className="flex items-center space-x-8 justify-center">
            {/* Navigation links */}
            <div className="flex items-center space-x-4">
              {navigation.map((item, index) => (
                <motion.div
                  key={item.name}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * index, duration: 0.5 }}
                >
                  <Link
                    href={item.href}
                    className={cn(
                      "relative px-3 py-1.5 text-sm font-medium transition-all duration-300 rounded-full text-white",
                      "hover:text-blue-200 hover:scale-105",
                      pathname === item.href
                        ? "text-blue-200"
                        : "text-white hover:bg-white/10"
                    )}
                  >
                    {item.name}
                    {pathname === item.href && (
                      <motion.div
                        layoutId="navbar-active"
                        className="absolute inset-0 bg-gradient-to-r from-blue-400/20 to-purple-400/20 rounded-full -z-10"
                        initial={false}
                        transition={{ type: "spring", stiffness: 300, damping: 30 }}
                      />
                    )}
                  </Link>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
        
        {/* Subtle glow effect */}
        <div className="absolute inset-0 bg-gradient-to-r from-blue-400/10 via-purple-400/10 to-pink-400/10 rounded-full blur-xl -z-10 opacity-60" />
      </nav>
    </header>
  )
}