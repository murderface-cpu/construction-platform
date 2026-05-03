import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search, SlidersHorizontal, X, Loader2 } from "lucide-react";
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
    // Normalise API response to local Contractor shape
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
  } catch {
    // Fallback to mock data when backend is unavailable
  }
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

  const clearFilters = () => {
    setLocation("all"); setSpecialty("all"); setMinRating("0"); setSearch("");
  };

  return (
    <div className="space-y-6 p-6 md:p-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Find a contractor</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Browse vetted professionals. Filter by location, specialty, and rating.
        </p>
      </div>

      <div className="rounded-xl border border-border bg-card p-4 shadow-sm">
        <div className="flex flex-col gap-3 md:flex-row md:items-center">
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search by name, specialty, or tag…"
              value={search}
              onChange={(e) => { setSearch(e.target.value); setVisible(PAGE_SIZE); }}
              className="h-10 pl-9"
            />
          </div>
          <div className="grid grid-cols-2 gap-2 md:flex md:items-center">
            <Select value={location} onValueChange={(v) => { setLocation(v); setVisible(PAGE_SIZE); }}>
              <SelectTrigger className="h-10 md:w-[160px]"><SelectValue placeholder="Location" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All locations</SelectItem>
                {dynamicLocations.map((l) => <SelectItem key={l} value={l}>{l}</SelectItem>)}
              </SelectContent>
            </Select>
            <Select value={specialty} onValueChange={(v) => { setSpecialty(v); setVisible(PAGE_SIZE); }}>
              <SelectTrigger className="h-10 md:w-[180px]"><SelectValue placeholder="Specialty" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All specialties</SelectItem>
                {dynamicSpecialties.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}
              </SelectContent>
            </Select>
            <Select value={minRating} onValueChange={(v) => { setMinRating(v); setVisible(PAGE_SIZE); }}>
              <SelectTrigger className="h-10 md:w-[140px]"><SelectValue placeholder="Rating" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="0">Any rating</SelectItem>
                <SelectItem value="4">4.0+ stars</SelectItem>
                <SelectItem value="4.5">4.5+ stars</SelectItem>
                <SelectItem value="4.8">4.8+ stars</SelectItem>
              </SelectContent>
            </Select>
            <Select value={sort} onValueChange={(v) => setSort(v as SortKey)}>
              <SelectTrigger className="h-10 md:w-[170px]"><SelectValue placeholder="Sort" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="recommended">Recommended</SelectItem>
                <SelectItem value="rating">Highest rated</SelectItem>
                <SelectItem value="price-asc">Price: low to high</SelectItem>
                <SelectItem value="price-desc">Price: high to low</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {(activeFilters > 0 || search) && (
          <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-border pt-3">
            <SlidersHorizontal className="h-3.5 w-3.5 text-muted-foreground" />
            <span className="text-xs text-muted-foreground">Active:</span>
            {location !== "all" && <Badge variant="secondary">{location}</Badge>}
            {specialty !== "all" && <Badge variant="secondary">{specialty}</Badge>}
            {minRating !== "0" && <Badge variant="secondary">{minRating}+ stars</Badge>}
            {search && <Badge variant="secondary">"{search}"</Badge>}
            <Button variant="ghost" size="sm" onClick={clearFilters} className="ml-auto h-7 gap-1 text-xs">
              <X className="h-3 w-3" /> Clear
            </Button>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>
          {isLoading ? "Loading…" : `${filtered.length} contractor${filtered.length === 1 ? "" : "s"} found`}
        </span>
      </div>

      {isLoading ? (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => <ContractorCardSkeleton key={i} />)}
        </div>
      ) : filtered.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border bg-muted/30 p-12 text-center">
          <h3 className="text-base font-semibold">No contractors match your filters</h3>
          <p className="mt-1 text-sm text-muted-foreground">Try widening your search or clearing filters.</p>
          <Button onClick={clearFilters} variant="outline" size="sm" className="mt-4">Clear filters</Button>
        </div>
      ) : (
        <>
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {visibleItems.map((c) => <ContractorCard key={c.id} contractor={c} />)}
          </div>
          {hasMore && (
            <div className="flex justify-center pt-2">
              <Button variant="outline" onClick={() => setVisible((v) => v + PAGE_SIZE)}>
                Load more
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
