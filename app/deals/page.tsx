// app/deals/page.tsx

import { Navbar } from "@/components/navbar";
import { DealCard } from "@/components/deal-card";
import { ScrollStack } from "@/components/ui/scroll-stack";
import { Toaster } from "@/components/ui/toaster";
import SilkBackground from "@/components/ui/backgrounds/SilkBackground";

// Define the type for a single deal post
interface DealPost {
  id: string;
  text: string;
  created_at: string;
  url: string | null;
  likes: number;
  retweets: number;
  price: string | null;
  discount: string | null;
  product_name: string | null;
  image_url: string | null;
}

// Mock data for demonstration (will be replaced with real API data)
const mockDeals: DealPost[] = [
  {
    id: "1",
    text: "🔥 MASSIVE DEAL ALERT! Samsung Galaxy S24 Ultra at unbeatable price! Limited time offer - grab yours now before stock runs out! #SamsungDeal #TechDeals",
    created_at: "2024-01-15T10:30:00Z",
    url: "https://amazon.in/samsung-galaxy-s24-ultra",
    likes: 342,
    retweets: 128,
    price: "₹1,19,999",
    discount: "25% off",
    product_name: "Samsung Galaxy S24 Ultra 256GB",
    image_url: "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400&h=400&fit=crop"
  },
  {
    id: "2", 
    text: "💰 INSANE PRICE DROP! Apple MacBook Air M2 - Perfect for students and professionals. Don't miss this incredible opportunity! #MacBookDeal #AppleDeals",
    created_at: "2024-01-15T09:15:00Z",
    url: "https://flipkart.com/apple-macbook-air-m2",
    likes: 567,
    retweets: 234,
    price: "₹94,999",
    discount: "30% off",
    product_name: "Apple MacBook Air M2 13-inch",
    image_url: "https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=400&h=400&fit=crop"
  },
  {
    id: "3",
    text: "⚡ FLASH SALE ALERT! Sony WH-1000XM5 Noise Cancelling Headphones - The ultimate audio experience at an unbeatable price! #SonyHeadphones #AudioDeals",
    created_at: "2024-01-15T08:45:00Z", 
    url: "https://amazon.in/sony-wh-1000xm5-headphones",
    likes: 289,
    retweets: 91,
    price: "₹24,999",
    discount: "40% off",
    product_name: "Sony WH-1000XM5 Wireless Headphones",
    image_url: "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=400&h=400&fit=crop"
  },
  {
    id: "4",
    text: "🎮 GAMING ALERT! PlayStation 5 back in stock with exclusive bundle deals! Free games included - this won't last long! #PS5Deal #GamingDeals",
    created_at: "2024-01-15T07:20:00Z",
    url: "https://flipkart.com/playstation-5-bundle",
    likes: 1234,
    retweets: 456,
    price: "₹54,999",
    discount: "Bundle offer",
    product_name: "PlayStation 5 Console Bundle",
    image_url: "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=400&h=400&fit=crop"
  },
  {
    id: "5",
    text: "👟 SNEAKER ALERT! Nike Air Jordan 1 Retro High - Iconic style meets unbeatable comfort. Limited edition colorway available now! #NikeJordan #SneakerDeals",
    created_at: "2024-01-15T06:00:00Z",
    url: "https://amazon.in/nike-air-jordan-1-retro",
    likes: 456,
    retweets: 178,
    price: "₹12,999",
    discount: "35% off",
    product_name: "Nike Air Jordan 1 Retro High",
    image_url: "https://images.unsplash.com/photo-1584735175315-9d5df23860e6?w=400&h=400&fit=crop"
  },
  {
    id: "6",
    text: "📱 SMARTPHONE DEAL! OnePlus 12 Pro with flagship features at mid-range price! Fast charging, amazing camera, premium build quality! #OnePlusDeals #SmartphoneDeals",
    created_at: "2024-01-15T05:30:00Z",
    url: "https://flipkart.com/oneplus-12-pro",
    likes: 689,
    retweets: 267,
    price: "₹64,999",
    discount: "20% off",
    product_name: "OnePlus 12 Pro 512GB",
    image_url: "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=400&fit=crop"
  }
];

// This is a React Server Component, so we can fetch data directly.
async function getDeals(): Promise<DealPost[]> {
  try {
    // Fetch from our own backend's new endpoint
    const res = await fetch('http://localhost:8000/api/deals', {
      next: { revalidate: 300 } // Revalidate data every 5 minutes
    });

    if (!res.ok) {
      console.error("Failed to fetch deals, using mock data");
      return mockDeals;
    }

    const deals = await res.json();
    return deals.length > 0 ? deals : mockDeals;
  } catch (error) {
    console.error("Error fetching deals:", error);
    return mockDeals;
  }
}

export default async function DealsPage() {
  const deals = await getDeals();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 overflow-hidden">
      <Navbar />
      
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse delay-1000" />
        <div className="absolute top-1/2 left-1/2 w-80 h-80 bg-pink-500/10 rounded-full blur-3xl animate-pulse delay-2000" />
      </div>
      
      <SilkBackground color="#1e1b4b" speed={2} scale={3} noiseIntensity={0.6} />
      
      <main className="relative pt-32 pb-12">
        <div className="container mx-auto px-4">
          {/* Futuristic Header */}
          <div className="text-center mb-16 relative">
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-500/20 to-transparent h-px top-1/2 transform -translate-y-1/2" />
            
            <h1 className="relative inline-block text-6xl font-bold tracking-tight mb-6 bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              CYBER DEALS
            </h1>
            
            <div className="relative">
              <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto leading-relaxed">
                Curated hot deals from the future of shopping • Real-time price drops • 
                <span className="text-cyan-400"> @dealztrends</span>
              </p>
              
              {/* Stats display */}
              <div className="flex justify-center gap-8 text-sm text-gray-400">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                  <span>Live Updates</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
                  <span>{deals.length} Active Deals</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse" />
                  <span>Auto-Refresh</span>
                </div>
              </div>
            </div>
          </div>

          {/* ScrollStack Implementation */}
          {deals.length > 0 ? (
            <div className="max-w-4xl mx-auto">
              <ScrollStack>
                {deals.map((deal) => (
                  <div key={deal.id} className="w-full max-w-2xl mx-auto px-4">
                    <DealCard deal={deal} />
                  </div>
                ))}
              </ScrollStack>
            </div>
          ) : (
            <div className="text-center mt-16 relative">
              <div className="relative inline-block p-8 rounded-3xl bg-gradient-to-r from-slate-800/50 to-purple-800/50 backdrop-blur-xl border border-white/10">
                <h2 className="text-3xl font-bold mb-4 text-white">
                  No Active Deals
                </h2>
                <p className="text-gray-400 text-lg">
                  The deal matrix is currently empty. Check back soon for the latest offers.
                </p>
              </div>
            </div>
          )}
        </div>
      </main>
      
      <Toaster />
    </div>
  );
}