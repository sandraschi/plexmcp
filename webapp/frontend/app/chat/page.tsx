"use client";

import { API_BASE } from "@/utils/api";
import { useEffect, useRef, useState } from "react";

interface Message {
	role: "user" | "assistant";
	content: string;
}

const PERSONALITIES = [
	{ id: "default", label: "Default", preprompt: "" },
	{
		id: "plex",
		label: "Plex expert",
		preprompt:
			"You are a Plex Media Server expert. Give accurate, practical answers about libraries, clients, transcoding, remote access, and users. If you lack live server data, say so and suggest what to check in Plex settings or logs.",
	},
	{
		id: "anime",
		label: "Anime curator",
		preprompt:
			"You specialize in anime and serialized TV: seasons, watch order, OVAs, and cataloging in Plex. Be enthusiastic but precise; distinguish remakes and alternate cuts when relevant.",
	},
	{
		id: "critic",
		label: "Film critic",
		preprompt:
			"You discuss film and TV like a thoughtful critic: themes, direction, pacing, and craft. Avoid spoilers unless the user asks; stay constructive.",
	},
	{
		id: "theater",
		label: "Home theater",
		preprompt:
			"You advise on playback quality: HDR, audio codecs, direct play vs transcode, subtitles, and client settings in a home theater context.",
	},
	{
		id: "librarian",
		label: "Media librarian",
		preprompt:
			"You focus on organizing a Plex library: naming, collections, genres, parental controls, and consistent metadata workflows.",
	},
	{
		id: "casual",
		label: "Casual",
		preprompt:
			"You are a friendly media enthusiast. Chat naturally about movies, shows, and recommendations.",
	},
];

