import Image from "next/image"
import { Star } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

interface Product {
  name: string
  image: string
  price: string
  rating: string
  reviews: string
  url: string
}

interface ProductCardProps {
  platform: "amazon" | "flipkart"
  products: Product[] | null
}

export function ProductCard({ platform, products }: ProductCardProps) {
  if (!products || products.length === 0) {
    return (
      <Card className={`p-6 ${platform === "amazon" ? "bg-[#FEBD69]/10" : "bg-[#2874F0]/10"}`}>
        <p className="text-center text-gray-500">No products found</p>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {products.map((product, index) => (
        <Card key={index} className={`p-6 ${platform === "amazon" ? "bg-[#FEBD69]/10" : "bg-[#2874F0]/10"}`}>
          <div className="flex gap-4">
            <div className="w-32 h-32 relative rounded-lg overflow-hidden flex-shrink-0">
              <Image src={product.image || "/placeholder.svg"} alt={product.name} fill className="object-cover" />
            </div>

            <div className="flex-1">
              <div className="flex items-center gap-1 mb-2">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Star
                    key={i}
                    className={`w-4 h-4 ${
                      i < Number.parseFloat(product.rating || "0")
                        ? "fill-yellow-400 text-yellow-400"
                        : "fill-gray-200 text-gray-200"
                    }`}
                  />
                ))}
                <span className="text-sm text-gray-600 ml-2">{product.reviews}</span>
              </div>

              <h3 className="font-semibold text-lg mb-2 line-clamp-2">{product.name}</h3>

              <p className="text-2xl font-bold mb-4">₹{product.price}</p>

              <Button
                className={platform === "amazon" ? "bg-[#FEBD69] hover:bg-[#F3A847] text-black" : "bg-[#2874F0]"}
                onClick={() => window.open(product.url, "_blank")}
              >
                View on {platform === "amazon" ? "Amazon" : "Flipkart"}
              </Button>
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}

