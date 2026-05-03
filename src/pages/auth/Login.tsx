import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff, Loader2, HardHat } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuthStore, type UserRole } from "@/store/authStore";
import { authApi } from "@/lib/api";

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
      // Backend returns access + refresh tokens; fetch /me for profile
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
    <div className="space-y-7">
      <div className="space-y-1.5">
        <div className="flex items-center gap-2 mb-4 lg:hidden">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-accent">
            <HardHat className="h-4 w-4 text-white" />
          </div>
          <span className="font-semibold text-sm">BuildHub</span>
        </div>
        <h1 className="text-2xl font-semibold tracking-tight">Sign in</h1>
        <p className="text-sm text-muted-foreground">
          Welcome back. Pick up where you left off.
        </p>
      </div>

      <form onSubmit={onSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            autoComplete="email"
            placeholder="you@company.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="password">Password</Label>
            <Link to="#" className="text-xs text-muted-foreground hover:text-foreground transition-colors">
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
            />
            <button
              type="button"
              onClick={() => setShow((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
              aria-label={show ? "Hide password" : "Show password"}
            >
              {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
        </div>

        <Button type="submit" className="w-full" disabled={loading}>
          {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Sign in
        </Button>
      </form>

      <p className="text-center text-sm text-muted-foreground">
        New to BuildHub?{" "}
        <Link to="/auth/register" className="font-medium text-foreground hover:underline">
          Create an account
        </Link>
      </p>
    </div>
  );
}
