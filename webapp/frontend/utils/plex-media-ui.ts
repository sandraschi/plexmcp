/** Plex thumb/art path (e.g. /library/metadata/1/thumb/1) → image proxy URL. */
export function plexImageUrl(path: string | null | undefined): string | null {
	if (!path || typeof path !== "string") return null;
	const p = path.startsWith("/") ? path.slice(1) : path;
	return p ? `/image/${p}` : null;
}

export function ratingKeyFromItem(
	item: Record<string, unknown> | null | undefined,
): string | null {
	if (!item) return null;
	const rk = item.ratingKey ?? item.rating_key ?? item.id;
	if (rk == null || rk === "") return null;
	return String(rk);
}

/** Plex Web "details" deep link (requires configured PLEX_URL / app.plex.tv-style base). */
export function plexWebDetailsUrl(
	plexUrl: string | null | undefined,
	ratingKey: string,
): string | null {
	if (!plexUrl?.trim() || !ratingKey) return null;
	const base = plexUrl.replace(/\/$/, "");
	const key = `/library/metadata/${ratingKey}`;
	return `${base}/web/index.html#!/details?key=${encodeURIComponent(key)}`;
}

/**
 * Plex duration may be milliseconds (raw API) or minutes (formatted from get_details).
 */
export function formatRuntimeMinutes(
	duration: number | null | undefined,
): string | null {
	if (duration == null || !Number.isFinite(Number(duration))) return null;
	const d = Number(duration);
	const minutes = d > 100_000 ? d / 60_000 : d;
	if (!Number.isFinite(minutes) || minutes <= 0) return null;
	const h = Math.floor(minutes / 60);
	const m = Math.round(minutes % 60);
	if (h > 0) return `${h}h ${m}m`;
	return `${m} min`;
}

/** Heuristics: HTML error pages or RSC payloads must never be shown as plot text. */
const NON_PLOT_MARKERS: RegExp[] = [
	/<!DOCTYPE/i,
	/<\s*html[\s>]/i,
	/self\.__next_f/,
	/"pagePath"\s*:\s*"\/404"/,
	/_next\/static/,
	/next-error-h1/,
	/<\/script>/i,
];

/**
 * Returns a short plain-text snippet for cards/modals, or null if missing or unusable.
 * Only accepts real strings — objects/arrays are ignored (avoids huge JSON in the UI).
 */
export function safeMediaBlurb(
	value: unknown,
	maxChars: number,
): string | null {
	if (value == null) return null;
	if (typeof value !== "string") return null;
	const t = value.trim().replace(/\s+/g, " ");
	if (!t) return null;
	if (t.length > 60_000) return null;
	for (const re of NON_PLOT_MARKERS) {
		if (re.test(t)) return null;
	}
	if (t.length <= maxChars) return t;
	return `${t.slice(0, Math.max(1, maxChars - 1)).trimEnd()}…`;
}
