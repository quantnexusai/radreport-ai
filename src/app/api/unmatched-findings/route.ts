import { NextRequest, NextResponse } from 'next/server';
import { createServerSupabaseClient } from '@/lib/supabase-server';
import { isDemoMode, DEMO_UNMATCHED_FINDINGS } from '@/lib/demo-data';

// GET all unmatched findings
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit') || '100');

    // Demo mode
    if (isDemoMode()) {
      return NextResponse.json(DEMO_UNMATCHED_FINDINGS.slice(0, limit));
    }

    const supabase = await createServerSupabaseClient();

    // Check if user is authenticated
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const { data, error } = await supabase
      .from('unmatched_findings')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(limit);

    if (error) {
      console.error('Error fetching unmatched findings:', error);
      return NextResponse.json(
        { error: 'Failed to fetch unmatched findings' },
        { status: 500 }
      );
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching unmatched findings:', error);
    return NextResponse.json(
      { error: 'Failed to fetch unmatched findings' },
      { status: 500 }
    );
  }
}
