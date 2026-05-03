import { Star, StarHalf } from "lucide-react";
import { cn } from "@/lib/utils";

interface RatingStarsProps {
  value: number; // 0–5
  size?: "sm" | "md" | "lg";
  showValue?: boolean;
  reviewCount?: number;
  className?: string;
}

const sizeMap = { sm: "h-3 w-3", md: "h-4 w-4", lg: "h-5 w-5" };

export function RatingStars({
  value,
  size = "sm",
  showValue = true,
  reviewCount,
  className,
}: RatingStarsProps) {
  const full = Math.floor(value);
  const hasHalf = value - full >= 0.25 && value - full < 0.75;
  const total = 5;

  return (
    <div className={cn("inline-flex items-center gap-1.5", className)}>
      <div className="flex items-center text-warning" aria-hidden>
        {Array.from({ length: total }).map((_, i) => {
          if (i < full) {
            return <Star key={i} className={cn(sizeMap[size], "fill-current")} />;
          }
          if (i === full && hasHalf) {
            return <StarHalf key={i} className={cn(sizeMap[size], "fill-current")} />;
          }
          return <Star key={i} className={cn(sizeMap[size], "text-muted-foreground/30")} />;
        })}
      </div>
      {showValue && (
        <span className="text-xs font-medium text-foreground">
          {value.toFixed(1)}
          {typeof reviewCount === "number" && (
            <span className="ml-1 font-normal text-muted-foreground">
              ({reviewCount})
            </span>
          )}
        </span>
      )}
    </div>
  );
}
