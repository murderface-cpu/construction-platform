import { Link } from "react-router-dom";
import { MapPin, BadgeCheck, Clock, Star } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { Contractor } from "@/lib/data/contractors";

interface ContractorCardProps {
  contractor: Contractor;
}

export function ContractorCard({ contractor: c }: ContractorCardProps) {
  return (
    <Link
      to={`/contractors/${c.id}`}
      className="group block focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 rounded-xl"
    >
      <div className="overflow-hidden rounded-xl border border-border bg-card shadow-sm transition-all duration-300 group-hover:shadow-elegant group-hover:-translate-y-1">
        {/* Image area */}
        <div className="relative aspect-[3/2] overflow-hidden bg-muted">
          {c.avatarUrl ? (
            <img
              src={c.avatarUrl}
              alt={`${c.name} – ${c.specialty}`}
              loading="lazy"
              className="h-full w-full object-cover transition duration-500 group-hover:scale-[1.05]"
            />
          ) : (
            <div className="flex h-full items-center justify-center bg-gradient-primary text-4xl font-bold text-white/30">
              {c.name.slice(0, 1)}
            </div>
          )}

          {/* Gradient overlay at bottom */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent opacity-0 transition-opacity group-hover:opacity-100" />

          {/* Badges */}
          <div className="absolute left-3 top-3 flex items-center gap-1.5">
            {c.verified && (
              <span className="inline-flex items-center gap-1 rounded-full bg-white/95 px-2.5 py-1 text-[11px] font-semibold text-foreground shadow-sm backdrop-blur-sm">
                <BadgeCheck className="h-3 w-3 text-info" />
                Verified
              </span>
            )}
          </div>
          <div className="absolute right-3 top-3">
            <span className="inline-flex items-center rounded-full bg-foreground/80 px-2.5 py-1 text-[11px] font-bold text-white backdrop-blur-sm">
              ${c.hourlyRate}/hr
            </span>
          </div>
        </div>

        {/* Content */}
        <div className="p-4">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <h3 className="truncate text-[15px] font-semibold leading-tight">{c.name}</h3>
              <p className="mt-0.5 truncate text-xs text-muted-foreground">{c.specialty}</p>
            </div>
            {c.rating > 0 && (
              <div className="flex items-center gap-1 shrink-0">
                <Star className="h-3.5 w-3.5 fill-warning text-warning" />
                <span className="text-xs font-semibold">{c.rating.toFixed(1)}</span>
                <span className="text-[11px] text-muted-foreground">({c.reviewCount})</span>
              </div>
            )}
          </div>

          <div className="mt-3 flex items-center gap-3 text-[11px] text-muted-foreground">
            {c.location && (
              <span className="flex items-center gap-1">
                <MapPin className="h-3 w-3" />
                {c.location}
              </span>
            )}
            {c.yearsExperience > 0 && (
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {c.yearsExperience} yrs
              </span>
            )}
          </div>

          {c.tags.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {c.tags.slice(0, 3).map((t) => (
                <span key={t} className="inline-flex rounded-md bg-secondary px-2 py-0.5 text-[11px] font-medium text-secondary-foreground">
                  {t}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </Link>
  );
}
