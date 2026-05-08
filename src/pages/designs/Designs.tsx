import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Palette, Loader2, Bookmark, BookmarkCheck, Sparkles } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { designsApi } from "@/lib/api";
import { toast } from "sonner";
import { useState } from "react";

export default function Designs() {
  const qc = useQueryClient();
  const [saving, setSaving] = useState<string | null>(null);

  const { data: designs = [], isLoading } = useQuery({
    queryKey: ["designs"],
    queryFn: async () => {
      try {
        const { data } = await designsApi.list();
        return Array.isArray(data) ? data : data?.results ?? [];
      } catch { return []; }
    },
  });

  const { data: savedIds = [] } = useQuery({
    queryKey: ["saved-designs"],
    queryFn: async () => {
      try {
        const { data } = await designsApi.saved();
        const list = Array.isArray(data) ? data : data?.results ?? [];
        return list.map((d: any) => d.id ?? d.design_id);
      } catch { return []; }
    },
  });

  const toggleSave = async (id: string, isSaved: boolean) => {
    setSaving(id);
    try {
      if (isSaved) await designsApi.unsave(id);
      else await designsApi.save(id);
      qc.invalidateQueries({ queryKey: ["saved-designs"] });
      toast.success(isSaved ? "Removed from saved" : "Design saved!");
    } catch {
      toast.error("Failed to update saved designs");
    } finally {
      setSaving(null);
    }
  };

  const savedCount = savedIds.length;

  return (
    <div className="min-h-full bg-background">
      {/* Header */}
      <div className="border-b border-border/50 px-6 py-7 md:px-10">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">Design inspiration</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Browse curated designs. Save your favorites to reference during your project.
            </p>
          </div>
          {savedCount > 0 && (
            <div className="flex items-center gap-1.5 rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
              <BookmarkCheck className="h-3.5 w-3.5" />
              {savedCount} saved
            </div>
          )}
        </div>
      </div>

      <div className="px-6 py-7 md:px-10">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center gap-3 py-20">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            <p className="text-sm text-muted-foreground">Loading designs…</p>
          </div>
        ) : designs.length === 0 ? (
          <div className="mx-auto max-w-sm py-16 text-center">
            <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-500/20 to-pink-500/10">
              <Palette className="h-6 w-6 text-violet-500" />
            </div>
            <h3 className="text-base font-semibold">No designs yet</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Curated design inspiration will appear here once they're added.
            </p>
          </div>
        ) : (
          <>
            {savedCount > 0 && (
              <div className="mb-6 flex items-center gap-2 rounded-xl border border-primary/20 bg-primary/5 px-4 py-3">
                <Sparkles className="h-4 w-4 text-primary" />
                <p className="text-sm text-foreground">
                  You've saved <span className="font-semibold">{savedCount} design{savedCount !== 1 ? "s" : ""}</span>. They'll be here as reference when you start your project.
                </p>
              </div>
            )}

            {/* Masonry-style grid */}
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {designs.map((d: any) => {
                const isSaved = savedIds.includes(d.id);
                return (
                  <div
                    key={d.id}
                    className="group relative flex flex-col overflow-hidden rounded-xl border border-border/60 bg-card shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md"
                  >
                    {/* Image */}
                    <div className="relative aspect-[4/3] overflow-hidden bg-muted">
                      {d.image_url || d.thumbnail ? (
                        <img
                          src={d.image_url ?? d.thumbnail}
                          alt={d.title ?? d.name}
                          loading="lazy"
                          className="h-full w-full object-cover transition duration-500 group-hover:scale-[1.04]"
                        />
                      ) : (
                        <div className="flex h-full items-center justify-center bg-gradient-to-br from-muted to-muted/50">
                          <Palette className="h-10 w-10 text-muted-foreground/20" />
                        </div>
                      )}

                      {/* Overlay on hover */}
                      <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />

                      {/* Save button */}
                      <button
                        onClick={() => toggleSave(d.id, isSaved)}
                        disabled={saving === d.id}
                        aria-label={isSaved ? "Remove from saved" : "Save design"}
                        className={`absolute right-3 top-3 flex h-8 w-8 items-center justify-center rounded-full shadow-sm backdrop-blur-sm transition-all ${
                          isSaved
                            ? "bg-primary text-primary-foreground shadow-primary/20 hover:bg-primary/90"
                            : "bg-background/80 text-muted-foreground hover:bg-background hover:text-foreground"
                        }`}
                      >
                        {saving === d.id ? (
                          <Loader2 className="h-3.5 w-3.5 animate-spin" />
                        ) : isSaved ? (
                          <BookmarkCheck className="h-3.5 w-3.5" />
                        ) : (
                          <Bookmark className="h-3.5 w-3.5" />
                        )}
                      </button>

                      {/* Style badge overlay */}
                      {d.style && (
                        <div className="absolute bottom-3 left-3">
                          <span className="rounded-full bg-background/90 px-2.5 py-1 text-xs font-medium backdrop-blur-sm">
                            {d.style}
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Info */}
                    <div className="p-4">
                      <h3 className="text-sm font-semibold leading-snug">
                        {d.title ?? d.name}
                      </h3>
                      {d.description && (
                        <p className="mt-1 line-clamp-2 text-xs leading-relaxed text-muted-foreground">
                          {d.description}
                        </p>
                      )}
                      {d.tags && d.tags.length > 0 && (
                        <div className="mt-2.5 flex flex-wrap gap-1.5">
                          {(d.tags as string[]).slice(0, 3).map((tag) => (
                            <Badge key={tag} variant="secondary" className="px-2 py-0.5 text-xs font-normal">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
