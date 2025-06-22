import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Product } from "@/lib/types"
import { motion } from "framer-motion"

export function ProductCard({ product }: { product: Product }) {
  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <motion.div variants={cardVariants}>
      <Card className="p-4 flex flex-col items-center text-center transition-all duration-300 hover:shadow-xl hover:-translate-y-1 h-full">
          <div className="relative w-40 h-40 mb-4">
              <Image
                  src={product.image || "/placeholder.svg"}
                  alt={product.name}
                  fill
                  className="object-contain"
              />
          </div>
          <div className="flex-grow flex flex-col">
            <h3 className="font-semibold text-md leading-tight mb-2 line-clamp-3 flex-grow">{product.name}</h3>
            <p className="text-2xl font-bold text-gray-800 my-2">₹{product.price}</p>
          </div>
          <Button 
              onClick={() => window.open(product.url, "_blank")}
              className={`mt-4 w-full ${product.platform === 'amazon' 
                  ? 'bg-[#FF9900] hover:bg-[#FFAA22] text-black' 
                  : 'bg-[#2874F0] hover:bg-[#4A85F6]'}`}
          >
              View on {product.platform.charAt(0).toUpperCase() + product.platform.slice(1)}
          </Button>
      </Card>
    </motion.div>
  );
}