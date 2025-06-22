"use client"

import { useEffect, useState, useCallback, useRef } from "react"
import { motion } from "framer-motion"
import { scrapeProduct } from "@/app/actions"
import { Loader2, SearchX } from "lucide-react"
import { useSearchParams } from "next/navigation"
import { Search } from "@/components/search"
import { Toaster } from "@/components/ui/toaster"
import { useToast } from "@/hooks/use-toast"
import { Product } from "@/lib/types"
import { ProductCard } from "@/components/product-card"
import { Navbar } from "@/components/navbar"

interface SearchResults {
    amazon: Product[];
    flipkart: Product[];
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
        console.log(`Polling for query: "${searchQuery}"`);
        stopPolling();

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
            } catch (error) { stopPolling(); }
        }, 3000);

        setTimeout(() => {
            stopPolling();
            setLoading(false);
        }, 45000);

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
    
    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: { staggerChildren: 0.1 }
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
            <Navbar />
            <main className="pt-24 pb-12">
                <div className="container mx-auto px-4">
                    <motion.div 
                        className="max-w-3xl mx-auto mb-12"
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                    >
                        <Search />
                        {query && <h1 className="text-center text-2xl font-bold mt-4 dark:text-white">Results for "{query}"</h1>}
                    </motion.div>
                    
                    {loading && !hasResults && (
                         <div className="flex flex-col items-center justify-center text-center mt-16">
                            <Loader2 className="w-12 h-12 animate-spin text-blue-500 mb-4" />
                            <p className="text-lg font-semibold dark:text-gray-200">Searching for the best prices...</p>
                            <p className="text-gray-500 dark:text-gray-400">This can take a moment as we check sites in real-time.</p>
                        </div>
                    )}

                    {!loading && !hasResults && (
                        <div className="text-center mt-16">
                            <SearchX className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                            <h2 className="text-2xl font-bold mb-2 dark:text-white">No Results Found</h2>
                            <p className="text-gray-500 dark:text-gray-400">We couldn't find any products for "{query}". Please try a different search term.</p>
                        </div>
                    )}
                    
                    {hasResults && (
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                            <section>
                                <div className="flex items-center justify-center mb-6">
                                    <h2 className="text-3xl font-bold text-center text-gray-800 dark:text-white">Amazon</h2>
                                </div>
                                <motion.div 
                                    className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6"
                                    variants={containerVariants}
                                    initial="hidden"
                                    animate="visible"
                                >
                                    {results.amazon.map((product, index) => <ProductCard key={`amazon-${index}`} product={product} />)}
                                </motion.div>
                            </section>
                            <section>
                                <div className="flex items-center justify-center mb-6">
                                    <h2 className="text-3xl font-bold text-center text-gray-800 dark:text-white">Flipkart</h2>
                                </div>
                                <motion.div 
                                    className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6"
                                    variants={containerVariants}
                                    initial="hidden"
                                    animate="visible"
                                >
                                    {results.flipkart.map((product, index) => <ProductCard key={`flipkart-${index}`} product={product} />)}
                                </motion.div>
                            </section>
                        </div>
                    )}
                </div>
            </main>
            <Toaster />
        </div>
    )
}