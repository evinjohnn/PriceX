"use client"

import Link from "next/link"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { usePathname } from "next/navigation"
import { motion } from "framer-motion"

const navigation = [
  { name: "Home", href: "/" },
  { name: "About", href: "/about" },
  { name: "Contact", href: "/contact" },
  { name: "Pricing", href: "/pricing" },
]

export function Navbar() {
  const pathname = usePathname()

  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, delay: 1.5 }}
      className="fixed top-0 w-full border-b bg-white/50 backdrop-blur-xl z-50"
    >
      <nav className="container mx-auto">
        <div className="flex h-12 items-center justify-between px-4">
          {" "}
          {/* Reduced height */}
          <div className="flex-1 flex items-center justify-start space-x-6">
            {" "}
            {/* Added flex-1 and adjusted spacing */}
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "text-sm font-medium transition-colors hover:text-gray-900",
                  pathname === item.href ? "text-gray-900" : "text-gray-500",
                )}
              >
                {item.name}
              </Link>
            ))}
          </div>
          <div className="flex items-center gap-3">
            {" "}
            {/* Reduced gap */}
            <Button variant="ghost" size="sm">
              Sign in
            </Button>
            <Button size="sm">Get Started</Button>
          </div>
        </div>
      </nav>
    </motion.header>
  )
}

