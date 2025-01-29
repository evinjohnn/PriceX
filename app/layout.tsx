import { Inter } from "next/font/google"
import "./globals.css"
import { LoadingProvider } from "@/context/loading-context"

const inter = Inter({ subsets: ["latin"] })

export const metadata = {
  title: "PriceX - Smart Price Comparison",
  description: "Compare prices across multiple e-commerce platforms instantly",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className={inter.className}>
        <LoadingProvider>{children}</LoadingProvider>
      </body>
    </html>
  )
}

