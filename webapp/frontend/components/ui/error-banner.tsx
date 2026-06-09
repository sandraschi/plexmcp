import Link from "next/link";

interface ErrorBannerProps {
	title: string;
	message: string;
	hint?: string;
	actionHref?: string;
	actionLabel?: string;
}

export function ErrorBanner({ title, message, hint, actionHref, actionLabel }: ErrorBannerProps) {
	return (
		<div className="p-4 rounded-lg bg-red-900/30 border border-red-700">
			<h3 className="text-sm font-medium text-red-200">{title}</h3>
			<p className="text-sm text-slate-300 mt-1">{message}</p>
			{hint && <p className="text-xs text-slate-400 mt-2">{hint}</p>}
			{actionHref && actionLabel && (
				<Link
					href={actionHref}
					className="inline-block mt-3 text-sm font-medium text-amber hover:text-amber/80 underline"
				>
					{actionLabel}
				</Link>
			)}
		</div>
	);
}
