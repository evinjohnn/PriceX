// lib/types.ts
export interface Product {
  name: string
  image: string
  price: string // Keeping as string since we cleaned it up
  rating: string
  reviews: string
  url: string
  platform: "amazon" | "flipkart"
}

// You can remove ScrapingResponse if you define it directly in the search page