"use client";

import {
	type TasteDimension,
	type TasteKind,
	type TasteProfile,
	type TasteShift,
	type TasteStatus,
	getTasteProfile,
	getTasteShifts,
	getTasteStatus,
	startTasteRebuild,
	syncTaste,
} from "@/utils/api";
import { useCallback, useEffect, useState } from "react";

const BUCKETS = [
	{ id: "", label: "Any time" },
	{ id: "weekday_morning", label: "Weekday mornings" },
	{ id: "weekday_afternoon", label: "Weekday afternoons" },
	{ id: "weekday_evening", label: "Weekday evenings" },
	{ id: "saturday_morning", label: "Saturday mornings" },
	{ id: "sunday_morning", label: "Sunday mornings" },
	{ id: "weekend_afternoon", label: "Weekend afternoons" },
	{ id: "weekend_evening", label: "Weekend evenings" },
	{ id: "late_night", label: "Late at night" },
];

const FAMILIES = [
	{ id: "", label: "Everything", kinds: ["movie", "show"] },
	{ id: "genre", label: "Genres", kinds: ["movie", "show"] },
	{ id: "decade", label: "Decades", kinds: ["movie", "show"] },
	{ id: "runtime", label: "Length", kinds: ["movie", "show"] },
	{ id: "country", label: "Countries", kinds: ["movie"] },
	{ id: "director", label: "Directors", kinds: ["movie"] },
	{ id: "actor", label: "Actors", kinds: ["movie", "show"] },
];

const SHIFT_WINDOWS = [30, 90, 180];

function pct(x: number): string {
	return `${(x * 100).toFixed(x < 0.01 ? 2 : 1)}%`;
}

function label(dimension: string): { family: string; value: string } {
	const i = dimension.indexOf(":");
	const family = dimension.slice(0, i);
	const raw = dimension.slice(i + 1);
	return { family, value: raw.replace(/\b\w/g, (c) => c.toUpperCase()) };
}

function DimensionRow({ d }: { d: TasteDimension }) {
	const { family, value } = label(d.dimension);
	const positive = d.score >= 0;
	return (
		<li
			className="flex items-center gap-3 py-1.5"
			title={`${pct(d.watch_share)} of your watching vs ${pct(d.library_share)} of your library (${d.library_count} items)`}
		>
			<span className="w-20 shrink-0 text-[10px] uppercase tracking-wide text-slate-500">
				{family}
			</span>
			<span className="flex-1 min-w-0 truncate text-sm text-slate-200">{value}</span>
			<span className="relative h-2 w-28 shrink-0 rounded-full bg-slate-800">
				<span className="absolute left-1/2 top-0 h-2 w-px bg-slate-600" />
				<span
					className={`absolute top-0 h-2 rounded-full ${positive ? "bg-emerald-400" : "bg-rose-400"}`}
					style={{
						width: `${Math.min(Math.abs(d.score), 1) * 50}%`,
						left: positive ? "50%" : undefined,
						right: positive ? undefined : "50%",
					}}
				/>
			</span>
			<span
				className={`w-12 shrink-0 text-right text-xs tabular-nums ${positive ? "text-emerald-300" : "text-rose-300"}`}
			>
				{d.score > 0 ? "+" : ""}
				{d.score.toFixed(2)}
			</span>
		</li>
	);
}

function Panel({ title, rows, empty }: { title: string; rows: TasteDimension[]; empty: string }) {
	return (
		<section className="rounded-lg border border-slate-600/50 bg-slate-900/40 p-4">
			<h2 className="mb-2 text-sm font-semibold text-slate-200">{title}</h2>
			{rows.length === 0 ? (
				<p className="text-sm text-slate-500">{empty}</p>
			) : (
				<ul className="divide-y divide-slate-800">
					{rows.map((d) => (
						<DimensionRow key={d.dimension} d={d} />
					))}
				</ul>
			)}
		</section>
	);
}

function Chips<T extends string>({
	options,
	value,
	onChange,
}: {
	options: { id: T; label: string }[];
	value: T;
	onChange: (v: T) => void;
}) {
	return (
		<div className="flex flex-wrap gap-1.5">
			{options.map((o) => (
				<button
					key={o.id}
					type="button"
					onClick={() => onChange(o.id)}
					className={`rounded-full border px-3 py-1 text-xs transition-colors ${
						value === o.id
							? "border-amber/60 bg-amber/20 text-amber"
							: "border-slate-600/50 bg-slate-800 text-slate-300 hover:bg-slate-700"
					}`}
				>
					{o.label}
				</button>
			))}
		</div>
	);
}

