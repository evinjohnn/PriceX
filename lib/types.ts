export interface Product {
  name: string
  image: string
  price: string
  rating: string
  reviews: string
  url: string
  platform: "amazon" | "flipkart"
}

export interface ScrapingResponse {
  amazon: Product[]
  flipkart: Product[]
}

