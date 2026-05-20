import { AppLayout } from "@/components/layout/app-layout";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
	subsets: ["latin"],
	variable: "--font-body",
	display: "swap",
});

export const metadata: Metadata = {
	title: "PlexMCP Webapp",
	description: "Modern web interface for Plex Media Server management",
};

export default function RootLayout({
	children,
}: { children: React.ReactNode }) {
	return (
		<html lang="en" className={inter.variable} suppressHydrationWarning>
			<body className="font-sans antialiased bg-slate-900 text-slate-100 min-h-screen">
				<AppLayout>{children}</AppLayout>
			</body>
		</html>
	);
}
