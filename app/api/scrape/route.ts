// app/api/scrape/route.ts

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
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
  Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
  "Accept-Language": "en-US,en;q=0.9",
  "Accept-Encoding": "gzip, deflate, br",
  Connection: "keep-alive",
  "Upgrade-Insecure-Requests": "1",
  "Cache-Control": "max-age=0",
}

export async function GET(request: Request) {
  try {
    // await limiter.check(5, "CACHE_TOKEN") // You can re-enable this later

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

    if (amazonProducts.status === "rejected") {
      console.error("Amazon promise rejected:", amazonProducts.reason)
    }
    if (flipkartProducts.status === "rejected") {
      console.error("Flipkart promise rejected:", flipkartProducts.reason)
    }

    if (!results.amazon.length && !results.flipkart.length) {
      return NextResponse.json({ message: "No products found on either platform." }, { status: 404 })
    }

    return NextResponse.json(results)
  } catch (error: any) {
    console.error("Scraping error in GET handler:", error)
    return NextResponse.json(
      { error: error.message || "Internal server error" },
      { status: error.message === "Rate limit exceeded" ? 429 : 500 },
    )
  }
}

async function fetchWithRetry(url: string, retries = 2, delay = 1000): Promise<string> {
  for (let i = 0; i < retries; i++) {
    try {
      const fetchUrl = USE_PROXY && PROXY_URL ? `${PROXY_URL}${encodeURIComponent(url)}` : url
      const response = await fetch(fetchUrl, { headers, cache: "no-store" })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status} for ${url}`)
      }
      return await response.text()
    } catch (error) {
      if (i === retries - 1) throw error
      await new Promise((resolve) => setTimeout(resolve, delay * (i + 1)))
    }
  }
  throw new Error("Failed to fetch after multiple retries")
}

// Helper to clean up text
const cleanText = (text: string) => text.replace(/[\s,₹]+/g, "").trim()
const getFirstNumber = (text: string) => text.match(/(\d+\.?\d*)/)?.[0] || "0"

async function fetchAmazonProducts(query: string): Promise<Product[]> {
  try {
    const searchUrl = `https://www.amazon.in/s?k=${encodeURIComponent(query)}`
    const html = await fetchWithRetry(searchUrl)
    const $ = cheerio.load(html)
    const products: Product[] = []

    $('div[data-cy="search-result-item"]').each((i, el) => {
      if (products.length >= 5) return false // Stop after collecting 5 products

      const asin = $(el).attr("data-asin")
      if (!asin) return // Skip if it's not a real product item

      const name = $(el).find("h2 a.a-link-normal span.a-text-normal").text().trim()
      const priceText = $(el).find(".a-price-whole").first().text().trim()
      const image = $(el).find("img.s-image").attr("src")
      const rating = getFirstNumber($(el).find("span.a-icon-alt").first().text())
      const reviews = $(el).find('span.a-size-base.s-underline-text').text().trim() || '0'
      const url = `https://www.amazon.in${$(el).find("h2 a.a-link-normal").attr("href")}`

      if (name && priceText && image && url.startsWith("https://www.amazon.in")) {
        products.push({
          name,
          price: cleanText(priceText),
          image,
          rating: rating,
          reviews: cleanText(reviews),
          url,
          platform: "amazon",
        })
      }
    })

    if (products.length === 0) {
        console.error("No products found on Amazon. Page content might have changed or been blocked.");
        // Optional: you can log a snippet of the HTML to debug
        // console.log("Amazon HTML snippet:", $('body').html()?.substring(0, 500));
    }

    return products
  } catch (error) {
    console.error("Amazon scraping function error:", error)
    return []
  }
}

async function fetchFlipkartProducts(query: string): Promise<Product[]> {
  try {
    const searchUrl = `https://www.flipkart.com/search?q=${encodeURIComponent(query)}`
    const html = await fetchWithRetry(searchUrl)
    const $ = cheerio.load(html)
    const products: Product[] = []

    // Flipkart has multiple layouts, try the most common ones
    const productContainers = $('div._75nlfW').length ? $('div._75nlfW') : $('div.cPHDOP');

    productContainers.each((i, el) => {
      if (products.length >= 5) return false

      const name = $(el).find('div.KzDlHZ').text().trim() || $(el).find('a.wUfGUH').text().trim()
      const priceText = $(el).find('div.Nx9bqj._4b5DiR').text().trim()
      const image = $(el).find('img.DByuf4').attr('src')
      const rating = getFirstNumber($(el).find("div.XQDdHH").text())
      const reviews = $(el).find('span.Wphh3N').text().split(' ')[0] || '0' // e.g. "1,234 Ratings & 123 Reviews"
      const urlRelative = $(el).find('a.CGtC98').attr('href') || $(el).find('a.wUfGUH').attr('href')
      
      if (name && priceText && image && urlRelative) {
        products.push({
          name,
          price: cleanText(priceText),
          image,
          rating: rating,
          reviews: cleanText(reviews.split('&')[0]), // Get only the ratings count part
          url: `https://www.flipkart.com${urlRelative}`,
          platform: "flipkart",
        })
      }
    });

    if (products.length === 0) {
        console.error("No products found on Flipkart. Page content might have changed or been blocked.");
        // console.log("Flipkart HTML snippet:", $('body').html()?.substring(0, 500));
    }

    return products
  } catch (error) {
    console.error("Flipkart scraping function error:", error)
    return []
  }
}