'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { FileText, Settings, Stethoscope } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';

const navItems = [
  {
    label: 'Report Generator',
    href: '/dashboard',
    icon: FileText,
  },
  {
    label: 'Admin Panel',
    href: '/dashboard/admin',
    icon: Settings,
    adminOnly: true,
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const { profile } = useAuth();

  const filteredNavItems = navItems.filter(
    (item) => !item.adminOnly || profile?.is_admin
  );

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* Logo */}
      <div className="h-16 flex items-center px-4 border-b border-gray-200">
        <Link href="/dashboard" className="flex items-center gap-2">
          <Stethoscope className="h-8 w-8 text-primary-600" />
          <span className="text-lg font-bold text-gray-900">RadReport AI</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {filteredNavItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                isActive
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              }`}
            >
              <Icon className="h-5 w-5" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          Powered by Claude AI
        </p>
      </div>
    </aside>
  );
}
