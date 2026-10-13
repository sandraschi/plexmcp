"use client";

import {
	type TasteKind,
	getTasteRank,
	getTasteScore,
	getTasteTemporal,
	listLibraries,
} from "@/utils/api";
import Link from "next/link";
import { useEffect, useState } from "react";

export function TasteRankPanel({ kind }: { kind: TasteKind }) {
	const [libraries, setLibraries] = useState<{ id: string; title: string; type: string }[]>([]);
	const [libraryId, setLibraryId] = useState("");
	const [limit, setLimit] = useState("25");
	const [unwatchedOnly, setUnwatchedOnly] = useState(true);
	const [items, setItems] = useState<
		{ rating_key: string; title?: string; year?: number | null; score?: number }[]
	>([]);
	const [rankMsg, setRankMsg] = useState<string | null>(null);
	const [ranking, setRanking] = useState(false);
	const [scoreKey, setScoreKey] = useState("");
	const [scoreOut, setScoreOut] = useState<string | null>(null);
	const [temporalBucket, setTemporalBucket] = useState("weekend_evening");
	const [temporalSummary, setTemporalSummary] = useState<string | null>(null);

	useEffect(() => {
		let cancelled = false;
		listLibraries()
			.then((res) => {
				if (cancelled) return;
				const libs = (res?.data ?? []) as { id: unknown; title: unknown; type: unknown }[];
				const mapped = libs
					.filter((l) => typeof l.id !== "undefined")
					.map((l) => ({
						id: String(l.id),
						title: String(l.title ?? "Library"),
						type: String(l.type ?? ""),
					}));
				setLibraries(mapped);
				if (!libraryId && mapped.length > 0) {
					const match =
						mapped.find((l) => l.type === (kind === "show" ? "show" : "movie")) ?? mapped[0];
					setLibraryId(match.id);
				}
			})
			.catch(() => {});
		return () => {
			cancelled = true;
		};
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [kind]);

	const runRank = async () => {
		if (!libraryId) {
			setRankMsg("Pick a library first.");
			return;
		}
		setRanking(true);
		setRankMsg(null);
		try {
			const res = await getTasteRank({
				library_id: libraryId,
				limit: Number(limit) || 25,
				unwatched_only: unwatchedOnly,
			});
			if (!res.built) {
				setRankMsg(res.message ?? "Profile not built.");
				setItems([]);
				return;
			}
			const list = (res.data ?? res.items ?? []) as typeof items;
			setItems(list);
			setRankMsg(list.length === 0 ? "Nothing ranked — library may be fully watched." : null);
		} catch (e) {
			setRankMsg(e instanceof Error ? e.message : "Rank failed");
		} finally {
			setRanking(false);
		}
	};

	const runScore = async () => {
		const rk = scoreKey.trim();
		if (!rk) return;
		try {
			const res = await getTasteScore(rk);
			setScoreOut(
				res.built
					? `Score: ${typeof res.score === "number" ? res.score.toFixed(2) : JSON.stringify(res.detail ?? res)}`
					: (res.message ?? "Profile not built."),
			);
		} catch (e) {
			setScoreOut(e instanceof Error ? e.message : "Score failed");
		}
	};

	const runTemporal = async () => {
		try {
			const p = await getTasteTemporal(temporalBucket, { kind, top: 10 });
			setTemporalSummary(
				p.built
					? `${p.likes.length} likes / ${p.dislikes.length} dislikes at ${temporalBucket} (${p.library_items} items)`
					: (p.message ?? "Profile not built."),
			);
		} catch (e) {
			setTemporalSummary(e instanceof Error ? e.message : "Temporal lookup failed");
		}
	};

	return (
		<section
			aria-label="Taste recommendations"
			className="rounded-lg border border-slate-600/50 bg-slate-900/40 p-4 flex flex-col gap-4"
		>
			<h2 className="text-sm font-semibold text-slate-200">Recommendations from your taste</h2>
			<div className="flex flex-wrap items-end gap-3">
				<label className="text-xs text-slate-400">
					Library
					<select
						value={libraryId}
						onChange={(e) => setLibraryId(e.target.value)}
						data-testid="taste-rank-library"
						className="ml-2 px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-600 text-slate-100 text-sm"
					>
						{libraries.map((l) => (
							<option key={l.id} value={l.id}>
								{l.title} ({l.type || "?"})
							</option>
						))}
					</select>
				</label>
				<label className="text-xs text-slate-400">
					Limit
					<select
						value={limit}
						onChange={(e) => setLimit(e.target.value)}
						data-testid="taste-rank-limit"
						className="ml-2 px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-600 text-slate-100 text-sm"
					>
						{["10", "25", "50"].map((n) => (
							<option key={n} value={n}>
								{n}
							</option>
						))}
					</select>
				</label>
				<label className="flex items-center gap-2 text-xs text-slate-300">
					<input
						type="checkbox"
						checked={unwatchedOnly}
						onChange={(e) => setUnwatchedOnly(e.target.checked)}
						data-testid="taste-rank-unwatched"
					/>
					Unwatched only
				</label>
				<button
					type="button"
					onClick={() => void runRank()}
					disabled={ranking}
					data-testid="taste-rank-run"
					className="px-4 py-2 rounded-lg bg-amber text-slate-950 text-sm font-semibold hover:bg-amber/90 disabled:opacity-60"
				>
					{ranking ? "Ranking…" : "Rank this library"}
				</button>
			</div>
			{rankMsg && <p className="text-sm text-slate-400">{rankMsg}</p>}
			{items.length > 0 && (
				<ul data-testid="taste-rank-results" className="divide-y divide-slate-800">
					{items.slice(0, 25).map((it) => (
						<li
							key={it.rating_key}
							className="flex items-center justify-between gap-2 py-1.5 text-sm"
						>
							<Link
								href={`/media?ratingKey=${encodeURIComponent(it.rating_key)}`}
								className="text-slate-200 hover:text-amber truncate"
							>
								{it.title ?? it.rating_key}
								{it.year ? ` (${it.year})` : ""}
							</Link>
							<span className="text-xs tabular-nums text-slate-400 shrink-0">
								{typeof it.score === "number" ? it.score.toFixed(2) : ""}
							</span>
						</li>
					))}
				</ul>
			)}
			<div className="flex flex-wrap items-end gap-3 pt-2 border-t border-slate-800">
				<label className="text-xs text-slate-400">
					Score a rating key
					<input
						value={scoreKey}
						onChange={(e) => setScoreKey(e.target.value)}
						placeholder="e.g. 12345"
						data-testid="taste-score-key"
						className="ml-2 px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-600 text-slate-100 text-sm w-36"
					/>
				</label>
				<button
					type="button"
					onClick={() => void runScore()}
					data-testid="taste-score-run"
					className="px-4 py-2 rounded-lg bg-slate-700 text-slate-100 text-sm hover:bg-slate-600 border border-slate-600/50"
				>
					Score
				</button>
				{scoreOut && <span className="text-xs text-slate-400">{scoreOut}</span>}
			</div>
			<div className="flex flex-wrap items-end gap-3 pt-2 border-t border-slate-800">
				<label className="text-xs text-slate-400">
					Time bucket
					<select
						value={temporalBucket}
						onChange={(e) => setTemporalBucket(e.target.value)}
						data-testid="taste-temporal-bucket"
						className="ml-2 px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-600 text-slate-100 text-sm"
					>
						{[
							"weekday_evening",
							"weekend_evening",
							"sunday_morning",
							"late_night",
							"saturday_morning",
						].map((b) => (
							<option key={b} value={b}>
								{b}
							</option>
						))}
					</select>
				</label>
				<button
					type="button"
					onClick={() => void runTemporal()}
					data-testid="taste-temporal-run"
					className="px-4 py-2 rounded-lg bg-slate-700 text-slate-100 text-sm hover:bg-slate-600 border border-slate-600/50"
				>
					Check bucket
				</button>
				{temporalSummary && <span className="text-xs text-slate-400">{temporalSummary}</span>}
			</div>
		</section>
	);
}
