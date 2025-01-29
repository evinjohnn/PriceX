"use client"

import { useEffect, useState } from "react"
import { ProductCard } from "@/components/product-card"
import { scrapeProduct } from "@/app/actions"
import { Loader2 } from "lucide-react"
import { useSearchParams } from "next/navigation"
import { Search } from "@/components/search"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { useToast } from "@/components/ui/use-toast"

export default function SearchPage() {
  const searchParams = useSearchParams()
  const query = searchParams.get("q")
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<{
    amazon: any[]
    flipkart: any[]
  } | null>(null)
  const { toast } = useToast()

  useEffect(() => {
    async function performSearch() {
      if (!query) return

      setLoading(true)
      try {
        const data = await scrapeProduct(query)
        setResults(data)

        if (!data.amazon.length && !data.flipkart.length) {
          toast({
            title: "No results found",
            description: "Try searching for a different product",
            variant: "destructive",
          })
        }
      } catch (error: any) {
        console.error("Search failed:", error)
        toast({
          title: "Error",
          description: error.message || "Failed to perform search. Please try again.",
          variant: "destructive",
        })
      } finally {
        setLoading(false)
      }
    }

    performSearch()
  }, [query, toast])

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <Search />
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          <div>
            <h2 className="text-2xl font-bold mb-6 text-[#232F3E]">
              Amazon
              {results?.amazon && (
                <span className="text-sm font-normal text-gray-500 ml-2">({results.amazon.length} results)</span>
              )}
            </h2>
            {loading ? (
              <div className="flex items-center justify-center h-96">
                <Loader2 className="w-8 h-8 animate-spin text-[#FEBD69]" />
              </div>
            ) : (
              <ProductCard platform="amazon" products={results?.amazon} />
            )}
          </div>

          <div>
            <h2 className="text-2xl font-bold mb-6 text-[#2874F0]">
              Flipkart
              {results?.flipkart && (
                <span className="text-sm font-normal text-gray-500 ml-2">({results.flipkart.length} results)</span>
              )}
            </h2>
            {loading ? (
              <div className="flex items-center justify-center h-96">
                <Loader2 className="w-8 h-8 animate-spin text-[#2874F0]" />
              </div>
            ) : (
              <ProductCard platform="flipkart" products={results?.flipkart} />
            )}
          </div>
        </div>
      </div>
    </main>
  )
}