export default function ChatPage() {
	const [messages, setMessages] = useState<Message[]>([]);
	const [input, setInput] = useState("");
	const [loading, setLoading] = useState(false);
	const [refining, setRefining] = useState(false);
	const [model, setModel] = useState("llama3.2");
	const [models, setModels] = useState<string[]>([]);
	const [personality, setPersonality] = useState("default");
	const bottomRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		fetch(`${API_BASE}/api/llm/models`)
			.then((r) => r.json())
			.then((d: { models?: string[] }) => setModels(d.models ?? []))
			.catch(() => {});
	}, []);

	useEffect(() => {
		bottomRef.current?.scrollIntoView({ behavior: "smooth" });
	}, [messages]);

	const handleRefine = async () => {
		if (!input.trim() || refining) return;
		setRefining(true);
		try {
			const res = await fetch(`${API_BASE}/api/llm/refine`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ text: input.trim(), model }),
			});
			const data = await res.json();
			if (data.refined) setInput(data.refined);
		} catch {
			// ignore
		} finally {
			setRefining(false);
		}
	};

	const handleExport = (format: "md" | "json") => {
		const blob =
			format === "md"
				? new Blob(
						[
							messages
								.map((m) =>
									m.role === "user" ? `**You:** ${m.content}` : `**Assistant:** ${m.content}`,
								)
								.join("\n\n"),
						],
						{ type: "text/markdown" },
					)
				: new Blob([JSON.stringify({ messages }, null, 2)], {
						type: "application/json",
					});
		const url = URL.createObjectURL(blob);
		const a = document.createElement("a");
		a.href = url;
		a.download = `plex-chat-${Date.now()}.${format}`;
		a.click();
		URL.revokeObjectURL(url);
	};

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!input.trim() || loading) return;
		const userMsg: Message = { role: "user", content: input.trim() };
		setMessages((m) => [...m, userMsg]);
		setInput("");
		setLoading(true);

		const preprompt = PERSONALITIES.find((p) => p.id === personality)?.preprompt ?? "";
		const messagesToSend = preprompt
			? [{ role: "system" as const, content: preprompt }, ...messages, userMsg]
			: [...messages, userMsg];
		try {
			const res = await fetch(`${API_BASE}/api/llm/chat`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					messages: messagesToSend.map((x) => ({
						role: x.role,
						content: x.content,
					})),
					model,
					stream: false,
				}),
			});
			const text = await res.text();
			let data: Record<string, unknown>;
			try {
				data = text ? JSON.parse(text) : {};
			} catch {
				setMessages((m) => [
					...m,
					{
						role: "assistant",
						content: `Failed: invalid response (${text.slice(0, 80)}...)`,
					},
				]);
				return;
			}
			if (data.error) {
				setMessages((m) => [...m, { role: "assistant", content: `Error: ${data.error}` }]);
			} else {
				const msg = data.message as { content?: string } | undefined;
				const choices = data.choices as Array<{ message?: { content?: string } }> | undefined;
				const content = msg?.content ?? choices?.[0]?.message?.content ?? JSON.stringify(data);
				setMessages((m) => [...m, { role: "assistant", content: String(content) }]);
			}
		} catch (e) {
			setMessages((m) => [
				...m,
				{
					role: "assistant",
					content: `Failed: ${e instanceof Error ? e.message : "Unknown error"}`,
				},
			]);
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className="container mx-auto p-6 flex flex-col h-[calc(100vh-8rem)]">
			<h1 className="text-3xl font-bold mb-4 text-slate-100">Chat</h1>
			<div className="flex flex-wrap gap-4 mb-4 items-end">
				<div>
					<label htmlFor="chat-personality" className="block text-sm text-slate-400 mb-1">
						Personality
					</label>
					<select
						id="chat-personality"
						value={personality}
						onChange={(e) => setPersonality(e.target.value)}
						className="px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 focus:outline-none focus:ring-2 focus:ring-amber"
					>
						{PERSONALITIES.map((p) => (
							<option key={p.id} value={p.id}>
								{p.label}
							</option>
						))}
					</select>
				</div>
				<div>
					<label htmlFor="chat-model" className="block text-sm text-slate-400 mb-1">
						Model
					</label>
					<select
						id="chat-model"
						value={model}
						onChange={(e) => setModel(e.target.value)}
						className="px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 focus:outline-none focus:ring-2 focus:ring-amber min-w-[140px]"
					>
						{models.length > 0 ? (
							models.map((m) => (
								<option key={m} value={m}>
									{m}
								</option>
							))
						) : (
							<option value={model}>{model}</option>
						)}
					</select>
				</div>
				{messages.length > 0 && (
					<div className="flex gap-2">
						<button
							type="button"
							onClick={() => handleExport("md")}
							className="px-3 py-2 rounded-lg bg-slate-700 text-slate-200 text-sm hover:bg-slate-600"
						>
							Export MD
						</button>
						<button
							type="button"
							onClick={() => handleExport("json")}
							className="px-3 py-2 rounded-lg bg-slate-700 text-slate-200 text-sm hover:bg-slate-600"
						>
							Export JSON
						</button>
					</div>
				)}
			</div>
			<div className="flex-1 overflow-auto rounded-xl glass-panel border border-slate-600/50 p-4 space-y-4 min-h-0">
				{messages.length === 0 && (
					<p className="text-slate-500 text-center py-8">
						Ask about your Plex library or anything. Uses Ollama/LM Studio. Set LLM_BASE_URL in
						backend/.env.
					</p>
				)}
				{messages.map((msg, i) => (
					<div
						key={`${msg.role}-${i}-${msg.content?.slice(0, 24) ?? ""}`}
						className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
					>
						<div
							className={`max-w-[85%] rounded-lg px-4 py-2 ${
								msg.role === "user"
									? "bg-amber/20 text-slate-200"
									: "bg-slate-700/80 text-slate-200"
							}`}
						>
							<p className="whitespace-pre-wrap">{msg.content}</p>
						</div>
					</div>
				))}
				{loading && (
					<div className="flex justify-start">
						<div className="bg-slate-700/80 rounded-lg px-4 py-2 text-slate-400">...</div>
					</div>
				)}
				<div ref={bottomRef} />
			</div>
			<form onSubmit={handleSubmit} className="mt-4 flex flex-col sm:flex-row gap-2">
				<div className="flex-1 flex gap-2">
					<input
						type="text"
						value={input}
						onChange={(e) => setInput(e.target.value)}
						placeholder="Message..."
						disabled={loading}
						className="flex-1 px-4 py-3 rounded-xl glass-panel border border-slate-600/50 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber disabled:opacity-50"
					/>
					<button
						type="button"
						onClick={handleRefine}
						disabled={loading || refining || !input.trim()}
						className="px-3 py-3 rounded-xl bg-slate-700 text-slate-200 text-sm hover:bg-slate-600 disabled:opacity-50"
						title="Refine with LLM"
					>
						{refining ? "..." : "Refine"}
					</button>
				</div>
				<button
					type="submit"
					disabled={loading || !input.trim()}
					className="px-6 py-3 rounded-xl bg-amber text-slate-900 font-medium hover:bg-amber/90 disabled:opacity-50 disabled:cursor-not-allowed"
				>
					Send
				</button>
			</form>
		</div>
	);
}
