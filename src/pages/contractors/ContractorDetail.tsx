import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowLeft, BadgeCheck, Briefcase, Calendar as CalendarIcon,
  MapPin, MessageSquare, Star, Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { RatingStars } from "@/components/ui/rating-stars";
import { BookingModal } from "@/components/forms/BookingModal";
import { contractorsApi, reviewsApi } from "@/lib/api";
import { contractors as MOCK, type Contractor } from "@/lib/data/contractors";
import { PORTFOLIO_POOL, SAMPLE_REVIEWS } from "@/lib/data/portfolio";
import { format } from "date-fns";

export default function ContractorDetail() {
  const { id } = useParams<{ id: string }>();
  const [bookingOpen, setBookingOpen] = useState(false);

  const { data: contractor, isLoading } = useQuery({
    queryKey: ["contractor", id],
    queryFn: async (): Promise<Contractor> => {
      try {
        const { data } = await contractorsApi.get(id!);
        return {
          id: data.id ?? id!,
          name: data.name ?? data.user?.name ?? "",
          avatarUrl: data.avatar_url ?? data.profile_image ?? "",
          specialty: data.specialty ?? "General Contractor",
          location: data.location ?? "",
          rating: parseFloat(data.rating ?? "0") || 0,
          reviewCount: data.review_count ?? 0,
          yearsExperience: data.years_experience ?? 0,
          hourlyRate: parseFloat(data.hourly_rate ?? "0") || 0,
          verified: data.verified ?? false,
          bio: data.bio ?? data.description ?? "",
          tags: data.tags ?? [],
          portfolio: data.portfolio ?? [],
        } as any;
      } catch {
        return MOCK.find((c) => c.id === id) ?? MOCK[0];
      }
    },
    enabled: !!id,
  });

  const { data: reviews = [] } = useQuery({
    queryKey: ["reviews", id],
    queryFn: async () => {
      try {
        const { data } = await reviewsApi.list(id!);
        const list = Array.isArray(data) ? data : data?.results ?? [];
        if (list.length > 0) return list;
      } catch {}
      return SAMPLE_REVIEWS;
    },
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-20">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const c = contractor;
  if (!c) {
    return (
      <div className="p-8">
        <p className="text-sm text-muted-foreground">Contractor not found.</p>
        <Button asChild variant="outline" size="sm" className="mt-4">
          <Link to="/contractors"><ArrowLeft className="mr-1 h-4 w-4" /> Back</Link>
        </Button>
      </div>
    );
  }

  const portfolio = (c as any).portfolio?.length
    ? (c as any).portfolio
    : PORTFOLIO_POOL.slice(0, 4).map((p, i) => ({ ...p, id: `${c.id}-${p.id}-${i}` }));

  const avgRating = reviews.length
    ? reviews.reduce((acc: number, r: any) => acc + (r.rating ?? 0), 0) / reviews.length
    : c.rating;

  return (
    <div className="p-6 md:p-8">
      <Button asChild variant="ghost" size="sm" className="mb-4 -ml-2">
        <Link to="/contractors"><ArrowLeft className="mr-1 h-4 w-4" /> Back to marketplace</Link>
      </Button>

      <div className="grid gap-8 lg:grid-cols-[1fr_320px]">
        <div className="space-y-8">
          {/* Header */}
          <div className="flex flex-col items-start gap-5 sm:flex-row">
            {c.avatarUrl ? (
              <img src={c.avatarUrl} alt={c.name} loading="eager" width={128} height={128}
                className="h-28 w-28 shrink-0 rounded-xl object-cover shadow-card" />
            ) : (
              <div className="flex h-28 w-28 items-center justify-center rounded-xl bg-secondary text-3xl font-bold">
                {c.name.slice(0, 1)}
              </div>
            )}
            <div className="min-w-0 flex-1 space-y-2">
              <div className="flex flex-wrap items-center gap-2">
                <h1 className="text-2xl font-semibold tracking-tight">{c.name}</h1>
                {c.verified && (
                  <Badge className="gap-1 bg-info/10 text-info hover:bg-info/15">
                    <BadgeCheck className="h-3 w-3" /> Verified
                  </Badge>
                )}
              </div>
              <p className="text-sm text-muted-foreground">{c.specialty}</p>
              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
                {c.location && <span className="inline-flex items-center gap-1"><MapPin className="h-3.5 w-3.5" /> {c.location}</span>}
                {c.yearsExperience > 0 && <span className="inline-flex items-center gap-1"><Briefcase className="h-3.5 w-3.5" /> {c.yearsExperience} years exp</span>}
                <RatingStars value={c.rating} reviewCount={c.reviewCount} />
              </div>
              <div className="flex flex-wrap gap-1.5 pt-1">
                {c.tags.map((t) => <Badge key={t} variant="secondary" className="font-normal">{t}</Badge>)}
              </div>
            </div>
          </div>

          {c.bio && (
            <section className="space-y-3">
              <h2 className="text-lg font-semibold">About</h2>
              <p className="text-sm leading-relaxed text-muted-foreground">{c.bio}</p>
            </section>
          )}

          <Separator />

          {/* Portfolio */}
          <section className="space-y-4">
            <div className="flex items-end justify-between">
              <h2 className="text-lg font-semibold">Portfolio</h2>
              <span className="text-xs text-muted-foreground">{portfolio.length} projects</span>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              {portfolio.map((p: any) => (
                <figure key={p.id} className="group overflow-hidden rounded-lg border border-border bg-card">
                  <div className="relative aspect-[4/3] overflow-hidden bg-muted">
                    {p.imageUrl || p.image_url ? (
                      <img src={p.imageUrl ?? p.image_url} alt={p.title} loading="lazy"
                        className="h-full w-full object-cover transition duration-300 group-hover:scale-[1.03]" />
                    ) : (
                      <div className="flex h-full items-center justify-center text-muted-foreground text-sm">No image</div>
                    )}
                  </div>
                  <figcaption className="flex items-center justify-between p-3">
                    <span className="text-sm font-medium">{p.title}</span>
                    <Badge variant="secondary" className="font-normal">{p.category}</Badge>
                  </figcaption>
                </figure>
              ))}
            </div>
          </section>

          <Separator />

          {/* Reviews */}
          <section className="space-y-4">
            <div className="flex items-end justify-between">
              <h2 className="text-lg font-semibold">Reviews</h2>
              <RatingStars value={avgRating} reviewCount={reviews.length} size="md" />
            </div>
            {reviews.length === 0 ? (
              <div className="rounded-xl border border-dashed border-border bg-muted/30 p-8 text-center text-sm text-muted-foreground">
                No reviews yet.
              </div>
            ) : (
              <div className="space-y-3">
                {reviews.map((r: any) => (
                  <Card key={r.id} className="shadow-sm">
                    <CardContent className="space-y-2 p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-secondary text-xs font-semibold">
                            {(r.author ?? r.reviewer_name ?? "?").slice(0, 1)}
                          </div>
                          <div className="leading-tight">
                            <div className="text-sm font-medium">{r.author ?? r.reviewer_name ?? "Anonymous"}</div>
                            <div className="text-[11px] text-muted-foreground">
                              {r.date ?? r.created_at ? format(new Date(r.date ?? r.created_at), "MMM d, yyyy") : ""}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-0.5">
                          {Array.from({ length: 5 }).map((_, i) => (
                            <Star key={i} className={`h-3.5 w-3.5 ${i < r.rating ? "fill-warning text-warning" : "text-muted-foreground/30"}`} />
                          ))}
                        </div>
                      </div>
                      <p className="text-sm leading-relaxed text-muted-foreground">{r.body ?? r.comment ?? r.text}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </section>
        </div>

        {/* Sticky booking sidebar */}
        <aside className="lg:sticky lg:top-20 lg:self-start">
          <Card className="shadow-elegant">
            <CardContent className="space-y-4 p-5">
              <div className="space-y-1">
                <div className="text-xs uppercase tracking-wider text-muted-foreground">Hourly rate</div>
                <div className="text-3xl font-semibold tracking-tight">
                  ${c.hourlyRate || "—"}
                  {c.hourlyRate > 0 && <span className="text-sm font-normal text-muted-foreground">/hr</span>}
                </div>
              </div>
              <Separator />
              <Button className="w-full" size="lg" onClick={() => setBookingOpen(true)}>
                <CalendarIcon className="mr-2 h-4 w-4" /> Book consultation
              </Button>
              <Button variant="outline" className="w-full">
                <MessageSquare className="mr-2 h-4 w-4" /> Send a message
              </Button>
              <p className="text-center text-[11px] text-muted-foreground">
                You won't be charged until booking is confirmed.
              </p>
            </CardContent>
          </Card>
        </aside>
      </div>

      <BookingModal contractor={c} open={bookingOpen} onOpenChange={setBookingOpen} />
    </div>
  );
}
