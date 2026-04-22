import { getBaseUrl } from "./api";

export async function playMedia(mediaKey: string, clientId?: string) {
	const res = await fetch(`${getBaseUrl()}/api/playback/play`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ media_key: mediaKey, client_id: clientId }),
	});
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

export async function listClients() {
	const res = await fetch(`${getBaseUrl()}/api/playback/clients`);
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}
