"use client";

import { API_BASE } from "@/utils/api";
import { Trash2 } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";

interface Message {
	role: "user" | "assistant";
	content: string;
	ts?: string;
}

const STORAGE_KEY = "plex-mcp-chat-history";
const PERSONALITY_KEY = "plex-mcp-chat-personality";
const MAX_MESSAGES = 100;

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

const EXAMPLE_PROMPTS = [
	"What's recently added to my Plex library?",
	"Show me unwatched movies sorted by rating",
	"Which libraries have the most content?",
	"What anime series are in my library?",
	"Recommend something to watch tonight",
	"Check my server health and status",
];

function loadMessages(): Message[] {
	try {
		const raw = localStorage.getItem(STORAGE_KEY);
		if (raw) return JSON.parse(raw);
	} catch {}
	return [];
}

function saveMessages(msgs: Message[]) {
	try {
		const trimmed = msgs.slice(-MAX_MESSAGES);
		localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
	} catch {}
}

function loadPersonality(): string {
	try {
		return localStorage.getItem(PERSONALITY_KEY) || "default";
	} catch {}
	return "default";
}

export default function ChatPage() {
	const [messages, setMessages] = useState<Message[]>(loadMessages);
	const [input, setInput] = useState("");
	const [loading, setLoading] = useState(false);
	const [refining, setRefining] = useState(false);
	const [model, setModel] = useState("gemma4:12b");
	const [models, setModels] = useState<string[]>([]);
	const [personality, setPersonality] = useState(loadPersonality);
	const [providerStatus, setProviderStatus] = useState<"connected" | "offline" | "detecting">(
		"detecting",
	);
	const bottomRef = useRef<HTMLDivElement>(null);

	const scrollToBottom = useCallback(() => {
		bottomRef.current?.scrollIntoView({ behavior: "smooth" });
	}, []);

	useEffect(() => {
		scrollToBottom();
	}, [messages, scrollToBottom]);

	// Persist messages
	useEffect(() => {
		saveMessages(messages);
	}, [messages]);

	// Persist personality
	useEffect(() => {
		try {
			localStorage.setItem(PERSONALITY_KEY, personality);
		} catch {}
	}, [personality]);

	// Provider detection + model discovery
	useEffect(() => {
		let cancelled = false;
		(async () => {
			try {
				const r = await fetch(`${API_BASE}/health`);
				if (cancelled) return;
				setProviderStatus(r.ok ? "connected" : "offline");
			} catch {
				if (!cancelled) setProviderStatus("offline");
			}
		})();

		fetch(`${API_BASE}/api/llm/models`)
			.then((r) => r.json())
			.then((d: { models?: string[] }) => {
				if (cancelled) return;
				const list = d.models ?? [];
				setModels(list);
				const saved = localStorage.getItem("plex-webapp-default-llm-model");
				if (saved && list.includes(saved)) setModel(saved);
			})
			.catch(() => {});

		return () => {
			cancelled = true;
		};
	}, []);

	const handleClear = () => {
		setMessages([]);
		try {
			localStorage.removeItem(STORAGE_KEY);
		} catch {}
	};

	const handleExport = (format: "md" | "json") => {
		const blob =
			format === "md"
				? new Blob(
						[
							messages
								.map(
									(m) =>
										`[${m.ts || "unknown"}] ${m.role === "user" ? "You" : "Assistant"}: ${m.content}`,
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
		a.download = `plex-chat-${new Date().toISOString().slice(0, 10)}.${format}`;
		a.click();
		URL.revokeObjectURL(url);
	};

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

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!input.trim() || loading) return;
		const userMsg: Message = {
			role: "user",
			content: input.trim(),
			ts: new Date().toISOString(),
		};
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
				setMessages((m) => [
					...m,
					{ role: "assistant", content: String(content), ts: new Date().toISOString() },
				]);
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
		<div
			className="container mx-auto p-6 flex flex-col h-[calc(100vh-8rem)]"
			data-testid="chat-page"
		>
			{/* Controls bar */}
			<div className="flex flex-wrap gap-4 mb-4 items-end" data-testid="chat-controls">
				<div>
					<label htmlFor="chat-personality" className="block text-sm text-slate-400 mb-1">
						Personality
					</label>
					<select
						id="chat-personality"
						value={personality}
						onChange={(e) => setPersonality(e.target.value)}
						className="px-4 py-2 rounded-lg bg-zinc-800 border border-zinc-600 text-zinc-100 focus:outline-none focus:ring-2 focus:ring-amber"
						data-testid="personality-select"
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
						className="px-4 py-2 rounded-lg bg-zinc-800 border border-zinc-600 text-zinc-100 focus:outline-none focus:ring-2 focus:ring-amber min-w-[140px]"
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
				<div className="flex items-center gap-2 self-center">
					<span
						className={`w-2 h-2 rounded-full ${
							providerStatus === "connected"
								? "bg-green-500"
								: providerStatus === "offline"
									? "bg-red-500"
									: "bg-gray-500"
						} animate-pulse`}
					/>
					<span className="text-zinc-400 text-sm">
						{providerStatus === "connected"
							? "Backend online"
							: providerStatus === "offline"
								? "Offline"
								: "Detecting..."}
					</span>
				</div>
				<div className="flex gap-2 self-center ml-auto">
					{messages.length > 0 && (
						<>
							<button
								type="button"
								onClick={() => handleExport("md")}
								className="px-3 py-2 rounded-lg bg-zinc-800 border border-zinc-600 text-zinc-300 text-sm hover:bg-zinc-700"
								data-testid="chat-export"
							>
								Export
							</button>
							<button
								type="button"
								onClick={handleClear}
								className="p-2 rounded-lg bg-zinc-800 border border-zinc-600 text-zinc-400 hover:text-red-400"
								title="Clear conversation"
								data-testid="chat-clear"
							>
								<Trash2 size={16} />
							</button>
						</>
					)}
				</div>
			</div>

			{/* Messages */}
			<div
				className="flex-1 overflow-auto rounded-xl bg-zinc-800/80 border border-zinc-600/50 p-4 space-y-4 min-h-0"
				data-testid="chat-messages"
			>
				{messages.length === 0 && (
					<div>
						<p className="text-zinc-500 text-center py-4">
							Ask about your Plex library or anything. Uses Ollama/LM Studio.
						</p>
						<div className="flex flex-wrap gap-2 justify-center mt-2" data-testid="example-prompts">
							{EXAMPLE_PROMPTS.map((prompt) => (
								<button
									key={prompt}
									onClick={() => setInput(prompt)}
									className="px-3 py-1.5 text-xs rounded-full bg-zinc-700 border border-zinc-600 text-zinc-300 hover:bg-zinc-600 hover:text-zinc-100 transition-colors"
								>
									{prompt}
								</button>
							))}
						</div>
					</div>
				)}
				{messages.map((msg, i) => (
					<div
						key={`${msg.role}-${i}-${msg.content?.slice(0, 24) ?? ""}`}
						className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
					>
						<div
							className={`max-w-[85%] rounded-lg px-4 py-2 ${
								msg.role === "user" ? "bg-amber/20 text-zinc-200" : "bg-zinc-700/80 text-zinc-200"
							}`}
						>
							<p className="whitespace-pre-wrap">{msg.content}</p>
						</div>
					</div>
				))}
				{loading && (
					<div className="flex justify-start">
						<div className="bg-zinc-700/80 rounded-lg px-4 py-2 text-zinc-400 animate-pulse">
							Thinking...
						</div>
					</div>
				)}
				<div ref={bottomRef} />
			</div>

			{/* Input */}
			<form onSubmit={handleSubmit} className="mt-4 flex flex-col sm:flex-row gap-2">
				<div className="flex-1 flex gap-2">
					<input
						type="text"
						value={input}
						onChange={(e) => setInput(e.target.value)}
						placeholder="Message..."
						disabled={loading}
						className="flex-1 px-4 py-3 rounded-xl bg-zinc-800 border border-zinc-600 text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-amber disabled:opacity-50"
						data-testid="chat-input"
					/>
					<button
						type="button"
						onClick={handleRefine}
						disabled={loading || refining || !input.trim()}
						className="px-3 py-3 rounded-xl bg-zinc-700 text-zinc-200 text-sm hover:bg-zinc-600 disabled:opacity-50"
						title="Refine with LLM"
					>
						{refining ? "..." : "Refine"}
					</button>
				</div>
				<button
					type="submit"
					disabled={loading || !input.trim()}
					className="px-6 py-3 rounded-xl bg-amber text-zinc-900 font-medium hover:bg-amber/90 disabled:opacity-50 disabled:cursor-not-allowed"
					data-testid="chat-send"
				>
					Send
				</button>
			</form>
		</div>
	);
}
