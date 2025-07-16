import { Inter } from "next/font/google"
import localFont from "next/font/local"
import "./globals.css"
import { LoadingProvider } from "@/context/loading-context"

const inter = Inter({ subsets: ["latin"] })

// Temporarily using system font until custom font is provided
const customLogoFont = {
  variable: "--font-logo",
  className: "font-logo",
}

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

