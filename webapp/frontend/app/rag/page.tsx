import { RAGDashboard } from "@/components/rag/rag-dashboard";

export default function RAGPage() {
	return (
		<div className="flex-1 p-8 overflow-y-auto">
			<div className="flex flex-col gap-2 mb-8">
				<h1 className="text-4xl font-bold text-white tracking-tight">RAG Management</h1>
				<p className="text-slate-400">Deep metadata indexing and vector store orchestration.</p>
			</div>
			<RAGDashboard />
		</div>
	);
}
