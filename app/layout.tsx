import { Inter } from "next/font/google"
import "./globals.css"
import { LoadingProvider } from "@/context/loading-context"
import dynamic from "next/dynamic"

const inter = Inter({ subsets: ["latin"] })

// Using system font for logo until custom font is provided
const customLogoFont = {
  variable: "--font-logo",
}

export const metadata = {
  title: "PriceX - Smart Price Comparison",
  description: "Compare prices across multiple e-commerce platforms instantly",
}

const FluidGlass = dynamic(() => import("@/components/FluidGlass/FluidGlass"), { ssr: false })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`scroll-smooth ${customLogoFont.variable}`}>
      <body className={inter.className}>
        {/* 3D FluidGlass cursor-following effect overlay */}
        <div style={{ height: "100vh", width: "100vw", position: "fixed", top: 0, left: 0, pointerEvents: "none", zIndex: 9999 }}>
          <FluidGlass
            mode="lens"
            lensProps={{
              scale: 0.25,
              ior: 1.15,
              thickness: 5,
              chromaticAberration: 0.1,
              anisotropy: 0.01
            }}
          />
        </div>
        <LoadingProvider>{children}</LoadingProvider>
      </body>
    </html>
  )
}

