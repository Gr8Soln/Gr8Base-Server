import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { ArrowLeft, Loader2 } from "lucide-react";
import { CarosMark } from "@/components/caros/CarosMark";
import { useAuth } from "@/lib/auth";

export const Route = createFileRoute("/auth/login")({
  head: () => ({ meta: [{ title: "Sign in · CAROS" }] }),
  component: LoginPage,
});

function GoogleLogo() {
  return (
    <svg className="h-4 w-4" viewBox="0 0 24 24">
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
    </svg>
  );
}

function LoginPage() {
  const { user, loading, signIn } = useAuth();
  const [err, setErr] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (user) navigate({ to: "/dashboard" as any });
  }, [user, navigate]);

  const handle = async () => {
    setErr(null);
    try { await signIn(); }
    catch { setErr("Authentication failed. Please try again."); }
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center px-4 bg-background">
      <div className="absolute inset-0 bg-grid bg-grid-fade pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[500px] w-[500px] rounded-full bg-emerald/5 blur-3xl pointer-events-none" />

      <div className="relative w-full max-w-[420px] rounded-2xl border border-border bg-surface/90 backdrop-blur p-8 md:p-10 animate-fade-up">
        <CarosMark size="md" className="mb-8" />
        <h1 className="text-2xl font-bold tracking-tight text-foreground">Sign in to CAROS</h1>
        <p className="mt-1.5 text-sm text-muted-foreground">Your career intelligence platform</p>

        {err && (
          <div className="mt-6 rounded-lg border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
            {err}
          </div>
        )}

        <button
          onClick={handle}
          disabled={loading}
          className="mt-8 w-full inline-flex items-center justify-center gap-2.5 rounded-lg bg-white text-zinc-900 px-4 py-3 text-sm font-medium shadow-sm transition-all hover:bg-zinc-100 disabled:opacity-70"
        >
          {loading ? (
            <><Loader2 className="h-4 w-4 animate-spin" /> Connecting…</>
          ) : (
            <><GoogleLogo /> Continue with Google</>
          )}
        </button>

        <div className="my-6 flex items-center gap-3">
          <div className="h-px flex-1 bg-border" />
          <div className="text-[11px] uppercase tracking-wider text-muted-foreground">Secure authentication via Google OAuth</div>
          <div className="h-px flex-1 bg-border" />
        </div>

        <p className="text-xs text-muted-foreground text-center">
          By continuing, you agree to our Terms of Service.
        </p>

        <Link to="/" className="mt-8 inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors">
          <ArrowLeft className="h-3 w-3" /> Back to caros.io
        </Link>
      </div>
    </div>
  );
}
