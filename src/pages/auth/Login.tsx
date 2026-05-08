import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff, Loader2, HardHat, ArrowRight, ShieldCheck, Star, Zap } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuthStore, type UserRole } from "@/store/authStore";
import { authApi } from "@/lib/api";

const TRUST_SIGNALS = [
  { icon: ShieldCheck, text: "Bank-grade security" },
  { icon: Star, text: "4.9 average rating" },
  { icon: Zap, text: "Instant matching" },
];

export default function Login() {
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error("Enter your email and password");
      return;
    }
    setLoading(true);
    try {
      const { data } = await authApi.login(email, password);
      const meRes = await fetch(
        `${import.meta.env.VITE_API_BASE_URL || "/api/v1"}/auth/me/`,
        { headers: { Authorization: `Bearer ${data.access}` } }
      );
      const me = meRes.ok ? await meRes.json() : null;
      const user = {
        id: me?.id ?? me?.pk ?? "user",
        name: me?.name ?? me?.first_name ?? email.split("@")[0],
        email: me?.email ?? email,
        role: (me?.role ?? "homeowner") as UserRole,
        avatarUrl: me?.avatar_url ?? me?.profile_image ?? undefined,
      };
      login(user, data.access, data.refresh);
      toast.success("Welcome back!");
      navigate("/dashboard");
    } catch (err: any) {
      const msg =
        err?.response?.data?.detail ??
        err?.response?.data?.non_field_errors?.[0] ??
        "Invalid credentials";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Mobile logo */}
      <div className="flex items-center gap-2.5 lg:hidden">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary/70 shadow-sm">
          <HardHat className="h-4 w-4 text-primary-foreground" />
        </div>
        <span className="font-semibold tracking-tight">BuildHub</span>
      </div>

      {/* Header */}
      <div className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight">Sign in to BuildHub</h1>
        <p className="text-sm text-muted-foreground">
          Welcome back — pick up where you left off.
        </p>
      </div>

      {/* Form */}
      <form onSubmit={onSubmit} className="space-y-4">
        <div className="space-y-1.5">
          <Label htmlFor="email" className="text-sm font-medium">Email address</Label>
          <Input
            id="email"
            type="email"
            autoComplete="email"
            placeholder="you@company.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="h-10"
          />
        </div>

        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <Label htmlFor="password" className="text-sm font-medium">Password</Label>
            <Link
              to="/auth/forgot-password"
              className="text-xs text-muted-foreground underline-offset-2 transition-colors hover:text-foreground hover:underline"
            >
              Forgot password?
            </Link>
          </div>
          <div className="relative">
            <Input
              id="password"
              type={show ? "text" : "password"}
              autoComplete="current-password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="h-10 pr-10"
            />
            <button
              type="button"
              onClick={() => setShow((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 rounded text-muted-foreground transition-colors hover:text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              aria-label={show ? "Hide password" : "Show password"}
            >
              {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
        </div>

        <Button
          type="submit"
          className="group w-full gap-2 font-medium shadow-sm"
          size="lg"
          disabled={loading}
        >
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <>
              Sign in
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </>
          )}
        </Button>
      </form>

      {/* Divider */}
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-border" />
        </div>
        <div className="relative flex justify-center">
          <span className="bg-card px-3 text-xs text-muted-foreground">
            New to BuildHub?
          </span>
        </div>
      </div>

      <Button asChild variant="outline" className="w-full" size="lg">
        <Link to="/auth/register">Create a free account</Link>
      </Button>

      {/* Trust signals */}
      <div className="flex items-center justify-center gap-5 border-t border-border/50 pt-4">
        {TRUST_SIGNALS.map(({ icon: Icon, text }) => (
          <div key={text} className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <Icon className="h-3 w-3 text-primary/70" />
            <span>{text}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
