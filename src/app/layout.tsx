import type { Metadata } from 'next';
import { AuthProvider } from '@/lib/auth-context';
import './globals.css';

export const metadata: Metadata = {
  title: 'RadReport AI - AI-Powered Radiology Report Generator',
  description:
    'Generate structured radiology reports using AI-powered multimodal processing. Built with Next.js, Supabase, and Claude AI.',
  keywords: ['radiology', 'AI', 'report generator', 'medical imaging', 'CT scan'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 flex flex-col">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
