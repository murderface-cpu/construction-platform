import { useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowLeft, HardHat, Mail, Loader2, CheckCircle2,
  ArrowRight, RefreshCw,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { authApi } from "@/lib/api";

type Step = "email" | "sent";

export default function ForgotPassword() {
  const [step, setStep] = useState<Step>("email");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) {
      toast.error("Enter your email address");
      return;
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      toast.error("Enter a valid email address");
      return;
    }
    setLoading(true);
    try {
      await authApi.forgotPassword?.(email);
    } catch {
      // Intentionally swallow errors — never confirm or deny account existence
    } finally {
      setLoading(false);
      setStep("sent");
      startResendCooldown();
    }
  };

  const startResendCooldown = () => {
    setResendCooldown(60);
    const interval = setInterval(() => {
      setResendCooldown((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const handleResend = async () => {
    if (resendCooldown > 0) return;
    setLoading(true);
    try {
      await authApi.forgotPassword?.(email);
      toast.success("Reset link resent");
    } catch {
      toast.success("Reset link resent"); // Same as above — no info leakage
    } finally {
      setLoading(false);
      startResendCooldown();
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

      {step === "email" ? (
        <>
          {/* Header */}
          <div className="space-y-1">
            <h1 className="text-2xl font-semibold tracking-tight">Forgot your password?</h1>
            <p className="text-sm text-muted-foreground">
              No problem. Enter your email and we'll send you a reset link.
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="email" className="text-sm font-medium">
                Email address
              </Label>
              <div className="relative">
                <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="email"
                  type="email"
                  autoComplete="email"
                  placeholder="you@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="h-10 pl-9"
                  autoFocus
                />
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
                  Send reset link
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                </>
              )}
            </Button>
          </form>

          {/* Back to sign in */}
          <div className="flex justify-center">
            <Link
              to="/auth/login"
              className="inline-flex items-center gap-1.5 text-sm text-muted-foreground underline-offset-2 transition-colors hover:text-foreground hover:underline"
            >
              <ArrowLeft className="h-3.5 w-3.5" />
              Back to sign in
            </Link>
          </div>
        </>
      ) : (
        <>
          {/* Success state */}
          <div className="space-y-1">
            {/* Animated check */}
            <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-500/10">
              <CheckCircle2 className="h-7 w-7 text-emerald-500" />
            </div>
            <h1 className="text-2xl font-semibold tracking-tight">Check your inbox</h1>
            <p className="text-sm text-muted-foreground">
              If <span className="font-medium text-foreground">{email}</span> is
              linked to a BuildHub account, you'll receive a password reset link
              within a few minutes.
            </p>
          </div>

          {/* Hints */}
          <div className="rounded-xl border border-border/60 bg-muted/40 p-4 space-y-2">
            <p className="text-xs font-medium text-foreground">Didn't get the email?</p>
            <ul className="space-y-1.5 text-xs text-muted-foreground">
              <li className="flex items-start gap-2">
                <span className="mt-0.5 text-muted-foreground/50">•</span>
                Check your spam or junk folder
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-0.5 text-muted-foreground/50">•</span>
                Make sure you entered the correct email
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-0.5 text-muted-foreground/50">•</span>
                The link expires in 30 minutes
              </li>
            </ul>
          </div>

          {/* Resend */}
          <Button
            variant="outline"
            className="w-full gap-2"
            size="lg"
            onClick={handleResend}
            disabled={loading || resendCooldown > 0}
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4" />
            )}
            {resendCooldown > 0
              ? `Resend in ${resendCooldown}s`
              : "Resend reset link"}
          </Button>

          {/* Try different email */}
          <div className="flex flex-col items-center gap-2 text-center">
            <button
              type="button"
              onClick={() => setStep("email")}
              className="text-sm text-muted-foreground underline-offset-2 transition-colors hover:text-foreground hover:underline"
            >
              Try a different email address
            </button>
            <Link
              to="/auth/login"
              className="inline-flex items-center gap-1.5 text-sm text-muted-foreground underline-offset-2 transition-colors hover:text-foreground hover:underline"
            >
              <ArrowLeft className="h-3.5 w-3.5" />
              Back to sign in
            </Link>
          </div>
        </>
      )}
    </div>
  );
}
