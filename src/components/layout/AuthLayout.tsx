import { Outlet, Link } from "react-router-dom";
import { HardHat, CheckCircle2 } from "lucide-react";

const STATS = [
  { k: "12k+", v: "Vetted Contractors" },
  { k: "98%", v: "On-time delivery" },
  { k: "4.9★", v: "Avg. rating" },
];

const TESTIMONIALS = [
  { text: "Found the perfect contractor for our extension in hours, not weeks.", author: "Sarah M.", role: "Homeowner" },
  { text: "BuildHub completely transformed how I manage client projects.", author: "James K.", role: "General Contractor" },
];

export default function AuthLayout() {
  return (
    <div className="grid min-h-screen w-full lg:grid-cols-[1fr_480px]">
      {/* Visual panel */}
      <div className="relative hidden bg-gradient-hero lg:flex lg:flex-col lg:justify-between overflow-hidden">
        {/* Subtle geometric pattern */}
        <div className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `repeating-linear-gradient(
              0deg, transparent, transparent 60px, hsl(0 0% 100% / 1) 60px, hsl(0 0% 100% / 1) 61px
            ), repeating-linear-gradient(
              90deg, transparent, transparent 60px, hsl(0 0% 100% / 1) 60px, hsl(0 0% 100% / 1) 61px
            )`
          }}
        />

        <div className="relative p-10">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/10 backdrop-blur-sm ring-1 ring-white/20">
              <HardHat className="h-5 w-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-white">BuildHub</span>
          </Link>
        </div>

        <div className="relative space-y-8 p-10">
          <div className="space-y-4">
            <h2 className="text-4xl font-bold leading-[1.15] tracking-tight text-white">
              Build smarter.<br />
              <span className="text-amber-400">Track every<br />milestone.</span>
            </h2>
            <p className="max-w-sm text-sm text-white/70 leading-relaxed">
              BuildHub connects homeowners with vetted contractors and gives every
              project the visibility of an enterprise construction platform.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-3 max-w-sm">
            {STATS.map((s) => (
              <div key={s.v} className="rounded-xl border border-white/10 bg-white/5 p-3.5 backdrop-blur-sm">
                <div className="text-2xl font-bold text-white">{s.k}</div>
                <div className="mt-0.5 text-[11px] uppercase tracking-wide text-white/50">{s.v}</div>
              </div>
            ))}
          </div>

          <div className="space-y-3 max-w-sm">
            {TESTIMONIALS.map((t) => (
              <div key={t.author} className="rounded-xl border border-white/10 bg-white/5 p-4 backdrop-blur-sm">
                <p className="text-sm text-white/80 italic leading-relaxed">"{t.text}"</p>
                <div className="mt-2.5 flex items-center gap-2">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                  <span className="text-xs text-white/60">{t.author} · {t.role}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="relative p-10">
          <p className="text-xs text-white/40">© {new Date().getFullYear()} BuildHub. All rights reserved.</p>
        </div>
      </div>

      {/* Form panel */}
      <div className="flex items-center justify-center bg-background p-6 sm:p-12">
        <div className="w-full max-w-sm animate-slide-up">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
