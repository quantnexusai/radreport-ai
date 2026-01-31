import { NextRequest, NextResponse } from 'next/server';
import { createServerSupabaseClient } from '@/lib/supabase-server';
import { isDemoMode } from '@/lib/demo-data';

interface UpdateTemplatesBody {
  technique_template_chest: string;
  technique_template_abdomen: string;
}

// PUT update facility templates (admin only)
export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;

    // Demo mode: simulate success
    if (isDemoMode()) {
      const body: UpdateTemplatesBody = await request.json();
      return NextResponse.json({
        id: parseInt(id),
        ...body,
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

    const body: UpdateTemplatesBody = await request.json();
    const { technique_template_chest, technique_template_abdomen } = body;

    if (!technique_template_chest || !technique_template_abdomen) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    const { data, error } = await supabase
      .from('facilities')
      .update({
        technique_template_chest,
        technique_template_abdomen,
      })
      .eq('id', id)
      .select()
      .single();

    if (error) {
      console.error('Error updating facility templates:', error);
      return NextResponse.json(
        { error: 'Failed to update facility templates' },
        { status: 500 }
      );
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Error updating facility templates:', error);
    return NextResponse.json(
      { error: 'Failed to update facility templates' },
      { status: 500 }
    );
  }
}
