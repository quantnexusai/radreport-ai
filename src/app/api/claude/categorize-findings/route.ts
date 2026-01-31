import { NextRequest, NextResponse } from 'next/server';
import { categorizeFindings } from '@/lib/claude';
import { isDemoMode, getDemoCategorizedFindings } from '@/lib/demo-data';
import { CategorizeFindingsRequest } from '@/lib/types';

export async function POST(request: NextRequest) {
  try {
    const body: CategorizeFindingsRequest = await request.json();
    const { findings, categories, section_name } = body;

    if (!findings || !categories || !section_name) {
      return NextResponse.json(
        { error: 'Missing required fields: findings, categories, section_name' },
        { status: 400 }
      );
    }

    if (!Array.isArray(findings) || !Array.isArray(categories)) {
      return NextResponse.json(
        { error: 'findings and categories must be arrays' },
        { status: 400 }
      );
    }

    // Demo mode: return simulated response
    if (isDemoMode()) {
      return NextResponse.json({
        result: getDemoCategorizedFindings(findings, categories),
        preview: true,
      });
    }

    const result = await categorizeFindings(findings, categories, section_name);

    return NextResponse.json({ result });
  } catch (error) {
    console.error('Error categorizing findings:', error);
    return NextResponse.json(
      { error: 'Failed to categorize findings' },
      { status: 500 }
    );
  }
}
