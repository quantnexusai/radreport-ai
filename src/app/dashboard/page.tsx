'use client';

import { ReportGenerator } from '@/components/dashboard/ReportGenerator';

export default function DashboardPage() {
  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Report Generator</h1>
        <p className="text-gray-600 mt-1">
          Generate structured radiology reports with AI assistance.
        </p>
      </div>
      <ReportGenerator />
    </div>
  );
}
