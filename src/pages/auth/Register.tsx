import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Loader2, HardHat } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuthStore, type UserRole } from "@/store/authStore";
import { authApi } from "@/lib/api";

export default function Register() {
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [password_confirm, setConfirmPassword] = useState("");
  const [role, setRole] = useState<UserRole>("homeowner");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !email || password.length < 8 || password !== password_confirm) {
      toast.error("Fill all fields. Password must be at least 8 characters.");
      return;
    }
    setLoading(true);
    try {
      const { data } = await authApi.register({ name, email, password, password_confirm, role });
      // Auto-login after register
      const loginRes = await authApi.login(email, password);
      const meRes = await fetch(
        `${import.meta.env.VITE_API_BASE_URL || "/api/v1"}/auth/me/`,
        { headers: { Authorization: `Bearer ${loginRes.data.access}` } }
      );
      const me = meRes.ok ? await meRes.json() : null;
      login(
        {
          id: me?.id ?? data?.id ?? "user",
          name: me?.name ?? name,
          email: me?.email ?? email,
          role: (me?.role ?? role) as UserRole,
          avatarUrl: me?.avatar_url ?? undefined,
        },
        loginRes.data.access,
        loginRes.data.refresh
      );
      toast.success("Account created! Welcome to BuildHub.");
      navigate("/dashboard");
    } catch (err: any) {
      const data = err?.response?.data;
      const msg =
        data?.email?.[0] ??
        data?.password?.[0] ??
        data?.detail ??
        data?.non_field_errors?.[0] ??
        "Registration failed. Please try again.";
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
        <h1 className="text-2xl font-semibold tracking-tight">Create your account</h1>
        <p className="text-sm text-muted-foreground">
          Join thousands building smarter with BuildHub.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-2 rounded-xl bg-muted p-1">
        {(["homeowner", "contractor"] as UserRole[]).map((r) => (
          <button
            key={r}
            type="button"
            onClick={() => setRole(r)}
            className={`rounded-lg px-3 py-2.5 text-xs font-medium capitalize transition-all ${
              role === r
                ? "bg-card text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            I'm a {r}
          </button>
        ))}
      </div>

      <form onSubmit={onSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="name">Full name</Label>
          <Input
            id="name"
            placeholder="Jane Cooper"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            placeholder="you@company.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            placeholder="At least 8 characters"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="password_confirm">Confirm Password</Label>
          <Input
            id="password_confirm"
            type="password"
            placeholder="At least 8 characters"
            value={password_confirm}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
        </div>
        <Button type="submit" className="w-full" disabled={loading}>
          {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Create account
        </Button>
      </form>

      <p className="text-center text-sm text-muted-foreground">
        Already have an account?{" "}
        <Link to="/auth/login" className="font-medium text-foreground hover:underline">
          Sign in
        </Link>
      </p>
    </div>
  );
}