export function TasteClient() {
	const [status, setStatus] = useState<TasteStatus | null>(null);
	const [kind, setKind] = useState<TasteKind>("movie");
	const [bucket, setBucket] = useState("");
	const [family, setFamily] = useState("");
	const [profile, setProfile] = useState<TasteProfile | null>(null);
	const [shiftDays, setShiftDays] = useState(90);
	const [shifts, setShifts] = useState<TasteShift[]>([]);
	const [err, setErr] = useState<string | null>(null);
	const [busy, setBusy] = useState(false);
	const [note, setNote] = useState<string | null>(null);

	const refreshStatus = useCallback(async () => {
		try {
			setStatus(await getTasteStatus());
		} catch (e) {
			setErr(e instanceof Error ? e.message : "Could not reach the backend");
		}
	}, []);

	useEffect(() => {
		void refreshStatus();
	}, [refreshStatus]);

	// Poll while a rebuild is running.
	const running = status?.running ?? false;
	useEffect(() => {
		if (!running) return;
		const id = setInterval(() => void refreshStatus(), 2000);
		return () => clearInterval(id);
	}, [running, refreshStatus]);

	const built = status?.built ?? false;
	const finishedAt = status?.rebuilt_at;

	useEffect(() => {
		if (!built) return;
		let cancelled = false;
		getTasteProfile({ kind, bucket: bucket || null, prefix: family || null, top: 14 })
			.then((p) => {
				if (!cancelled) setProfile(p);
			})
			.catch((e: Error) => !cancelled && setErr(e.message));
		return () => {
			cancelled = true;
		};
		// finishedAt: reload after a rebuild completes
	}, [built, kind, bucket, family, finishedAt]);

	useEffect(() => {
		if (!built) return;
		let cancelled = false;
		getTasteShifts({ kind, days: shiftDays, prefix: "genre", top: 8 })
			.then((r) => {
				if (!cancelled) setShifts(r.shifts ?? []);
			})
			.catch((e: Error) => !cancelled && setErr(e.message));
		return () => {
			cancelled = true;
		};
	}, [built, kind, shiftDays, finishedAt]);

	const handleRebuild = async (refreshBaseline = false) => {
		setBusy(true);
		setErr(null);
		setNote(null);
		try {
			await startTasteRebuild({ refresh_baseline: refreshBaseline });
			await refreshStatus();
		} catch (e) {
			setErr(e instanceof Error ? e.message : "Could not start the rebuild");
		} finally {
			setBusy(false);
		}
	};

	const handleSync = async () => {
		setBusy(true);
		setErr(null);
		setNote(null);
		try {
			const r = await syncTaste();
			setNote(r.events_new ? `Folded in ${r.events_new} new view(s).` : "Already up to date.");
			await refreshStatus();
		} catch (e) {
			setErr(e instanceof Error ? e.message : "Sync failed");
		} finally {
			setBusy(false);
		}
	};

	const progress = status?.progress;
	const progressPct =
		progress?.total && progress.total > 0
			? Math.min(100, ((progress.done ?? 0) / progress.total) * 100)
			: null;
	const families = FAMILIES.filter((f) => f.kinds.includes(kind));

	return (
		<div className="max-w-5xl mx-auto p-6 flex flex-col gap-6">
			<div className="flex flex-wrap items-start justify-between gap-4">
				<div>
					<h1 className="text-3xl font-bold text-slate-100">Your taste</h1>
					<p className="text-slate-400 text-sm mt-1 max-w-2xl">
						Learned from your Plex watch history. A score compares what you watch with what is in
						your library: positive means you pick it more than its share of the library, negative
						means it is there but you pass it over.
					</p>
				</div>
				{built && (
					<div className="flex gap-2">
						<button
							type="button"
							disabled={busy || running}
							onClick={() => void handleSync()}
							className="px-4 py-2 rounded-lg bg-slate-700 text-slate-100 text-sm font-medium hover:bg-slate-600 border border-slate-600/50 disabled:opacity-50"
						>
							Update from latest viewing
						</button>
						<button
							type="button"
							disabled={busy || running}
							onClick={() => void handleRebuild(true)}
							className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 text-sm hover:bg-slate-700 border border-slate-600/50 disabled:opacity-50"
						>
							Rebuild
						</button>
					</div>
				)}
			</div>

			{err && <p className="text-red-400 text-sm">{err}</p>}
			{note && <p className="text-emerald-300 text-sm">{note}</p>}

			{status && !built && !running && (
				<div className="rounded-lg border border-amber/30 bg-amber/5 p-8 text-center">
					<p className="text-slate-200 font-medium">No taste profile yet</p>
					<p className="text-slate-400 text-sm mt-1 max-w-xl mx-auto">
						This reads your whole Plex watch history and surveys your library to learn what you
						gravitate toward. It takes a couple of minutes on a large library, runs in the
						background, and only reads from Plex.
					</p>
					{progress?.phase === "error" && progress.message && (
						<p className="text-red-400 text-sm mt-3">Last attempt failed: {progress.message}</p>
					)}
					<button
						type="button"
						disabled={busy}
						onClick={() => void handleRebuild()}
						className="mt-4 px-5 py-2.5 rounded-lg bg-amber text-slate-900 text-sm font-semibold hover:bg-amber/90 disabled:opacity-60"
					>
						Build my profile
					</button>
				</div>
			)}

			{running && (
				<div className="rounded-lg border border-slate-600/50 bg-slate-900/40 p-5">
					<p className="text-slate-200 text-sm">{progress?.message || "Working..."}</p>
					<div className="mt-3 h-2 rounded-full bg-slate-800 overflow-hidden">
						<div
							className={`h-full bg-amber transition-all ${progressPct === null ? "w-1/3 animate-pulse" : ""}`}
							style={progressPct === null ? undefined : { width: `${progressPct}%` }}
						/>
					</div>
				</div>
			)}

			{built && (
				<>
					<div className="flex flex-col gap-3 rounded-lg border border-slate-600/50 bg-slate-900/40 p-4">
						<div className="flex flex-wrap items-center gap-x-6 gap-y-2">
							<Chips
								options={[
									{ id: "movie" as TasteKind, label: "Movies" },
									{ id: "show" as TasteKind, label: "TV shows" },
								]}
								value={kind}
								onChange={(k) => {
									setKind(k);
									if (!FAMILIES.find((f) => f.id === family)?.kinds.includes(k)) setFamily("");
								}}
							/>
						</div>
						<div>
							<p className="mb-1.5 text-[10px] uppercase tracking-wide text-slate-500">When</p>
							<Chips options={BUCKETS} value={bucket} onChange={setBucket} />
						</div>
						<div>
							<p className="mb-1.5 text-[10px] uppercase tracking-wide text-slate-500">Show</p>
							<Chips options={families} value={family} onChange={setFamily} />
						</div>
					</div>

					{profile?.success && (
						<div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
							<Panel
								title="You gravitate toward"
								rows={profile.likes}
								empty={
									bucket
										? "Not enough viewing at this time of the week to say."
										: "Nothing stands out yet."
								}
							/>
							<Panel
								title="You tend to pass over"
								rows={profile.dislikes}
								empty="Nothing stands out yet."
							/>
						</div>
					)}

					<section className="rounded-lg border border-slate-600/50 bg-slate-900/40 p-4">
						<div className="flex flex-wrap items-center justify-between gap-2 mb-2">
							<h2 className="text-sm font-semibold text-slate-200">
								Lately: genres moving in your {kind === "movie" ? "movies" : "TV"}
							</h2>
							<Chips
								options={SHIFT_WINDOWS.map((d) => ({ id: String(d), label: `${d} days` }))}
								value={String(shiftDays)}
								onChange={(v) => setShiftDays(Number(v))}
							/>
						</div>
						{shifts.length === 0 ? (
							<p className="text-sm text-slate-500">
								No genre has moved meaningfully in this window. Try a longer one.
							</p>
						) : (
							<ul className="divide-y divide-slate-800">
								{shifts.map((s) => (
									<li
										key={s.dimension}
										className="flex items-center justify-between py-1.5 text-sm"
									>
										<span className="text-slate-200">{label(s.dimension).value}</span>
										<span className={s.delta > 0 ? "text-emerald-300" : "text-rose-300"}>
											{s.delta > 0 ? "more" : "less"}
											{s.new ? " (new)" : ""}{" "}
											<span className="text-xs tabular-nums text-slate-500">
												{s.delta > 0 ? "+" : ""}
												{s.delta.toFixed(2)}
											</span>
										</span>
									</li>
								))}
							</ul>
						)}
					</section>

					<p className="text-[11px] text-slate-500">
						Built from {status?.events.toLocaleString()} views across{" "}
						{status?.library_items.toLocaleString()} library items; history up to{" "}
						{status?.last_history_ts ?? "unknown"}. Recent viewing counts more (one-year half-life).
						Hover a row for the numbers behind it.
					</p>
				</>
			)}
		</div>
	);
}
