export function rateLimit({ interval, uniqueTokenPerInterval }: { interval: number; uniqueTokenPerInterval: number }) {
  const tokens = new Map()

  return {
    check: async (limit: number, token: string) => {
      const now = Date.now()
      const windowStart = now - interval

      const tokenCount = tokens.get(token) || []
      const validTokens = tokenCount.filter((timestamp: number) => timestamp > windowStart)

      if (validTokens.length >= limit) {
        throw new Error("Rate limit exceeded")
      }

      validTokens.push(now)
      tokens.set(token, validTokens)

      return true
    },
  }
}

