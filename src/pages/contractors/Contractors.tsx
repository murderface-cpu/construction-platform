import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search, SlidersHorizontal, X, Loader2, Sparkles } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { ContractorCard } from "@/components/cards/ContractorCard";
import { ContractorCardSkeleton } from "@/components/cards/ContractorCardSkeleton";
import { contractorsApi } from "@/lib/api";
import {
  contractors as MOCK_DATA, LOCATIONS, SPECIALTIES, type Contractor,
} from "@/lib/data/contractors";

const PAGE_SIZE = 6;
type SortKey = "recommended" | "rating" | "price-asc" | "price-desc";

async function fetchContractors(): Promise<Contractor[]> {
  try {
    const { data } = await contractorsApi.list();
    const list = Array.isArray(data) ? data : data?.results ?? data?.data ?? [];
    if (list.length > 0) {
      return list.map((c: any) => ({
        id: c.id ?? c.pk,
        name: c.name ?? c.user?.name ?? `${c.user?.first_name ?? ""} ${c.user?.last_name ?? ""}`.trim(),
        avatarUrl: c.avatar_url ?? c.profile_image ?? c.photo ?? "",
        specialty: c.specialty ?? c.trade ?? "General Contractor",
        location: c.location ?? c.city ?? "",
        rating: parseFloat(c.rating ?? c.avg_rating ?? "0") || 0,
        reviewCount: c.review_count ?? c.reviews_count ?? 0,
        yearsExperience: c.years_experience ?? c.experience_years ?? 0,
        hourlyRate: parseFloat(c.hourly_rate ?? c.rate ?? "0") || 0,
        verified: c.verified ?? c.is_verified ?? false,
        bio: c.bio ?? c.description ?? "",
        tags: c.tags ?? c.skills ?? [],
      }));
    }
  } catch {}
  return MOCK_DATA;
}

