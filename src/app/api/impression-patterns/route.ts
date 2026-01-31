import { NextRequest, NextResponse } from 'next/server';
import { createServerSupabaseClient } from '@/lib/supabase-server';
import { isDemoMode, DEMO_PATTERNS } from '@/lib/demo-data';
import { ImpressionPatternFormData } from '@/lib/types';

// GET all impression patterns
export async function GET() {
  try {
    // Demo mode
    if (isDemoMode()) {
      return NextResponse.json(DEMO_PATTERNS);
    }

    const supabase = await createServerSupabaseClient();
    const { data, error } = await supabase
      .from('impression_lookup')
      .select('*')
      .order('section_name')
      .order('finding_pattern');

    if (error) {
      console.error('Error fetching impression patterns:', error);
      return NextResponse.json(
        { error: 'Failed to fetch impression patterns' },
        { status: 500 }
      );
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching impression patterns:', error);
    return NextResponse.json(
      { error: 'Failed to fetch impression patterns' },
      { status: 500 }
    );
  }
}

// POST create new impression pattern (admin only)
export async function POST(request: NextRequest) {
  try {
    // Demo mode: simulate success
    if (isDemoMode()) {
      const body: ImpressionPatternFormData = await request.json();
      return NextResponse.json({
        id: Date.now(),
        ...body,
        created_at: new Date().toISOString(),
      });
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

    const body: ImpressionPatternFormData = await request.json();
    const { finding_pattern, section_name, impression_text } = body;

    if (!finding_pattern || !section_name || !impression_text) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    const { data, error } = await supabase
      .from('impression_lookup')
      .insert({
        finding_pattern,
        section_name,
        impression_text,
      })
      .select()
      .single();

    if (error) {
      console.error('Error creating impression pattern:', error);
      return NextResponse.json(
        { error: 'Failed to create impression pattern' },
        { status: 500 }
      );
    }

    return NextResponse.json(data, { status: 201 });
  } catch (error) {
    console.error('Error creating impression pattern:', error);
    return NextResponse.json(
      { error: 'Failed to create impression pattern' },
      { status: 500 }
    );
  }
}
