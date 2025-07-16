// components/search.tsx

"use client"

import { useState, useEffect, type KeyboardEvent } from "react"
import { Command } from "cmdk"
import { SearchIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { motion } from "framer-motion"
import { useRouter, useSearchParams, usePathname } from "next/navigation"
import { useDebounce } from "@/hooks/use-debounce"
import ShinyText from "@/components/ui/text-animations/ShinyText"

export function Search() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const pathname = usePathname() // Get the current page path
  const [value, setValue] = useState(searchParams.get("q") || "")
  
  // CORRECTED: Increased debounce delay to a more comfortable 1000ms (1 second)
  const debouncedSearch = useDebounce(value, 1000);

  const handleSearch = () => {
    if (value.trim()) {
      router.push(`/search?q=${encodeURIComponent(value.trim())}`)
    }
  }

  useEffect(() => {
    // CORRECTED: Only trigger automatic search on the /search page itself.
    // On the homepage ('/'), the user must press Enter or click the button.
    const isSearchPage = pathname === '/search';
    if (isSearchPage && debouncedSearch.trim()) {
      router.push(`/search?q=${encodeURIComponent(debouncedSearch.trim())}`);
    }
  }, [debouncedSearch, router, pathname]);


  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault()
      handleSearch()
    }
  }

  return (
    <motion.div
      className="relative w-full max-w-2xl mx-auto"
      initial={{ opacity: 0, scaleX: 0 }}
      animate={{ opacity: 1, scaleX: 1 }}
      transition={{
        duration: 0.8,
        delay: 1.2,
        ease: "easeOut",
      }}
    >
      <div className="relative">
        <Command className="relative z-50 overflow-visible bg-white shadow-[0_1px_6px_rgba(32,33,36,.28)] rounded-full border-0">
          <div className="flex items-center px-6">
            <div className="flex-1 relative">
              <Command.Input
                value={value}
                onValueChange={setValue}
                onKeyDown={handleKeyDown}
                placeholder=""
                className="flex-1 h-14 px-4 text-base bg-transparent outline-none w-full"
              />
              {!value && (
                <div className="absolute left-4 top-1/2 transform -translate-y-1/2 pointer-events-none">
                  <ShinyText 
                    text="Search for products on Amazon and Flipkart..." 
                    className="text-gray-400"
                    speed={3}
                  />
                </div>
              )}
            </div>
            <Button
              onClick={handleSearch}
              size="icon"
              variant="ghost"
              className="rounded-full opacity-75 hover:opacity-100"
            >
              <SearchIcon className="h-5 w-5 text-gray-400" />
            </Button>
          </div>
        </Command>
      </div>
    </motion.div>
  )
}