export default function Contractors() {
  const { data, isLoading } = useQuery({
    queryKey: ["contractors"],
    queryFn: fetchContractors,
    staleTime: 2 * 60 * 1000,
  });

  const [search, setSearch] = useState("");
  const [location, setLocation] = useState("all");
  const [specialty, setSpecialty] = useState("all");
  const [minRating, setMinRating] = useState("0");
  const [sort, setSort] = useState<SortKey>("recommended");
  const [visible, setVisible] = useState(PAGE_SIZE);

  const dynamicLocations = useMemo(() => {
    if (!data) return LOCATIONS;
    const fromAPI = [...new Set(data.map((c) => c.location).filter(Boolean))];
    return fromAPI.length > 0 ? fromAPI : LOCATIONS;
  }, [data]);

  const dynamicSpecialties = useMemo(() => {
    if (!data) return SPECIALTIES;
    const fromAPI = [...new Set(data.map((c) => c.specialty).filter(Boolean))];
    return fromAPI.length > 0 ? fromAPI : SPECIALTIES;
  }, [data]);

  const filtered = useMemo(() => {
    if (!data) return [];
    const q = search.trim().toLowerCase();
    let out = data.filter((c) => {
      if (location !== "all" && c.location !== location) return false;
      if (specialty !== "all" && c.specialty !== specialty) return false;
      if (c.rating < Number(minRating)) return false;
      if (q) {
        const hay = `${c.name} ${c.specialty} ${c.location} ${c.tags.join(" ")}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
    out = [...out].sort((a, b) => {
      switch (sort) {
        case "rating": return b.rating - a.rating;
        case "price-asc": return a.hourlyRate - b.hourlyRate;
        case "price-desc": return b.hourlyRate - a.hourlyRate;
        default: return b.rating * 50 + b.reviewCount - (a.rating * 50 + a.reviewCount);
      }
    });
    return out;
  }, [data, search, location, specialty, minRating, sort]);

  const visibleItems = filtered.slice(0, visible);
  const hasMore = visible < filtered.length;
  const activeFilters =
    (location !== "all" ? 1 : 0) +
    (specialty !== "all" ? 1 : 0) +
    (minRating !== "0" ? 1 : 0);
  const hasAnyFilter = activeFilters > 0 || !!search;

  const clearFilters = () => {
    setLocation("all"); setSpecialty("all"); setMinRating("0"); setSearch("");
    setVisible(PAGE_SIZE);
  };

  return (
    <div className="min-h-full bg-background">
      {/* Page header */}
      <div className="border-b border-border/50 px-6 py-7 md:px-10">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">Find a contractor</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Browse vetted professionals. Filter by location, specialty, and rating.
            </p>
          </div>
          {data && !isLoading && (
            <Badge variant="secondary" className="shrink-0 mt-1 font-medium">
              {filtered.length} available
            </Badge>
          )}
        </div>
      </div>

      <div className="px-6 py-6 md:px-10">
        {/* Search & filter bar */}
        <div className="rounded-xl border border-border/60 bg-card p-4 shadow-sm">
          <div className="flex flex-col gap-3 md:flex-row md:items-center">
            {/* Search */}
            <div className="relative flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by name, specialty, or skill…"
                value={search}
                onChange={(e) => { setSearch(e.target.value); setVisible(PAGE_SIZE); }}
                className="h-10 pl-9"
              />
              {search && (
                <button
                  type="button"
                  onClick={() => { setSearch(""); setVisible(PAGE_SIZE); }}
                  className="absolute right-3 top-1/2 -translate-y-1/2 rounded text-muted-foreground hover:text-foreground"
                >
                  <X className="h-3.5 w-3.5" />
                </button>
              )}
            </div>

            {/* Filters */}
            <div className="flex flex-wrap items-center gap-2">
              <Select value={location} onValueChange={(v) => { setLocation(v); setVisible(PAGE_SIZE); }}>
                <SelectTrigger className="h-10 w-full sm:w-[150px]">
                  <SelectValue placeholder="Location" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All locations</SelectItem>
                  {dynamicLocations.map((l) => (
                    <SelectItem key={l} value={l}>{l}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={specialty} onValueChange={(v) => { setSpecialty(v); setVisible(PAGE_SIZE); }}>
                <SelectTrigger className="h-10 w-full sm:w-[165px]">
                  <SelectValue placeholder="Specialty" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All specialties</SelectItem>
                  {dynamicSpecialties.map((s) => (
                    <SelectItem key={s} value={s}>{s}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={minRating} onValueChange={(v) => { setMinRating(v); setVisible(PAGE_SIZE); }}>
                <SelectTrigger className="h-10 w-full sm:w-[130px]">
                  <SelectValue placeholder="Rating" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="0">Any rating</SelectItem>
                  <SelectItem value="4">4.0+ ★</SelectItem>
                  <SelectItem value="4.5">4.5+ ★</SelectItem>
                  <SelectItem value="4.8">4.8+ ★</SelectItem>
                </SelectContent>
              </Select>

              <Select value={sort} onValueChange={(v) => setSort(v as SortKey)}>
                <SelectTrigger className="h-10 w-full sm:w-[160px]">
                  <SelectValue placeholder="Sort" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="recommended">
                    <span className="flex items-center gap-2">
                      <Sparkles className="h-3.5 w-3.5 text-amber-500" />
                      Recommended
                    </span>
                  </SelectItem>
                  <SelectItem value="rating">Highest rated</SelectItem>
                  <SelectItem value="price-asc">Price: low → high</SelectItem>
                  <SelectItem value="price-desc">Price: high → low</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Active filter pills */}
          {hasAnyFilter && (
            <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-border/50 pt-3">
              <SlidersHorizontal className="h-3.5 w-3.5 text-muted-foreground" />
              <span className="text-xs text-muted-foreground">Filters:</span>
              {search && (
                <Badge variant="secondary" className="gap-1 pl-2 pr-1">
                  "{search}"
                  <button onClick={() => { setSearch(""); setVisible(PAGE_SIZE); }} className="ml-0.5 rounded hover:text-foreground">
                    <X className="h-2.5 w-2.5" />
                  </button>
                </Badge>
              )}
              {location !== "all" && (
                <Badge variant="secondary" className="gap-1 pl-2 pr-1">
                  {location}
                  <button onClick={() => { setLocation("all"); setVisible(PAGE_SIZE); }} className="ml-0.5 rounded hover:text-foreground">
                    <X className="h-2.5 w-2.5" />
                  </button>
                </Badge>
              )}
              {specialty !== "all" && (
                <Badge variant="secondary" className="gap-1 pl-2 pr-1">
                  {specialty}
                  <button onClick={() => { setSpecialty("all"); setVisible(PAGE_SIZE); }} className="ml-0.5 rounded hover:text-foreground">
                    <X className="h-2.5 w-2.5" />
                  </button>
                </Badge>
              )}
              {minRating !== "0" && (
                <Badge variant="secondary" className="gap-1 pl-2 pr-1">
                  {minRating}+ stars
                  <button onClick={() => { setMinRating("0"); setVisible(PAGE_SIZE); }} className="ml-0.5 rounded hover:text-foreground">
                    <X className="h-2.5 w-2.5" />
                  </button>
                </Badge>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={clearFilters}
                className="ml-auto h-7 gap-1 text-xs text-muted-foreground hover:text-foreground"
              >
                Clear all
              </Button>
            </div>
          )}
        </div>

        {/* Results */}
        <div className="mt-6">
          {isLoading ? (
            <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <ContractorCardSkeleton key={i} />
              ))}
            </div>
          ) : filtered.length === 0 ? (
            <div className="mx-auto max-w-sm py-16 text-center">
              <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-muted">
                <Search className="h-6 w-6 text-muted-foreground" />
              </div>
              <h3 className="text-base font-semibold">No contractors found</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                Try adjusting your filters or widening your search criteria.
              </p>
              <Button onClick={clearFilters} variant="outline" size="sm" className="mt-5">
                Clear all filters
              </Button>
            </div>
          ) : (
            <>
              <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                {visibleItems.map((c) => (
                  <ContractorCard key={c.id} contractor={c} />
                ))}
              </div>
              {hasMore && (
                <div className="mt-8 flex justify-center">
                  <Button
                    variant="outline"
                    onClick={() => setVisible((v) => v + PAGE_SIZE)}
                    className="min-w-[160px]"
                  >
                    Load more
                    <span className="ml-2 rounded-full bg-muted px-1.5 py-0.5 text-xs">
                      {filtered.length - visible} remaining
                    </span>
                  </Button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
