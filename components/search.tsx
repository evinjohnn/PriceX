"use client"

import { useState, useEffect, type KeyboardEvent } from "react"
import { Command } from "cmdk"
import { SearchIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { motion } from "framer-motion"
import { useRouter, useSearchParams } from "next/navigation"
import { useDebounce } from "@/hooks/use-debounce" // <-- Import the hook

export function Search() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [value, setValue] = useState(searchParams.get("q") || "")
  
  // Use the debounce hook with a 500ms delay
  const debouncedSearch = useDebounce(value, 500);

  const handleSearch = () => {
    if (value.trim()) {
      router.push(`/search?q=${encodeURIComponent(value.trim())}`)
    }
  }

  useEffect(() => {
    // Only trigger search when the debounced value changes and is not empty
    if (debouncedSearch.trim()) {
      router.push(`/search?q=${encodeURIComponent(debouncedSearch.trim())}`);
    }
  }, [debouncedSearch, router]);


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
            <Command.Input
              value={value}
              onValueChange={setValue}
              onKeyDown={handleKeyDown}
              placeholder="Search for products on Amazon and Flipkart..."
              className="flex-1 h-14 px-4 text-base bg-transparent outline-none placeholder:text-gray-400"
            />
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