"use client"

import dynamic from 'next/dynamic'
import { SilkProps } from './Silk'

// Create a dynamic import for the Silk component to avoid SSR issues
const SilkComponent = dynamic(() => import('./Silk'), {
  ssr: false,
  loading: () => <div className="fixed inset-0 -z-10 bg-gradient-to-br from-gray-50 to-gray-100" />
})

// Fallback component that works with SSR
const FallbackBackground = ({ className }: { className?: string }) => (
  <div className={`fixed inset-0 -z-10 bg-gradient-to-br from-gray-50 via-gray-100 to-gray-200 ${className}`} />
)

const SilkBackground: React.FC<SilkProps> = (props) => {
  // Use a simple fallback for SSR
  if (typeof window === 'undefined') {
    return <FallbackBackground className={props.className} />
  }

  return <SilkComponent {...props} />
}

export default SilkBackground