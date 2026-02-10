interface ErrorBannerProps {
  title: string;
  message: string;
  hint?: string;
}

export function ErrorBanner({ title, message, hint }: ErrorBannerProps) {
  return (
    <div className="p-4 rounded-lg bg-red-900/30 border border-red-700">
      <h3 className="font-semibold text-red-200">{title}</h3>
      <p className="text-sm text-slate-300 mt-1">{message}</p>
      {hint && <p className="text-xs text-slate-400 mt-2">{hint}</p>}
    </div>
  );
}
