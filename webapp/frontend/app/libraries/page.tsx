import { ErrorBanner } from "@/components/ui/error-banner";
import { listLibraries } from "@/utils/api";
import Link from "next/link";

function librarySectionId(lib: { id?: string; key?: string }): string {
	return String(lib.id ?? lib.key ?? "");
}

export default async function LibrariesPage({
	searchParams,
}: {
	searchParams: Promise<{ library_id?: string }>;
}) {
	const { library_id: activeLibraryId } = await searchParams;
	let data: {
		success?: boolean;
		data?: { key?: string; title?: string; type?: string }[];
		error?: string;
	} | null = null;
	try {
		data = await listLibraries();
	} catch {
		data = null;
	}

	const libraries = (data?.data ?? []) as { key?: string; title?: string; type?: string }[];

	return (
		<div className="container mx-auto p-6">
			<h1 className="text-3xl font-bold mb-6 text-slate-100">Libraries</h1>
			{data === null ? (
				<ErrorBanner
					title="Could not load libraries"
					message="Backend unavailable or PLEX_TOKEN not configured."
					hint="Set PLEX_TOKEN in webapp/backend/.env"
				/>
			) : !data.success ? (
				<ErrorBanner
					title="Error"
					message={String(data.error ?? "Unknown error")}
					hint="Check PLEX_TOKEN and PLEX_URL in backend/.env"
				/>
			) : (
				<div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
					{libraries.map(
						(lib: { id?: string; key?: string; title?: string; type?: string }, index: number) => {
							const sid = librarySectionId(lib);
							const isMovie = (lib.type ?? "").toLowerCase() === "movie";
							const href = isMovie
								? `/movies?library_id=${encodeURIComponent(sid)}`
								: `/search?library_id=${encodeURIComponent(sid)}`;
							const isActive =
								activeLibraryId != null && activeLibraryId !== "" && activeLibraryId === sid;
							return (
								<Link
									key={sid || `lib-${index}`}
									href={href}
									className={`relative block p-6 rounded-xl glass-panel border transition-colors ${
										isActive
											? "border-amber/50 ring-1 ring-amber/30"
											: "border-slate-600/50 hover:border-amber/40"
									}`}
								>
									{isActive && (
										<span className="absolute top-3 right-3 text-xs font-semibold uppercase tracking-wide px-2 py-0.5 rounded-md bg-amber/20 text-amber border border-amber/40">
											Active
										</span>
									)}
									<p className="text-xl font-semibold text-slate-100 pr-16">
										{lib.title ?? "Library"}
									</p>
									<p className="text-sm text-slate-400">{lib.type ?? ""}</p>
								</Link>
							);
						},
					)}
				</div>
			)}
		</div>
	);
}
