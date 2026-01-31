import { NextRequest, NextResponse } from 'next/server';
import { generateImpression } from '@/lib/claude';
import { isDemoMode, getDemoImpression } from '@/lib/demo-data';
import { GenerateImpressionRequest } from '@/lib/types';

export async function POST(request: NextRequest) {
  try {
    const body: GenerateImpressionRequest = await request.json();
    const { finding, section_name } = body;

    if (!finding || !section_name) {
      return NextResponse.json(
        { error: 'Missing required fields: finding, section_name' },
        { status: 400 }
      );
    }

    // Demo mode: return simulated response
    if (isDemoMode()) {
      return NextResponse.json({
        result: getDemoImpression(finding),
        preview: true,
      });
    }

    const result = await generateImpression(finding, section_name);

    return NextResponse.json({ result });
  } catch (error) {
    console.error('Error generating impression:', error);
    return NextResponse.json(
      { error: 'Failed to generate impression' },
      { status: 500 }
    );
  }
}
