import { AuthProvider } from "@/components/Auth/AuthProvider";
import { Inter } from "next/font/google";
import "@/styles/globals.css";
import type { Metadata } from "next";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "OperaBot",
  description: "Operational Knowledge Assistant",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <body style={{ backgroundColor: "#0A0A0A", color: "#F5F5F5" }}>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
