'use client';

import { useAuth } from '@/lib/auth-context';
import { AdminPanel } from '@/components/dashboard/admin/AdminPanel';
import { Card, CardContent } from '@/components/ui/Card';
import { ShieldAlert } from 'lucide-react';

export default function AdminPage() {
  const { isAdmin, isDemo, isLoading } = useAuth();

  // In demo mode, allow admin access
  if (!isAdmin && !isDemo) {
    return (
      <div className="max-w-2xl mx-auto mt-20">
        <Card>
          <CardContent className="text-center py-12">
            <ShieldAlert className="h-16 w-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Access Denied
            </h2>
            <p className="text-gray-600">
              You don&apos;t have permission to access the admin panel. Please
              contact an administrator if you believe this is an error.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Admin Panel</h1>
        <p className="text-gray-600 mt-1">
          Manage facilities, templates, and impression patterns.
        </p>
      </div>
      <AdminPanel />
    </div>
  );
}
