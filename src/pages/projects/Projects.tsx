import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, FolderKanban, Loader2, ChevronRight, Calendar, Users2, MapPin, DollarSign } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { projectsApi } from "@/lib/api";
import { useAuthStore } from "@/store/authStore";
import { toast } from "sonner";
import { format } from "date-fns";

function statusColor(s: string) {
  if (s === "active" || s === "in_progress") return "bg-success/10 text-success";
  if (s === "completed") return "bg-info/10 text-info";
  if (s === "cancelled") return "bg-destructive/10 text-destructive";
  return "bg-secondary text-secondary-foreground";
}

export default function Projects() {
  const isContractor = useAuthStore((s) => s.user?.role === "contractor");
  const qc = useQueryClient();
  const [createOpen, setCreateOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("renovation");
  const [location, setLocation] = useState("");
  const [budget, setBudget] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [creating, setCreating] = useState(false);

  const { data: projects = [], isLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: async () => {
      try {
        const { data } = await projectsApi.list();
        return Array.isArray(data) ? data : data?.results ?? [];
      } catch { return []; }
    },
  });

  const handleCreate = async () => {
    if (!title.trim()) { toast.error("Enter a project title"); return; }
    if (!location.trim()) { toast.error("Enter a project location"); return; }
    setCreating(true);
    try {
      await projectsApi.create({
        title,
        description,
        category,
        location,
        budget: budget ? parseFloat(budget) : null,
        start_date: startDate || null,
        end_date: endDate || null,
      });
      qc.invalidateQueries({ queryKey: ["projects"] });
      toast.success("Project created!");
      setCreateOpen(false);
      resetForm();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "Failed to create project");
    } finally {
      setCreating(false);
    }
  };

  const resetForm = () => {
    setTitle("");
    setDescription("");
    setCategory("renovation");
    setLocation("");
    setBudget("");
    setStartDate("");
    setEndDate("");
  };

  return (
    <div className="space-y-6 p-6 md:p-8">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Projects</h1>
          <p className="text-sm text-muted-foreground mt-1">
            {isContractor ? "Projects you're assigned to." : "Manage your construction projects."}
          </p>
        </div>
        {!isContractor && (
          <Button onClick={() => setCreateOpen(true)}>
            <Plus className="mr-2 h-4 w-4" /> New project
          </Button>
        )}
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center p-16">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : projects.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border bg-muted/30 p-12 text-center">
          <FolderKanban className="mx-auto mb-3 h-8 w-8 text-muted-foreground" />
          <h3 className="text-base font-semibold">No projects yet</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            {isContractor ? "You haven't been assigned to any projects yet." : "Create your first project to get started."}
          </p>
          {!isContractor && (
            <Button onClick={() => setCreateOpen(true)} size="sm" className="mt-4">
              <Plus className="mr-2 h-4 w-4" /> Create project
            </Button>
          )}
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects.map((p: any) => (
            <Link key={p.id} to={`/projects/${p.id}`}>
              <Card className="h-full cursor-pointer transition hover:shadow-elegant hover:-translate-y-0.5">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between gap-2">
                    <CardTitle className="text-base leading-tight">{p.title ?? p.name}</CardTitle>
                    <Badge className={`shrink-0 text-xs capitalize ${statusColor(p.status ?? "pending")}`}>
                      {(p.status ?? "pending").replace("_", " ")}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  {p.description && (
                    <p className="line-clamp-2 text-sm text-muted-foreground">{p.description}</p>
                  )}
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    {p.created_at && (
                      <span className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {format(new Date(p.created_at), "MMM d, yyyy")}
                      </span>
                    )}
                    {p.members_count != null && (
                      <span className="flex items-center gap-1">
                        <Users2 className="h-3 w-3" /> {p.members_count} members
                      </span>
                    )}
                  </div>
                  <div className="flex items-center text-xs font-medium text-primary">
                    View details <ChevronRight className="ml-1 h-3 w-3" />
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}

      {/* Create dialog */}
      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>New project</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            {/* Title */}
            <div className="space-y-2">
              <Label>Project title *</Label>
              <Input
                placeholder="Kitchen renovation"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>

            {/* Category */}
            <div className="space-y-2">
              <Label>Category</Label>
              <Select value={category} onValueChange={setCategory}>
                <SelectTrigger>
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="renovation">Renovation</SelectItem>
                  <SelectItem value="new_build">New Build</SelectItem>
                  <SelectItem value="repair">Repair</SelectItem>
                  <SelectItem value="landscaping">Landscaping</SelectItem>
                  <SelectItem value="interior">Interior Design</SelectItem>
                  <SelectItem value="commercial">Commercial</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Location */}
            <div className="space-y-2">
              <Label>Location *</Label>
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  className="pl-9"
                  placeholder="123 Main St, City, State"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                />
              </div>
            </div>

            {/* Budget */}
            <div className="space-y-2">
              <Label>Budget (optional)</Label>
              <div className="relative">
                <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  type="number"
                  min="0"
                  step="0.01"
                  className="pl-9"
                  placeholder="50000.00"
                  value={budget}
                  onChange={(e) => setBudget(e.target.value)}
                />
              </div>
            </div>

            {/* Dates */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Start date (optional)</Label>
                <Input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>End date (optional)</Label>
                <Input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                />
              </div>
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label>Description (optional)</Label>
              <Textarea
                placeholder="Describe the scope of work…"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => { setCreateOpen(false); resetForm(); }}>Cancel</Button>
            <Button onClick={handleCreate} disabled={creating}>
              {creating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Create project
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}