import { Inter } from "next/font/google"
import localFont from "next/font/local"
import "./globals.css"
import { LoadingProvider } from "@/context/loading-context"

const inter = Inter({ subsets: ["latin"] })

const customLogoFont = localFont({
  src: [
    {
      path: "../fonts/font.woff2",
      weight: "100 900",
      style: "normal",
    },
  ],
  variable: "--font-logo",
  display: "swap",
  fallback: ["system-ui", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "Arial", "sans-serif"],
  preload: false, // Don't preload since we're using a placeholder
})

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
    <html lang="en" className={`scroll-smooth ${customLogoFont.variable}`}>
      <body className={inter.className}>
        <LoadingProvider>{children}</LoadingProvider>
      </body>
    </html>
  )
}

