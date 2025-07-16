// components/tweet-card.tsx

"use client"

import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Heart, Repeat } from "lucide-react";
import { formatDistanceToNow } from 'date-fns';

// This is a custom component to represent the X/Twitter icon
const TwitterIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg
    aria-label="X"
    role="img"
    viewBox="0 0 24 24"
    xmlns="http://www.w3.org/2000/svg"
    {...props}
  >
    <path d="M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 7.184L18.901 1.153zm-1.65 19.57h2.6l-13.724-19.57h-2.66l13.784 19.57z" />
  </svg>
);


interface DealPost {
  id: string;
  text: string;
  created_at: string;
  url: string;
  likes: number;
  retweets: number;
}

// Function to parse tweet text and make links clickable
const formatTweetText = (text: string) => {
  const urlRegex = /(https?:\/\/[^\s]+)/g;
  const hashtagRegex = /#(\w+)/g;
  const mentionRegex = /@(\w+)/g;

  const parts = text
    .replace(urlRegex, (url) => `<a href="${url}" target="_blank" rel="noopener noreferrer" class="text-blue-500 hover:underline">${url}</a>`)
    .replace(hashtagRegex, (hashtag, word) => `<a href="https://x.com/hashtag/${word}" target="_blank" rel="noopener noreferrer" class="text-blue-500 hover:underline">${hashtag}</a>`)
    .replace(mentionRegex, (mention, word) => `<a href="https://x.com/${word}" target="_blank" rel="noopener noreferrer" class="text-blue-500 hover:underline">${mention}</a>`);

  return <p dangerouslySetInnerHTML={{ __html: parts }} className="whitespace-pre-wrap text-sm" />;
};

export function TweetCard({ deal }: { deal: DealPost }) {
  const timeAgo = formatDistanceToNow(new Date(deal.created_at), { addSuffix: true });

  return (
    <Card className="flex flex-col h-full transition-all duration-300 hover:shadow-xl hover:-translate-y-1 bg-white dark:bg-gray-900/50">
      <CardContent className="p-6 flex-grow">
        {formatTweetText(deal.text)}
      </CardContent>
      <CardFooter className="p-4 bg-gray-50 dark:bg-gray-800/50 border-t flex justify-between items-center text-sm text-gray-500 dark:text-gray-400">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1">
            <Heart className="w-4 h-4" />
            <span>{deal.likes}</span>
          </div>
          <div className="flex items-center gap-1">
            <Repeat className="w-4 h-4" />
            <span>{deal.retweets}</span>
          </div>
        </div>
        <a 
          href={deal.url} 
          target="_blank" 
          rel="noopener noreferrer" 
          className="flex items-center gap-2 hover:text-blue-500"
        >
          <span>{timeAgo}</span>
          <TwitterIcon className="w-4 h-4 fill-current" />
        </a>
      </CardFooter>
    </Card>
  );
}