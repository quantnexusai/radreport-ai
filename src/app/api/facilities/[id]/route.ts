import { NextRequest, NextResponse } from 'next/server';
import { createServerSupabaseClient } from '@/lib/supabase-server';
import { isDemoMode, DEMO_FACILITIES } from '@/lib/demo-data';

// GET single facility
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;

    // Demo mode
    if (isDemoMode()) {
      const facility = DEMO_FACILITIES.find((f) => f.id === parseInt(id));
      if (!facility) {
        return NextResponse.json(
          { error: 'Facility not found' },
          { status: 404 }
        );
      }
      return NextResponse.json(facility);
    }

    const supabase = await createServerSupabaseClient();
    const { data, error } = await supabase
      .from('facilities')
      .select('*')
      .eq('id', id)
      .single();

    if (error) {
      if (error.code === 'PGRST116') {
        return NextResponse.json(
          { error: 'Facility not found' },
          { status: 404 }
        );
      }
      console.error('Error fetching facility:', error);
      return NextResponse.json(
        { error: 'Failed to fetch facility' },
        { status: 500 }
      );
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching facility:', error);
    return NextResponse.json(
      { error: 'Failed to fetch facility' },
      { status: 500 }
    );
  }
}

// DELETE facility (admin only)
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
      .from('facilities')
      .delete()
      .eq('id', id);

    if (error) {
      console.error('Error deleting facility:', error);
      return NextResponse.json(
        { error: 'Failed to delete facility' },
        { status: 500 }
      );
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error deleting facility:', error);
    return NextResponse.json(
      { error: 'Failed to delete facility' },
      { status: 500 }
    );
  }
}
