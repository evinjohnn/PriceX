import { Inter } from "next/font/google"
import localFont from "next/font/local"
import "./globals.css"
import { LoadingProvider } from "@/context/loading-context"

const inter = Inter({ subsets: ["latin"] })

const customLogoFont = localFont({
  src: "../fonts/font.woff2",
  variable: "--font-logo",
  display: "swap",
  fallback: ["system-ui", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "Arial", "sans-serif"],
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

