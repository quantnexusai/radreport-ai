import { NextRequest, NextResponse } from 'next/server';
import { analyzeImage } from '@/lib/claude';
import { isDemoMode, getDemoImageAnalysis } from '@/lib/demo-data';
import { AnalyzeImageRequest } from '@/lib/types';

export async function POST(request: NextRequest) {
  try {
    const body: AnalyzeImageRequest = await request.json();
    const { image_data, study_type } = body;

    if (!image_data || !study_type) {
      return NextResponse.json(
        { error: 'Missing required fields: image_data, study_type' },
        { status: 400 }
      );
    }

    // Validate image data size (rough check for base64)
    if (image_data.length > 20 * 1024 * 1024) {
      return NextResponse.json(
        { error: 'Image too large. Maximum size is 10MB.' },
        { status: 413 }
      );
    }

    // Demo mode: return simulated response
    if (isDemoMode()) {
      return NextResponse.json({
        result: getDemoImageAnalysis(),
        preview: true,
      });
    }

    const result = await analyzeImage(image_data, study_type);

    return NextResponse.json({ result });
  } catch (error) {
    console.error('Error analyzing image:', error);
    return NextResponse.json(
      { error: 'Failed to analyze image' },
      { status: 500 }
    );
  }
}
