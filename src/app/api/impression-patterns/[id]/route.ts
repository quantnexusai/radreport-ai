import { NextRequest, NextResponse } from 'next/server';
import { createServerSupabaseClient } from '@/lib/supabase-server';
import { isDemoMode } from '@/lib/demo-data';

// DELETE impression pattern (admin only)
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;

    // Demo mode: simulate success
    if (isDemoMode()) {
      return NextResponse.json({ success: true });
    }

    const supabase = await createServerSupabaseClient();

    // Check if user is authenticated and is admin
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Check admin status
    const { data: profile, error: profileError } = await supabase
      .from('profiles')
      .select('is_admin')
      .eq('id', user.id)
      .single();

    if (profileError || !profile?.is_admin) {
      return NextResponse.json(
        { error: 'Admin access required' },
        { status: 403 }
      );
    }

    const { error } = await supabase
      .from('impression_lookup')
      .delete()
      .eq('id', id);

    if (error) {
      console.error('Error deleting impression pattern:', error);
      return NextResponse.json(
        { error: 'Failed to delete impression pattern' },
        { status: 500 }
      );
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error deleting impression pattern:', error);
    return NextResponse.json(
      { error: 'Failed to delete impression pattern' },
      { status: 500 }
    );
  }
}
