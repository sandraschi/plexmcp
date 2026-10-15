"use client";

import { ErrorBanner } from "@/components/ui/error-banner";
import { type SkillPrompt, type SkillResource, getSkills } from "@/utils/api";
import { BACKEND_DOWN_HINT } from "@/utils/config-hints";
import { BookMarked, Boxes, Sparkles } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

function PromptCard({ prompt }: { prompt: SkillPrompt }) {
	return (
		<li
			data-testid={`skill-prompt-${prompt.name}`}
			className="rounded-xl glass-panel border border-slate-600/50 p-4"
		>
			<div className="flex items-center gap-2 mb-1">
				<Sparkles className="w-4 h-4 text-amber shrink-0" />
				<span className="font-medium text-slate-200 text-sm">{prompt.title}</span>
			</div>
			<p className="text-sm text-slate-400 mb-2">{prompt.description}</p>
			<p className="text-xs text-slate-500 mb-2">Use when: {prompt.use_when}</p>
			<code className="text-xs text-amber/90 bg-slate-800/80 px-1.5 py-0.5 rounded">
				{prompt.uri}
			</code>
		</li>
	);
}

function ResourceCard({ resource }: { resource: SkillResource }) {
	return (
		<li
			data-testid={`skill-resource-${resource.title}`}
			className="rounded-xl glass-panel border border-slate-600/50 p-4"
		>
			<div className="flex items-center gap-2 mb-1">
				<Boxes className="w-4 h-4 text-amber shrink-0" />
				<span className="font-medium text-slate-200 text-sm">{resource.title}</span>
			</div>
			<p className="text-sm text-slate-400 mb-2">{resource.description}</p>
			<code className="text-xs text-amber/90 bg-slate-800/80 px-1.5 py-0.5 rounded">
				{resource.uri}
			</code>
		</li>
	);
}

export default function SkillsPage() {
	const [prompts, setPrompts] = useState<SkillPrompt[] | null>(null);
	const [resources, setResources] = useState<SkillResource[] | null>(null);
	const [source, setSource] = useState<string>("");
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	const load = async () => {
		setLoading(true);
		setError(null);
		try {
			const data = await getSkills();
			setPrompts(data.prompts ?? []);
			setResources(data.resources ?? []);
			setSource(data.source ?? "");
		} catch (e) {
			setError(e instanceof Error ? e.message : String(e));
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		load();
	}, []);

	return (
		<div className="container mx-auto p-6 max-w-6xl" data-testid="skills-page">
			<div className="flex items-start gap-3 mb-2">
				<BookMarked className="w-7 h-7 text-amber shrink-0 mt-0.5" />
				<div>
					<h1 className="text-3xl font-bold text-slate-100">Skills</h1>
					<p className="text-slate-500 mt-1 text-sm">
						Expert prompts and resources the chat uses first. Same catalog the MCP server registers
						— mirrored from <code className="text-amber/80">{source}</code>.
					</p>
				</div>
				<Link
					href="/chat"
					className="ml-auto inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-amber text-slate-950 text-sm font-semibold hover:bg-amber/90 transition-colors shrink-0"
				>
					Open chat
				</Link>
			</div>

			{loading ? (
				<p className="text-slate-500 mt-6" data-testid="skills-loading">
					Loading skills…
				</p>
			) : error ? (
				<div className="mt-6" data-testid="skills-error">
					<ErrorBanner title="Skills unavailable" message={error} hint={BACKEND_DOWN_HINT} />
					<button
						type="button"
						onClick={load}
						className="mt-3 px-4 py-2 rounded-lg border border-slate-600 text-sm text-slate-200 hover:border-amber/40 hover:text-amber transition-colors"
					>
						Retry
					</button>
				</div>
			) : (prompts?.length ?? 0) + (resources?.length ?? 0) === 0 ? (
				<p className="text-sm text-slate-500 mt-6" data-testid="skills-empty">
					No skills registered on the backend.
				</p>
			) : (
				<div className="mt-6 space-y-6">
					<section aria-label="Prompt skills">
						<h2 className="text-sm uppercase tracking-wide text-slate-500 mb-3">
							Prompts · {prompts?.length ?? 0}
						</h2>
						<ul className="grid sm:grid-cols-2 gap-4">
							{(prompts ?? []).map((p) => (
								<PromptCard key={p.uri} prompt={p} />
							))}
						</ul>
					</section>
					<section aria-label="Skill resources">
						<h2 className="text-sm uppercase tracking-wide text-slate-500 mb-3">
							Resources · {resources?.length ?? 0}
						</h2>
						<ul className="grid sm:grid-cols-2 gap-4">
							{(resources ?? []).map((r) => (
								<ResourceCard key={r.uri} resource={r} />
							))}
						</ul>
					</section>
				</div>
			)}
		</div>
	);
}
