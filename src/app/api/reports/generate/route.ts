import { NextRequest, NextResponse } from 'next/server';
import { createServerSupabaseClient } from '@/lib/supabase-server';
import { generateReport } from '@/lib/report-generator';
import { isDemoMode, generateDemoReport, DEMO_FACILITIES, DEMO_TEMPLATES, DEMO_PATTERNS } from '@/lib/demo-data';
import { ReportGenerationRequest, Facility, ReportTemplate, ImpressionPattern } from '@/lib/types';

export async function POST(request: NextRequest) {
  try {
    const body: ReportGenerationRequest = await request.json();
    const { facility_name, study_type, sections_data, image_data } = body;

    // Validate required fields
    if (!facility_name || !study_type || !sections_data) {
      return NextResponse.json(
        { error: 'Missing required fields: facility_name, study_type, sections_data' },
        { status: 400 }
      );
    }

    // Validate study type
    const validStudyTypes = ['Full Body', 'Chest', 'Abdomen and Pelvis'];
    if (!validStudyTypes.includes(study_type)) {
      return NextResponse.json(
        { error: 'Invalid study_type. Must be one of: Full Body, Chest, Abdomen and Pelvis' },
        { status: 400 }
      );
    }

    // Demo mode: return simulated report
    if (isDemoMode()) {
      const report = generateDemoReport(facility_name, study_type, sections_data);
      return NextResponse.json({
        report,
        success: true,
        preview: true,
      });
    }

    // Get data from Supabase
    const supabase = await createServerSupabaseClient();

    // Fetch facilities
    const { data: facilities, error: facilitiesError } = await supabase
      .from('facilities')
      .select('*');

    if (facilitiesError) {
      console.error('Error fetching facilities:', facilitiesError);
      return NextResponse.json(
        { error: 'Failed to fetch facilities' },
        { status: 500 }
      );
    }

    // Fetch templates
    const { data: templates, error: templatesError } = await supabase
      .from('report_templates')
      .select('*');

    if (templatesError) {
      console.error('Error fetching templates:', templatesError);
      return NextResponse.json(
        { error: 'Failed to fetch templates' },
        { status: 500 }
      );
    }

    // Fetch impression patterns
    const { data: patterns, error: patternsError } = await supabase
      .from('impression_lookup')
      .select('*');

    if (patternsError) {
      console.error('Error fetching patterns:', patternsError);
      return NextResponse.json(
        { error: 'Failed to fetch patterns' },
        { status: 500 }
      );
    }

    // Generate the report
    const report = await generateReport(
      facility_name,
      study_type,
      sections_data,
      image_data,
      {
        facilities: facilities as Facility[],
        templates: templates as ReportTemplate[],
        patterns: patterns as ImpressionPattern[],
        useClaudeForUnmatched: true,
        onUnmatchedFinding: async (finding, sectionName) => {
          // Log unmatched finding to database
          try {
            await supabase.from('unmatched_findings').insert({
              finding,
              section_name: sectionName,
            });
          } catch (error) {
            console.error('Error logging unmatched finding:', error);
          }
        },
      }
    );

    return NextResponse.json({
      report,
      success: true,
    });
  } catch (error) {
    console.error('Error generating report:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json(
      { error: `Failed to generate report: ${errorMessage}`, success: false },
      { status: 500 }
    );
  }
}
