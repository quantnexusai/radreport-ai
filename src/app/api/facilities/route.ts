import { NextRequest, NextResponse } from 'next/server';
import { createServerSupabaseClient } from '@/lib/supabase-server';
import { isDemoMode, DEMO_FACILITIES } from '@/lib/demo-data';
import { FacilityFormData } from '@/lib/types';

// GET all facilities
export async function GET() {
  try {
    // Demo mode
    if (isDemoMode()) {
      return NextResponse.json(DEMO_FACILITIES);
    }

    const supabase = await createServerSupabaseClient();
    const { data, error } = await supabase
      .from('facilities')
      .select('*')
      .order('name');

    if (error) {
      console.error('Error fetching facilities:', error);
      return NextResponse.json(
        { error: 'Failed to fetch facilities' },
        { status: 500 }
      );
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching facilities:', error);
    return NextResponse.json(
      { error: 'Failed to fetch facilities' },
      { status: 500 }
    );
  }
}

// POST create new facility (admin only)
export async function POST(request: NextRequest) {
  try {
    // Demo mode: simulate success
    if (isDemoMode()) {
      const body: FacilityFormData = await request.json();
      return NextResponse.json({
        id: Date.now(),
        ...body,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
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

    const body: FacilityFormData = await request.json();
    const { name, technique_template_chest, technique_template_abdomen } = body;

    if (!name || !technique_template_chest || !technique_template_abdomen) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    const { data, error } = await supabase
      .from('facilities')
      .insert({
        name,
        technique_template_chest,
        technique_template_abdomen,
      })
      .select()
      .single();

    if (error) {
      console.error('Error creating facility:', error);

      if (error.code === '23505') {
        return NextResponse.json(
          { error: 'A facility with this name already exists' },
          { status: 409 }
        );
      }

      return NextResponse.json(
        { error: 'Failed to create facility' },
        { status: 500 }
      );
    }

    return NextResponse.json(data, { status: 201 });
  } catch (error) {
    console.error('Error creating facility:', error);
    return NextResponse.json(
      { error: 'Failed to create facility' },
      { status: 500 }
    );
  }
}
