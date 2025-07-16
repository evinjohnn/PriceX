// components/navbar.tsx

"use client"

import Link from "next/link"
import { cn } from "@/lib/utils"
import { usePathname } from "next/navigation"
import { motion } from "framer-motion"

const navigation = [
  { name: "Home", href: "/" },
  { name: "Search", href: "/search" },
  { name: "Deals", href: "/deals" },
]

export function Navbar() {
  const pathname = usePathname()

  return (
    <header className="w-full flex justify-center items-start pt-6 pb-2 z-50">
      <nav className="relative">
        <div className="
          flex items-center justify-center px-8 py-3 
          bg-white/10 backdrop-blur-xl border border-white/20 
          rounded-full shadow-lg shadow-black/5
          hover:bg-white/15 hover:border-white/30
          transition-all duration-300 ease-out
        ">
          <div className="flex items-center space-x-8">
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
                    "relative px-4 py-2 text-sm font-medium transition-all duration-300 rounded-full",
                    "hover:text-blue-600 hover:scale-105",
                    pathname === item.href 
                      ? "text-blue-600 bg-white/20 shadow-sm" 
                      : "text-gray-700 hover:bg-white/10"
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
        
        {/* Subtle glow effect */}
        <div className="absolute inset-0 bg-gradient-to-r from-blue-400/10 via-purple-400/10 to-pink-400/10 rounded-full blur-xl -z-10 opacity-60" />
      </nav>
    </header>
  )
}