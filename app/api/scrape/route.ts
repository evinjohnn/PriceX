import { NextResponse } from "next/server"
import * as cheerio from "cheerio"
import { rateLimit } from "@/lib/rate-limit"
import type { Product } from "@/lib/types"

const limiter = rateLimit({
  interval: 60 * 1000,
  uniqueTokenPerInterval: 500,
})

// Add proxy support for production
const PROXY_URL = process.env.PROXY_URL
const USE_PROXY = process.env.NODE_ENV === "production"

const headers = {
  "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
  Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
  "Accept-Language": "en-US,en;q=0.5",
  Connection: "keep-alive",
}

export async function GET(request: Request) {
  try {
    await limiter.check(5, "CACHE_TOKEN")

    const { searchParams } = new URL(request.url)
    const query = searchParams.get("q")

    if (!query) {
      return NextResponse.json({ error: "Query parameter is required" }, { status: 400 })
    }

    const [amazonProducts, flipkartProducts] = await Promise.allSettled([
      fetchAmazonProducts(query),
      fetchFlipkartProducts(query),
    ])

    const results = {
      amazon: amazonProducts.status === "fulfilled" ? amazonProducts.value : [],
      flipkart: flipkartProducts.status === "fulfilled" ? flipkartProducts.value : [],
    }

    if (!results.amazon.length && !results.flipkart.length) {
      return NextResponse.json({ error: "No products found" }, { status: 404 })
    }

    return NextResponse.json(results)
  } catch (error: any) {
    console.error("Scraping error:", error)
    return NextResponse.json(
      { error: error.message || "Internal server error" },
      { status: error.message === "Rate limit exceeded" ? 429 : 500 },
    )
  }
}

async function fetchWithRetry(url: string, retries = 3): Promise<string> {
  let lastError: Error | null = null

  for (let i = 0; i < retries; i++) {
    try {
      const fetchUrl = USE_PROXY ? `${PROXY_URL}${encodeURIComponent(url)}` : url
      const response = await fetch(fetchUrl, { headers })

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)

      return await response.text()
    } catch (error) {
      lastError = error as Error
      await new Promise((resolve) => setTimeout(resolve, 1000 * (i + 1)))
    }
  }

  throw lastError || new Error("Failed to fetch")
}

async function fetchAmazonProducts(query: string): Promise<Product[]> {
  try {
    const html = await fetchWithRetry(`https://www.amazon.in/s?k=${encodeURIComponent(query)}`)

    const $ = cheerio.load(html)
    const products: Product[] = []

    $(".s-result-item[data-asin]").each((i, el) => {
      if (i < 5 && $(el).attr("data-asin")) {
        const name = $(el).find("h2 span").text().trim()
        const price = $(el).find(".a-price-whole").first().text().trim()
        const image = $(el).find("img.s-image").attr("src")
        const rating = $(el).find(".a-icon-star-small .a-icon-alt").text().trim()
        const reviews = $(el).find(".a-size-base.s-underline-text").text().trim()
        const url = `https://www.amazon.in${$(el).find("h2 a").attr("href")}`

        if (name && price && image) {
          products.push({
            name,
            price,
            image,
            rating: rating || "0",
            reviews: reviews || "0 reviews",
            url,
            platform: "amazon",
          })
        }
      }
    })

    return products
  } catch (error) {
    console.error("Amazon scraping error:", error)
    return []
  }
}

async function fetchFlipkartProducts(query: string): Promise<Product[]> {
  try {
    const html = await fetchWithRetry(`https://www.flipkart.com/search?q=${encodeURIComponent(query)}`)

    const $ = cheerio.load(html)
    const products: Product[] = []

    $("div._1AtVbE").each((i, el) => {
      if (i < 5) {
        const name = $(el).find("div._4rR01T").text().trim() || $(el).find("a.s1Q9rs").text().trim()
        const price = $(el).find("div._30jeq3").text().trim()
        const image = $(el).find("img._396cs4").attr("src")
        const rating = $(el).find("div._3LWZlK").text().trim()
        const reviews = $(el).find("span._2_R_DZ").text().trim()
        const url = `https://www.flipkart.com${
          $(el).find("a._1fQZEK").attr("href") || $(el).find("a.s1Q9rs").attr("href")
        }`

        if (name && price && image) {
          products.push({
            name,
            price,
            image,
            rating: rating || "0",
            reviews: reviews || "0 reviews",
            url,
            platform: "flipkart",
          })
        }
      }
    })

    return products
  } catch (error) {
    console.error("Flipkart scraping error:", error)
    return []
  }
}

