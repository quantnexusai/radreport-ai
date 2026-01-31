import { NextRequest, NextResponse } from 'next/server';
import { processFindings } from '@/lib/claude';
import { isDemoMode, getDemoProcessedFindings } from '@/lib/demo-data';
import { ProcessFindingsRequest } from '@/lib/types';

export async function POST(request: NextRequest) {
  try {
    const body: ProcessFindingsRequest = await request.json();
    const { findings, section } = body;

    if (!findings || !section) {
      return NextResponse.json(
        { error: 'Missing required fields: findings, section' },
        { status: 400 }
      );
    }

    // Demo mode: return simulated response
    if (isDemoMode()) {
      return NextResponse.json({
        result: getDemoProcessedFindings(findings),
        preview: true,
      });
    }

    const result = await processFindings(findings, section);

    return NextResponse.json({ result });
  } catch (error) {
    console.error('Error processing findings:', error);
    return NextResponse.json(
      { error: 'Failed to process findings' },
      { status: 500 }
    );
  }
}
