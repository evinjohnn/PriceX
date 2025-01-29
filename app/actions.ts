"use server"

export async function scrapeProduct(query: string) {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_APP_URL}/api/scrape?q=${encodeURIComponent(query)}`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || "Failed to fetch products")
    }

    return await response.json()
  } catch (error) {
    console.error("Scraping failed:", error)
    throw error
  }
}

