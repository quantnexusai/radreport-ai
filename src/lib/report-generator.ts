import {
  Facility,
  ReportTemplate,
  ImpressionPattern,
  SectionName,
  SectionsData,
  StudyType,
} from './types';
import { matchImpression } from './impression-matcher';
import {
  processFindings,
  analyzeImage,
  generateImpression,
  categorizeFindings,
} from './claude';

interface GenerationContext {
  facilities: Facility[];
  templates: ReportTemplate[];
  patterns: ImpressionPattern[];
  useClaudeForUnmatched: boolean;
  onUnmatchedFinding?: (finding: string, sectionName: SectionName) => Promise<void>;
}

/**
 * Report Generator - orchestrates the report generation pipeline
 * Ported from Python implementation (utils/report_generator.py)
 */
export async function generateReport(
  facilityName: string,
  studyType: StudyType,
  sectionsData: SectionsData,
  imageData: string | undefined,
  context: GenerationContext
): Promise<string> {
  // Find facility
  const facility = context.facilities.find((f) => f.name === facilityName);
  if (!facility) {
    throw new Error(`Facility not found: ${facilityName}`);
  }

  const reportSections: string[] = [];
  const impressions: string[] = [];

  // Determine which sections to include
  const includeChest = studyType === 'Full Body' || studyType === 'Chest';
  const includeAbdomen = studyType === 'Full Body' || studyType === 'Abdomen and Pelvis';

  // Process chest section
  if (includeChest && sectionsData.chest && sectionsData.chest.trim()) {
    const sectionContent = await processSection(
      'chest',
      sectionsData.chest,
      facility,
      context,
      impressions
    );
    reportSections.push(...sectionContent);
  } else if (includeChest) {
    // Include default findings if no custom findings
    const sectionContent = generateDefaultSection('chest', facility, context);
    reportSections.push(...sectionContent);
  }

  // Process abdomen section
  if (includeAbdomen && sectionsData.abdomen_pelvis && sectionsData.abdomen_pelvis.trim()) {
    const sectionContent = await processSection(
      'abdomen_pelvis',
      sectionsData.abdomen_pelvis,
      facility,
      context,
      impressions
    );
    reportSections.push(...sectionContent);
  } else if (includeAbdomen) {
    // Include default findings if no custom findings
    const sectionContent = generateDefaultSection('abdomen_pelvis', facility, context);
    reportSections.push(...sectionContent);
  }

  // Generate impressions section
  reportSections.push(...generateImpressionsSection(impressions));

  // Analyze image if provided
  if (imageData) {
    try {
      const imageAnalysis = await analyzeImage(imageData, studyType);

      // Only include if there are significant findings
      if (imageAnalysis && !imageAnalysis.toLowerCase().startsWith('no significant')) {
        reportSections.push('');
        reportSections.push('AI IMAGE ANALYSIS:');
        reportSections.push(imageAnalysis);
      }
    } catch (error) {
      console.error('Error analyzing image:', error);
    }
  }

  return reportSections.join('\n');
}

/**
 * Process a single section with findings
 */
