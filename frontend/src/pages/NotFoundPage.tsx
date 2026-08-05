import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-3 bg-silver-100">
      <p className="text-lg font-medium text-brand-950">Pagina non trovata</p>
      <Link to="/" className="text-sm text-brand-600 underline">
        Torna alla home
      </Link>
    </div>
  );
}
