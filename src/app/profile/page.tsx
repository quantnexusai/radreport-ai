'use client';

import { useState } from 'react';
import { User, Mail, Calendar, Shield } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { PageLoader } from '@/components/ui/LoadingSpinner';

export default function ProfilePage() {
  const { user, profile, isLoading, isDemo } = useAuth();
  const [firstName, setFirstName] = useState(profile?.first_name || '');
  const [lastName, setLastName] = useState(profile?.last_name || '');
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');

  if (isLoading) {
    return <PageLoader />;
  }

  if (!user) {
    return (
      <>
        <Header />
        <main className="flex-1 flex items-center justify-center">
          <Card className="max-w-md w-full mx-4">
            <CardContent className="text-center py-8">
              <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Not Signed In
              </h2>
              <p className="text-gray-600">
                Please sign in to view your profile.
              </p>
            </CardContent>
          </Card>
        </main>
        <Footer />
      </>
    );
  }

  const handleSave = async () => {
    if (isDemo) {
      setMessage('Profile updates are disabled in demo mode');
      return;
    }

    setIsSaving(true);
    setMessage('');

    // TODO: Implement profile update API
    setTimeout(() => {
      setMessage('Profile updated successfully!');
      setIsSaving(false);
    }, 1000);
  };

  return (
    <>
      <Header />
      <main className="flex-1 py-8">
        <div className="max-w-2xl mx-auto px-4">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">Your Profile</h1>

          <div className="space-y-6">
            {/* Profile Info Card */}
            <Card>
              <CardHeader>
                <CardTitle>Profile Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label="First Name"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    disabled={isDemo}
                  />
                  <Input
                    label="Last Name"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    disabled={isDemo}
                  />
                </div>
                {message && (
                  <p
                    className={`text-sm ${
                      message.includes('success')
                        ? 'text-green-600'
                        : 'text-amber-600'
                    }`}
                  >
                    {message}
                  </p>
                )}
                <Button onClick={handleSave} isLoading={isSaving} disabled={isDemo}>
                  Save Changes
                </Button>
              </CardContent>
            </Card>

            {/* Account Info Card */}
            <Card>
              <CardHeader>
                <CardTitle>Account Information</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <Mail className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm text-gray-500">Email</p>
                      <p className="font-medium">{user.email}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Calendar className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm text-gray-500">Member Since</p>
                      <p className="font-medium">
                        {profile?.created_at
                          ? new Date(profile.created_at).toLocaleDateString()
                          : 'N/A'}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Shield className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm text-gray-500">Role</p>
                      <p className="font-medium">
                        {profile?.is_admin ? 'Administrator' : 'User'}
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {isDemo && (
              <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
                <p className="text-sm text-amber-800">
                  <strong>Demo Mode:</strong> Profile editing is disabled. Connect
                  Supabase for full functionality.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