async function processSection(
  sectionName: SectionName,
  findings: string,
  facility: Facility,
  context: GenerationContext,
  impressions: string[]
): Promise<string[]> {
  const section: string[] = [];

  // Header
  const header =
    sectionName === 'chest'
      ? 'CT CHEST WITHOUT CONTRAST:'
      : 'CT ABDOMEN AND PELVIS WITHOUT CONTRAST:';
  section.push(header);
  section.push('');

  // Technique
  section.push('TECHNIQUE:');
  const technique =
    sectionName === 'chest'
      ? facility.technique_template_chest
      : facility.technique_template_abdomen;
  section.push(technique);
  section.push('');

  // Process findings through Claude for formatting
  const processedFindings = await processFindings(findings, sectionName);

  // Get template for this section
  const template = context.templates.find((t) => t.section_name === sectionName);
  const defaultFindings = template?.default_findings || {};
  const categories = Object.keys(defaultFindings);

  // Split findings into individual items
  const findingsList = processedFindings
    .split('\n')
    .map((f) => f.trim())
    .filter((f) => f.length > 0);

  // First pass: Direct keyword matching
  const categorizedFindings: Record<string, string[]> = {};
  const uncategorized: string[] = [];

  for (const category of categories) {
    categorizedFindings[category] = [];
  }

  for (const finding of findingsList) {
    let matched = false;
    const findingLower = finding.toLowerCase();

    for (const category of categories) {
      if (findingLower.includes(category.toLowerCase())) {
        categorizedFindings[category].push(finding);
        matched = true;
        break;
      }
    }

    if (!matched) {
      uncategorized.push(finding);
    }
  }

  // Second pass: Claude-powered categorization for uncategorized findings
  if (uncategorized.length > 0 && categories.length > 0) {
    try {
      const claudeCategories = await categorizeFindings(
        uncategorized,
        categories,
        sectionName
      );

      for (const [finding, category] of Object.entries(claudeCategories)) {
        if (categorizedFindings[category]) {
          categorizedFindings[category].push(finding);
        }
      }
    } catch (error) {
      console.error('Error categorizing findings:', error);
      // Fall back to adding uncategorized findings to first category
      if (categories.length > 0) {
        categorizedFindings[categories[0]].push(...uncategorized);
      }
    }
  }

  // Build findings section
  section.push('FINDINGS:');

  for (const category of categories) {
    const categoryFindings = categorizedFindings[category];

    if (categoryFindings && categoryFindings.length > 0) {
      section.push(`${category}: ${categoryFindings.join('. ')}`);

      // Process each finding for impression
      for (const finding of categoryFindings) {
        await processFindingImpression(
          finding,
          sectionName,
          context,
          impressions
        );
      }
    } else {
      // Use default finding
      const defaultFinding = defaultFindings[category];
      if (defaultFinding) {
        section.push(`${category}: ${defaultFinding}`);
      }
    }
  }

  section.push('');
  return section;
}

/**
 * Generate default section content (no custom findings)
 */
function generateDefaultSection(
  sectionName: SectionName,
  facility: Facility,
  context: GenerationContext
): string[] {
  const section: string[] = [];

  // Header
  const header =
    sectionName === 'chest'
      ? 'CT CHEST WITHOUT CONTRAST:'
      : 'CT ABDOMEN AND PELVIS WITHOUT CONTRAST:';
  section.push(header);
  section.push('');

  // Technique
  section.push('TECHNIQUE:');
  const technique =
    sectionName === 'chest'
      ? facility.technique_template_chest
      : facility.technique_template_abdomen;
  section.push(technique);
  section.push('');

  // Default findings
  section.push('FINDINGS:');

  const template = context.templates.find((t) => t.section_name === sectionName);
  if (template) {
    for (const [category, finding] of Object.entries(template.default_findings)) {
      section.push(`${category}: ${finding}`);
    }
  }

  section.push('');
  return section;
}

/**
 * Process a finding and generate its impression
 */
async function processFindingImpression(
  finding: string,
  sectionName: SectionName,
  context: GenerationContext,
  impressions: string[]
): Promise<void> {
  // Try to match impression from database
  const impression = matchImpression(finding, context.patterns, sectionName);

  if (impression) {
    impressions.push(impression);
    return;
  }

  // Log unmatched finding
  if (context.onUnmatchedFinding) {
    await context.onUnmatchedFinding(finding, sectionName);
  }

  // Generate impression with Claude if enabled
  if (context.useClaudeForUnmatched) {
    try {
      const claudeImpression = await generateImpression(finding, sectionName);
      impressions.push(claudeImpression);
    } catch (error) {
      console.error('Error generating impression:', error);
      impressions.push(`Finding noted: ${finding}`);
    }
  }
}

/**
 * Generate the impressions section
 */
function generateImpressionsSection(impressions: string[]): string[] {
  const section: string[] = ['IMPRESSION:'];

  if (impressions.length > 0) {
    // Remove duplicates while preserving order
    const uniqueImpressions = [...new Set(impressions)];

    uniqueImpressions.forEach((impression, index) => {
      section.push(`${index + 1}. ${impression}`);
    });
  } else {
    section.push('Unremarkable exam.');
  }

  return section;
}
