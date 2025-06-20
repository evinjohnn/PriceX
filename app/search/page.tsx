// app/search/page.tsx

"use client"

import { useEffect, useState } from "react"
import { ProductCard } from "@/components/product-card"
import { scrapeProduct } from "@/app/actions"
import { Loader2 } from "lucide-react"
import { useSearchParams } from "next/navigation"
import { Search } from "@/components/search"
import { Toaster } from "@/components/ui/toaster" // Make sure to include the Toaster
// in app/search/page.tsx, line 10 (updated)
import { useToast } from "@/hooks/use-toast"
import { Product } from "@/lib/types"

interface SearchResults {
    amazon: Product[];
    flipkart: Product[];
}


export default function SearchPage() {
  const searchParams = useSearchParams()
  const query = searchParams.get("q")
  const [loading, setLoading] = useState(true) // Start loading immediately
  const [results, setResults] = useState<SearchResults | null>(null)
  const { toast } = useToast()

  useEffect(() => {
    async function performSearch() {
      if (!query) {
        setLoading(false)
        return
      }

      setLoading(true)
      setResults(null) // Clear previous results on new search

      try {
        const data = await scrapeProduct(query)
        setResults(data)

        if (!data?.amazon?.length && !data?.flipkart?.length) {
          toast({
            title: "No results found",
            description: `Could not find any products for "${query}". Try a different search.`,
            variant: "destructive",
          })
        }
      } catch (error: any) {
        console.error("Search failed:", error)
        // Check for specific message from our API
        const errorMessage = error.message.includes("No products found")
          ? `Could not find any products for "${query}". Try a different search.`
          : "Failed to perform search. The website might be blocking us. Please try again later."
          
        toast({
          title: "Error",
          description: errorMessage,
          variant: "destructive",
        })
        setResults({ amazon: [], flipkart: [] }) // Ensure results are not null on error
      } finally {
        setLoading(false)
      }
    }

    performSearch()
  }, [query, toast])

  return (
    <>
      <main className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="mb-8">
            <Search />
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h2 className="text-2xl font-bold mb-6 text-[#232F3E]">
                Amazon
                {results?.amazon && !loading && (
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
                {results?.flipkart && !loading && (
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
      <Toaster />
    </>
  )
}