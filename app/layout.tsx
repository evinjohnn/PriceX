import { Inter } from "next/font/google"
import localFont from 'next/font/local'
import "./globals.css"
import { LoadingProvider } from "@/context/loading-context"
import dynamic from "next/dynamic"
import { ThemeProvider } from "@/components/theme-provider"
import { Toaster } from "@/components/ui/toaster"

const inter = Inter({ subsets: ["latin"] })

// Correctly load the local font
const customLogoFont = localFont({
  src: './fonts/font.woff2',
  variable: '--font-logo',
})

export const metadata = {
  title: "PriceX - Smart Price Comparison",
  description: "Compare prices across multiple e-commerce platforms instantly",
}

// The FluidGlass component is causing a crash due to dependency issues
// and missing 3D model assets. It has been commented out to allow the app to run.
// const FluidGlass = dynamic(() => import("@/components/FluidGlass/FluidGlass"), { ssr: false })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} ${customLogoFont.variable}`} suppressHydrationWarning>
      <body>
        {/*
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
        */}
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <LoadingProvider>{children}</LoadingProvider>
          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  )
}