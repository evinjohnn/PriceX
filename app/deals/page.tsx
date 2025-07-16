// app/deals/page.tsx

import { Navbar } from "@/components/navbar";
import { TweetCard } from "@/components/tweet-card";
import { Toaster } from "@/components/ui/toaster";
import Silk from "@/components/ui/backgrounds/Silk";
import CurvedLoop from "@/components/ui/text-animations/CurvedLoop";

// Define the type for a single deal post
interface DealPost {
  id: string;
  text: string;
  created_at: string;
  url: string;
  likes: number;
  retweets: number;
}

// This is a React Server Component, so we can fetch data directly.
async function getDeals(): Promise<DealPost[]> {
  try {
    // Fetch from our own backend's new endpoint
    const res = await fetch('http://localhost:8000/api/deals', {
      next: { revalidate: 300 } // Revalidate data every 5 minutes
    });

    if (!res.ok) {
      console.error("Failed to fetch deals");
      return [];
    }

    return res.json();
  } catch (error) {
    console.error("Error fetching deals:", error);
    return [];
  }
}

export default async function DealsPage() {
  const deals = await getDeals();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <main className="pt-24 pb-12">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold tracking-tight text-gray-900 dark:text-white">
              Latest Deals & Price Drops
            </h1>
            <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">
              Hot deals curated from @dealztrends on X.
            </p>
          </div>

          {deals.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {deals.map(deal => (
                <TweetCard key={deal.id} deal={deal} />
              ))}
            </div>
          ) : (
            <div className="text-center mt-16">
              <h2 className="text-2xl font-bold mb-2 dark:text-white">Could Not Load Deals</h2>
              <p className="text-gray-500 dark:text-gray-400">
                There was a problem fetching the latest deals. Please try again later.
              </p>
            </div>
          )}
        </div>
      </main>
      <Toaster />
    </div>
  );
}