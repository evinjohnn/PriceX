"use client"

import { useEffect, useState, useCallback, useRef } from "react"
import Image from "next/image"
import { scrapeProduct } from "@/app/actions"
import { Loader2, SearchX } from "lucide-react"
import { useSearchParams } from "next/navigation"
import { Search } from "@/components/search"
import { Toaster } from "@/components/ui/toaster"
import { useToast } from "@/hooks/use-toast"
import { Product } from "@/lib/types"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Navbar } from "@/components/navbar"

interface SearchResults {
    amazon: Product[];
    flipkart: Product[];
}

// A new ProductCard component tailored for the search page
function SearchProductCard({ product }: { product: Product }) {
    return (
        <Card className="p-4 flex flex-col items-center text-center transition-all duration-300 hover:shadow-lg">
            <div className="relative w-40 h-40 mb-4">
                <Image
                    src={product.image || "/placeholder.svg"}
                    alt={product.name}
                    fill
                    className="object-contain"
                />
            </div>
            <h3 className="font-semibold text-md leading-tight mb-2 line-clamp-3 h-[60px]">{product.name}</h3>
            <p className="text-2xl font-bold text-gray-800 mb-4">₹{product.price}</p>
            <Button 
                onClick={() => window.open(product.url, "_blank")}
                className={product.platform === 'amazon' ? 'bg-[#FF9900] hover:bg-[#FFAA22] text-black' : 'bg-[#2874F0] hover:bg-[#4A85F6]'}
            >
                View on {product.platform.charAt(0).toUpperCase() + product.platform.slice(1)}
            </Button>
        </Card>
    );
}

export default function SearchPage() {
    const searchParams = useSearchParams();
    const query = searchParams.get("q");
    const [loading, setLoading] = useState(true);
    const [results, setResults] = useState<SearchResults>({ amazon: [], flipkart: [] });
    const { toast } = useToast();
    const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

    const stopPolling = useCallback(() => {
        if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
        }
    }, []);

    const pollResults = useCallback((searchQuery: string) => {
        console.log(`Polling for results for query: "${searchQuery}"`);
        stopPolling(); // Stop any previous polling

        pollingIntervalRef.current = setInterval(async () => {
            try {
                const res = await fetch(`http://localhost:8000/results?q=${encodeURIComponent(searchQuery)}`);
                if (res.status === 200) {
                    const data = await res.json();
                    if (data.amazon.length > 0 || data.flipkart.length > 0) {
                        setResults(data);
                    }
                } else if (res.status !== 202) {
                    stopPolling();
                }
            } catch (error) {
                stopPolling();
            }
        }, 3000);

        setTimeout(() => {
            stopPolling();
            setLoading(false);
            toast({ title: "Search Complete", description: "All scraping jobs have finished." });
        }, 45000); // Poll for a total of 45 seconds

    }, [toast, stopPolling]);

    useEffect(() => {
        if (query) {
            setLoading(true);
            setResults({ amazon: [], flipkart: [] });
            scrapeProduct(query)
                .then(res => {
                    toast({ title: "Search Started", description: res.message });
                    pollResults(query);
                })
                .catch(err => {
                    toast({ title: "Error", description: err.message, variant: "destructive" });
                    setLoading(false);
                });
        } else {
            setLoading(false);
        }
        return () => stopPolling();
    }, [query, toast, pollResults, stopPolling]);

    const hasResults = results.amazon.length > 0 || results.flipkart.length > 0;

    return (
        <>
            <Navbar />
            <main className="min-h-screen bg-gray-50 pt-24">
                <div className="container mx-auto px-4 py-8">
                    <div className="max-w-3xl mx-auto mb-12">
                        <Search />
                    </div>
                    
                    {loading && (
                         <div className="flex flex-col items-center justify-center text-center">
                            <Loader2 className="w-12 h-12 animate-spin text-blue-500 mb-4" />
                            <p className="text-lg font-semibold">Searching for the best prices...</p>
                            <p className="text-gray-500">This can take a moment as we check sites in real-time.</p>
                        </div>
                    )}

                    {!loading && !hasResults && (
                        <div className="text-center">
                            <SearchX className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                            <h2 className="text-2xl font-bold mb-2">No Results Found</h2>
                            <p className="text-gray-500">We couldn't find any products for "{query}". Please try a different search term.</p>
                        </div>
                    )}
                    
                    {hasResults && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                            <div>
                                <h2 className="text-3xl font-bold mb-6 text-center text-gray-800">Amazon</h2>
                                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                                    {results.amazon.map((product, index) => <SearchProductCard key={`amazon-${index}`} product={product} />)}
                                </div>
                            </div>
                            <div>
                            <h2 className="text-3xl font-bold mb-6 text-center text-gray-800">Flipkart</h2>
                                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                                    {results.flipkart.map((product, index) => <SearchProductCard key={`flipkart-${index}`} product={product} />)}
                                </div>
                            </div>
                        </div>
                    )}

                </div>
            </main>
            <Toaster />
        </>
    )
}