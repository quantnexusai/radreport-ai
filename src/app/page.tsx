'use client';

import { useState } from 'react';
import Link from 'next/link';
import {
  Stethoscope,
  FileText,
  Brain,
  Shield,
  Zap,
  ArrowRight,
} from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { AuthModal } from '@/components/AuthModal';
import { Button } from '@/components/ui/Button';

const features = [
  {
    icon: FileText,
    title: 'Structured Reports',
    description:
      'Generate comprehensive radiology reports with proper formatting and medical terminology.',
  },
  {
    icon: Brain,
    title: 'AI-Powered Analysis',
    description:
      'Leverage Claude AI for intelligent finding categorization and impression generation.',
  },
  {
    icon: Zap,
    title: 'Image Analysis',
    description:
      'Upload CT scan images for AI-assisted visual analysis and findings complement.',
  },
  {
    icon: Shield,
    title: 'Pattern Matching',
    description:
      'Intelligent 3-tier pattern matching for consistent impression generation.',
  },
];

export default function HomePage() {
  const { user, isDemo } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);

  return (
    <>
      <Header />
      <main className="flex-1">
        {/* Hero Section */}
        <section className="bg-gradient-to-b from-primary-50 to-white py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <div className="flex justify-center mb-6">
                <div className="p-4 bg-primary-100 rounded-full">
                  <Stethoscope className="h-12 w-12 text-primary-600" />
                </div>
              </div>
              <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
                AI-Powered Radiology Reports
              </h1>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
                Generate structured, professional radiology reports in seconds using
                advanced AI. Perfect for radiologists who want to save time while
                maintaining quality.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                {user ? (
                  <Link href="/dashboard">
                    <Button size="lg">
                      Go to Dashboard
                      <ArrowRight className="ml-2 h-5 w-5" />
                    </Button>
                  </Link>
                ) : (
                  <>
                    <Button size="lg" onClick={() => setShowAuthModal(true)}>
                      Get Started
                      <ArrowRight className="ml-2 h-5 w-5" />
                    </Button>
                    <Link href="/dashboard">
                      <Button variant="secondary" size="lg">
                        Try Demo
                      </Button>
                    </Link>
                  </>
                )}
              </div>
              {isDemo && (
                <p className="mt-4 text-sm text-amber-600">
                  Currently running in demo mode with sample data
                </p>
              )}
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Powerful Features
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Everything you need to generate professional radiology reports
                quickly and accurately.
              </p>
            </div>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
              {features.map((feature) => (
                <div
                  key={feature.title}
                  className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
                >
                  <div className="p-3 bg-primary-100 rounded-lg w-fit mb-4">
                    <feature.icon className="h-6 w-6 text-primary-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600">{feature.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Tech Stack Section */}
        <section className="py-20 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Built with Modern Technology
              </h2>
              <p className="text-lg text-gray-600">
                Powered by industry-leading tools and frameworks.
              </p>
            </div>
            <div className="flex flex-wrap justify-center gap-8 text-gray-600">
              <span className="px-4 py-2 bg-white rounded-lg shadow-sm">
                Next.js 15
              </span>
              <span className="px-4 py-2 bg-white rounded-lg shadow-sm">
                Tailwind CSS
              </span>
              <span className="px-4 py-2 bg-white rounded-lg shadow-sm">
                Supabase
              </span>
              <span className="px-4 py-2 bg-white rounded-lg shadow-sm">
                Claude AI
              </span>
              <span className="px-4 py-2 bg-white rounded-lg shadow-sm">
                TypeScript
              </span>
            </div>
          </div>
        </section>
      </main>
      <Footer />

      <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />
    </>
  );
}
