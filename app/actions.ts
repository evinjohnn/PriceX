"use server"

export async function scrapeProduct(query: string) {
  try {
    const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/search?q=${encodeURIComponent(query)}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error scraping product:', error);
    throw error;
  }
}