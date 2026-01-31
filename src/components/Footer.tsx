'use client';

import { Stethoscope } from 'lucide-react';

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2 text-gray-600">
            <Stethoscope className="h-5 w-5" />
            <span className="text-sm">
              RadReport AI v1.0.0
            </span>
          </div>
          <div className="text-sm text-gray-500">
            &copy; {currentYear} RadReport AI. All rights reserved.
          </div>
        </div>
      </div>
    </footer>
  );
}
