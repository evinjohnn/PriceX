"use client"

import { createContext, useContext, useState, useEffect } from "react"

interface LoadingContextType {
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

const LoadingContext = createContext<LoadingContextType>({
  isLoading: true,
  setIsLoading: () => {},
})

export function LoadingProvider({ children }: { children: React.ReactNode }) {
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 2000) // Show loading state for 2 seconds

    return () => clearTimeout(timer)
  }, [])

  return <LoadingContext.Provider value={{ isLoading, setIsLoading }}>{children}</LoadingContext.Provider>
}

export const useLoading = () => useContext(LoadingContext)

