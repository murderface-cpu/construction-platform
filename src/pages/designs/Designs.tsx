import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Palette, Heart, Loader2, Bookmark, BookmarkCheck } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
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

  return (
    <div className="space-y-6 p-6 md:p-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Design inspiration</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Browse curated designs. Save your favorites for your next project.
        </p>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center p-16">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : designs.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border bg-muted/30 p-12 text-center">
          <Palette className="mx-auto mb-3 h-8 w-8 text-muted-foreground" />
          <h3 className="text-base font-semibold">No designs yet</h3>
          <p className="mt-1 text-sm text-muted-foreground">Designs will appear here once they're added.</p>
        </div>
      ) : (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {designs.map((d: any) => {
            const isSaved = savedIds.includes(d.id);
            return (
              <Card key={d.id} className="group overflow-hidden transition hover:shadow-elegant hover:-translate-y-0.5">
                <div className="relative aspect-[4/3] overflow-hidden bg-muted">
                  {d.image_url || d.thumbnail ? (
                    <img src={d.image_url ?? d.thumbnail} alt={d.title ?? d.name}
                      loading="lazy"
                      className="h-full w-full object-cover transition duration-300 group-hover:scale-[1.03]" />
                  ) : (
                    <div className="flex h-full items-center justify-center">
                      <Palette className="h-8 w-8 text-muted-foreground/30" />
                    </div>
                  )}
                  <button
                    onClick={(e) => { e.stopPropagation(); toggleSave(d.id, isSaved); }}
                    disabled={saving === d.id}
                    className="absolute right-3 top-3 flex h-8 w-8 items-center justify-center rounded-full bg-card/90 shadow-sm transition hover:bg-card"
                  >
                    {saving === d.id ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : isSaved ? (
                      <BookmarkCheck className="h-4 w-4 text-primary" />
                    ) : (
                      <Bookmark className="h-4 w-4 text-muted-foreground" />
                    )}
                  </button>
                </div>
                <CardContent className="p-4 space-y-2">
                  <h3 className="font-medium text-sm">{d.title ?? d.name}</h3>
                  {d.style && <Badge variant="secondary" className="font-normal text-xs">{d.style}</Badge>}
                  {d.description && <p className="text-xs text-muted-foreground line-clamp-2">{d.description}</p>}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
