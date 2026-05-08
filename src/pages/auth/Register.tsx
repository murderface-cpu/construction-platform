import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Loader2, HardHat, Home, Wrench, Eye, EyeOff, ArrowRight, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuthStore, type UserRole } from "@/store/authStore";
import { authApi } from "@/lib/api";

const ROLE_OPTIONS: { value: UserRole; label: string; description: string; icon: typeof Home }[] = [
  {
    value: "homeowner",
    label: "Homeowner",
    description: "I need work done on my property",
    icon: Home,
  },
  {
    value: "contractor",
    label: "Contractor",
    description: "I offer professional services",
    icon: Wrench,
  },
];

function PasswordStrength({ password }: { password: string }) {
  const checks = [
    { label: "8+ characters", pass: password.length >= 8 },
    { label: "Uppercase", pass: /[A-Z]/.test(password) },
    { label: "Number", pass: /[0-9]/.test(password) },
  ];
  if (!password) return null;
  return (
    <div className="flex gap-2 pt-1">
      {checks.map((c) => (
        <div key={c.label} className="flex items-center gap-1 text-xs">
          <div className={`h-1.5 w-1.5 rounded-full transition-colors ${c.pass ? "bg-emerald-500" : "bg-muted-foreground/40"}`} />
          <span className={c.pass ? "text-emerald-600 dark:text-emerald-400" : "text-muted-foreground"}>
            {c.label}
          </span>
        </div>
      ))}
    </div>
  );
}

export default function Register() {
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [password_confirm, setConfirmPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [role, setRole] = useState<UserRole>("homeowner");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !email || password.length < 8 || password !== password_confirm) {
      toast.error("Fill all fields. Password must be at least 8 characters and match.");
      return;
    }
    setLoading(true);
    try {
      const { data } = await authApi.register({ name, email, password, password_confirm, role });
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
      const d = err?.response?.data;
      const msg =
        d?.email?.[0] ??
        d?.password?.[0] ??
        d?.detail ??
        d?.non_field_errors?.[0] ??
        "Registration failed. Please try again.";
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
        <h1 className="text-2xl font-semibold tracking-tight">Create your account</h1>
        <p className="text-sm text-muted-foreground">
          Join thousands building smarter with BuildHub.
        </p>
      </div>

      {/* Role selector */}
      <div className="grid grid-cols-2 gap-2.5">
        {ROLE_OPTIONS.map(({ value, label, description, icon: Icon }) => (
          <button
            key={value}
            type="button"
            onClick={() => setRole(value)}
            className={`relative flex flex-col gap-1.5 rounded-xl border-2 p-4 text-left transition-all ${
              role === value
                ? "border-primary bg-primary/5 shadow-sm"
                : "border-border bg-card hover:border-border/80 hover:bg-muted/40"
            }`}
          >
            {role === value && (
              <CheckCircle2 className="absolute right-2.5 top-2.5 h-3.5 w-3.5 text-primary" />
            )}
            <Icon className={`h-4 w-4 ${role === value ? "text-primary" : "text-muted-foreground"}`} />
            <span className={`text-sm font-semibold ${role === value ? "text-foreground" : "text-muted-foreground"}`}>
              {label}
            </span>
            <span className="text-xs leading-snug text-muted-foreground">{description}</span>
          </button>
        ))}
      </div>

      {/* Form */}
      <form onSubmit={onSubmit} className="space-y-4">
        <div className="space-y-1.5">
          <Label htmlFor="name" className="text-sm font-medium">Full name</Label>
          <Input
            id="name"
            placeholder="Jane Cooper"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="h-10"
            autoComplete="name"
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="email" className="text-sm font-medium">Email address</Label>
          <Input
            id="email"
            type="email"
            placeholder="you@company.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="h-10"
            autoComplete="email"
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="password" className="text-sm font-medium">Password</Label>
          <div className="relative">
            <Input
              id="password"
              type={showPw ? "text" : "password"}
              placeholder="At least 8 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="h-10 pr-10"
              autoComplete="new-password"
            />
            <button
              type="button"
              onClick={() => setShowPw((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 rounded text-muted-foreground transition-colors hover:text-foreground focus:outline-none"
              aria-label={showPw ? "Hide password" : "Show password"}
            >
              {showPw ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
          <PasswordStrength password={password} />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="password_confirm" className="text-sm font-medium">Confirm password</Label>
          <Input
            id="password_confirm"
            type="password"
            placeholder="Repeat your password"
            value={password_confirm}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className={`h-10 ${
              password_confirm && password !== password_confirm
                ? "border-destructive focus-visible:ring-destructive"
                : ""
            }`}
            autoComplete="new-password"
          />
          {password_confirm && password !== password_confirm && (
            <p className="text-xs text-destructive">Passwords don't match</p>
          )}
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
              Create account
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </>
          )}
        </Button>

        <p className="text-center text-xs text-muted-foreground">
          By creating an account, you agree to our{" "}
          <Link to="#" className="underline underline-offset-2 hover:text-foreground">Terms of Service</Link>{" "}
          and{" "}
          <Link to="#" className="underline underline-offset-2 hover:text-foreground">Privacy Policy</Link>.
        </p>
      </form>

      {/* Sign in link */}
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-border" />
        </div>
        <div className="relative flex justify-center">
          <span className="bg-card px-3 text-xs text-muted-foreground">Already have an account?</span>
        </div>
      </div>

      <Button asChild variant="outline" className="w-full" size="lg">
        <Link to="/auth/login">Sign in instead</Link>
      </Button>
    </div>
  );
}
