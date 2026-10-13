"use client";

import { getLlmOnboarding } from "@/utils/api";
import { useEffect, useState } from "react";

export function LlmOnboardingCard() {
	const [data, setData] = useState<Record<string, unknown> | null>(null);

	useEffect(() => {
		let cancelled = false;
		getLlmOnboarding()
			.then((d) => {
				if (!cancelled) setData(d as Record<string, unknown>);
			})
			.catch(() => {});
		return () => {
			cancelled = true;
		};
	}, []);

	if (!data) return null;
	const recommended = typeof data.recommended === "string" ? data.recommended : null;
	const keys = Object.keys(data).filter((k) => k !== "recommended");
	if (!recommended && keys.length === 0) return null;

	return (
		<div
			data-testid="llm-onboarding"
			className="mb-4 rounded-lg border border-amber/30 bg-amber/5 p-4"
		>
			<p className="text-sm text-slate-200 font-medium">Getting started with AI features</p>
			{recommended && <p className="text-sm text-slate-400 mt-1">{recommended}</p>}
			{keys.slice(0, 4).map((k) => (
				<p key={k} className="text-xs text-slate-500 mt-1">
					{k}: {String(data[k] ?? "")}
				</p>
			))}
		</div>
	);
}
