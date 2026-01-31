'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Stethoscope, LogIn, LogOut, User } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { Button } from './ui/Button';
import { AuthModal } from './AuthModal';

export function Header() {
  const { user, profile, signOut, isDemo } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);

  return (
    <>
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-2">
              <Stethoscope className="h-8 w-8 text-primary-600" />
              <span className="text-xl font-bold text-gray-900">RadReport AI</span>
            </Link>

            {/* Navigation */}
            <nav className="flex items-center gap-4">
              {user ? (
                <>
                  <Link
                    href="/dashboard"
                    className="text-gray-600 hover:text-gray-900 text-sm font-medium"
                  >
                    Dashboard
                  </Link>
                  {profile?.is_admin && (
                    <Link
                      href="/dashboard/admin"
                      className="text-gray-600 hover:text-gray-900 text-sm font-medium"
                    >
                      Admin
                    </Link>
                  )}
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <User className="h-4 w-4" />
                    <span>{profile?.first_name || user.email}</span>
                    {isDemo && (
                      <span className="px-2 py-0.5 bg-amber-100 text-amber-800 text-xs rounded-full">
                        Demo
                      </span>
                    )}
                  </div>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => signOut()}
                  >
                    <LogOut className="h-4 w-4 mr-1" />
                    Sign Out
                  </Button>
                </>
              ) : (
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => setShowAuthModal(true)}
                >
                  <LogIn className="h-4 w-4 mr-1" />
                  Sign In
                </Button>
              )}
            </nav>
          </div>
        </div>
      </header>

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
      />
    </>
  );
}
