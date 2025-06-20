"use server"

export async function scrapeProduct(query: string) {
  try {
    const response = await fetch(`http://localhost:8000/search?q=${encodeURIComponent(query)}`, {
      cache: 'no-store'
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      const errorMessage = errorData?.detail || `Failed to fetch products. Status: ${response.status}`;
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    console.error("Scraping failed:", error);
    if (error instanceof Error) {
        throw new Error(error.message);
    }
    throw new Error("An unknown error occurred during scraping.");
  }
}