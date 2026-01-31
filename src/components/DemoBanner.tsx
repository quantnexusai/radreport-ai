'use client';

import { AlertTriangle } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';

export function DemoBanner() {
  const { isDemo } = useAuth();

  if (!isDemo) return null;

  return (
    <div className="bg-amber-100 border-b border-amber-200 px-4 py-2">
      <div className="flex items-center justify-center gap-2 text-amber-800">
        <AlertTriangle className="h-4 w-4" />
        <span className="text-sm">
          <span className="font-medium">Demo Mode:</span> You are viewing sample data.
          Connect Supabase and Anthropic API for full functionality.
        </span>
      </div>
    </div>
  );
}
