import {
  Facility,
  ReportTemplate,
  ImpressionPattern,
  UnmatchedFinding,
  Profile,
  SectionsData,
  StudyType,
} from './types';

// ============================================
// Demo Mode Detection
// ============================================

export function isDemoMode(): boolean {
  // Check explicit demo mode flag
  if (process.env.NEXT_PUBLIC_DEMO_MODE === 'true') {
    return true;
  }

  // Check if Supabase is configured
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  return !supabaseUrl || supabaseUrl === '' || supabaseUrl.includes('placeholder');
}

// ============================================
// Demo User & Profile
// ============================================

export const DEMO_USER = {
  id: 'demo-user-id',
  email: 'demo@radreport.ai',
};

export const DEMO_PROFILE: Profile = {
  id: 'demo-user-id',
  email: 'demo@radreport.ai',
  first_name: 'Demo',
  last_name: 'User',
  is_admin: true, // Allow admin access in demo mode
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

// ============================================
// Demo Facilities
// ============================================

export const DEMO_FACILITIES: Facility[] = [
  {
    id: 1,
    name: 'Demo Medical Center',
    technique_template_chest:
      'Thin section axial images were obtained through the chest without intravenous contrast. Multiplanar reformations were reviewed.',
    technique_template_abdomen:
      'Thin section axial images were obtained through the abdomen and pelvis without intravenous contrast. Multiplanar reformations were reviewed.',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 2,
    name: 'City Hospital Radiology',
    technique_template_chest:
      'CT of the chest was performed without IV contrast using helical technique. Images were reviewed in lung and soft tissue windows.',
    technique_template_abdomen:
      'CT of the abdomen and pelvis was performed without IV contrast using helical technique. Coronal and sagittal reformations were reviewed.',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

// ============================================
// Demo Report Templates
// ============================================

export const DEMO_TEMPLATES: ReportTemplate[] = [
  {
    id: 1,
    section_name: 'chest',
    default_findings: {
      Heart: 'Normal size and configuration',
      Lungs: 'Clear. No focal consolidation, pleural effusion, or pneumothorax',
      Mediastinum: 'Unremarkable. No lymphadenopathy',
      Pleura: 'No effusion or thickening',
      'Osseous structures': 'No acute osseous abnormality',
    },
    created_at: new Date().toISOString(),
  },
  {
    id: 2,
    section_name: 'abdomen_pelvis',
    default_findings: {
      Liver: 'Normal size and attenuation. No focal lesion',
      Gallbladder: 'Unremarkable. No stones or wall thickening',
      Pancreas: 'Normal. No focal lesion or ductal dilatation',
      Spleen: 'Normal size',
      'Adrenal glands': 'Unremarkable',
      Kidneys: 'Normal size and enhancement. No hydronephrosis or stones',
      Bowel: 'No obstruction or wall thickening',
      Bladder: 'Unremarkable',
      'Pelvic organs': 'Unremarkable',
      Vasculature: 'Unremarkable',
      'Lymph nodes': 'No pathologic lymphadenopathy',
      'Osseous structures': 'No acute osseous abnormality',
    },
    created_at: new Date().toISOString(),
  },
];

// ============================================
// Demo Impression Patterns
// ============================================

export const DEMO_PATTERNS: ImpressionPattern[] = [
  {
    id: 1,
    finding_pattern: 'enlarged liver',
    section_name: 'abdomen_pelvis',
    impression_text: 'Hepatomegaly noted. Clinical correlation recommended.',
    created_at: new Date().toISOString(),
  },
  {
    id: 2,
    finding_pattern: 'pulmonary nodule',
    section_name: 'chest',
    impression_text:
      'Pulmonary nodule identified. Follow-up CT recommended per Fleischner Society guidelines based on size and patient risk factors.',
    created_at: new Date().toISOString(),
  },
  {
    id: 3,
    finding_pattern: 'pleural effusion',
    section_name: 'chest',
    impression_text: 'Pleural effusion present. Clinical correlation for etiology is recommended.',
    created_at: new Date().toISOString(),
  },
  {
    id: 4,
    finding_pattern: 'kidney stone',
    section_name: 'abdomen_pelvis',
    impression_text: 'Nephrolithiasis identified. Urology consultation may be warranted.',
    created_at: new Date().toISOString(),
  },
  {
    id: 5,
    finding_pattern: 'gallstone',
    section_name: 'abdomen_pelvis',
    impression_text: 'Cholelithiasis without evidence of acute cholecystitis.',
    created_at: new Date().toISOString(),
  },
];

// ============================================
// Demo Unmatched Findings
// ============================================

export const DEMO_UNMATCHED_FINDINGS: UnmatchedFinding[] = [
  {
    id: 1,
    finding: 'small pericardial effusion',
    section_name: 'chest',
    created_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
  },
  {
    id: 2,
    finding: 'mild hepatic steatosis',
    section_name: 'abdomen_pelvis',
    created_at: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
  },
];

// ============================================
// Demo Report Generator
// ============================================

export function generateDemoReport(
  facilityName: string,
  studyType: StudyType,
  sectionsData: SectionsData
): string {
  const facility = DEMO_FACILITIES.find((f) => f.name === facilityName) || DEMO_FACILITIES[0];
  const sections: string[] = [];

  const includeChest = studyType === 'Full Body' || studyType === 'Chest';
  const includeAbdomen = studyType === 'Full Body' || studyType === 'Abdomen and Pelvis';

  // Chest section
  if (includeChest) {
    sections.push('CT CHEST WITHOUT CONTRAST:');
    sections.push('');
    sections.push('TECHNIQUE:');
    sections.push(facility.technique_template_chest);
    sections.push('');
    sections.push('FINDINGS:');

    if (sectionsData.chest && sectionsData.chest.trim()) {
      sections.push(sectionsData.chest);
    } else {
      const chestTemplate = DEMO_TEMPLATES.find((t) => t.section_name === 'chest');
      if (chestTemplate) {
        Object.entries(chestTemplate.default_findings).forEach(([category, finding]) => {
          sections.push(`${category}: ${finding}`);
        });
      }
    }
    sections.push('');
  }

  // Abdomen section
  if (includeAbdomen) {
    sections.push('CT ABDOMEN AND PELVIS WITHOUT CONTRAST:');
    sections.push('');
    sections.push('TECHNIQUE:');
    sections.push(facility.technique_template_abdomen);
    sections.push('');
    sections.push('FINDINGS:');

    if (sectionsData.abdomen_pelvis && sectionsData.abdomen_pelvis.trim()) {
      sections.push(sectionsData.abdomen_pelvis);
    } else {
      const abdomenTemplate = DEMO_TEMPLATES.find((t) => t.section_name === 'abdomen_pelvis');
      if (abdomenTemplate) {
        Object.entries(abdomenTemplate.default_findings).forEach(([category, finding]) => {
          sections.push(`${category}: ${finding}`);
        });
      }
    }
    sections.push('');
  }

  // Impression
  sections.push('IMPRESSION:');
  if (
    (!sectionsData.chest || !sectionsData.chest.trim()) &&
    (!sectionsData.abdomen_pelvis || !sectionsData.abdomen_pelvis.trim())
  ) {
    sections.push('Unremarkable exam.');
  } else {
    sections.push('1. Findings as described above.');
    sections.push('2. Clinical correlation recommended.');
  }

  sections.push('');
  sections.push('--- Demo Mode Report ---');
  sections.push('This is a sample report generated in demo mode.');
  sections.push('Connect Supabase and Anthropic API for full AI-powered functionality.');

  return sections.join('\n');
}

// ============================================
// Demo Claude API Responses
// ============================================

export function getDemoProcessedFindings(findings: string): string {
  // Simple formatting for demo
  return findings
    .split('\n')
    .filter((line) => line.trim())
    .map((line) => {
      // Capitalize first letter
      const trimmed = line.trim();
      return trimmed.charAt(0).toUpperCase() + trimmed.slice(1);
    })
    .join('\n');
}

export function getDemoImageAnalysis(): string {
  return 'Demo Mode: Image analysis is simulated. In production, Claude AI would analyze the uploaded CT scan for abnormalities.';
}

export function getDemoImpression(finding: string): string {
  return `Demo impression for: "${finding}". Connect Anthropic API for AI-generated impressions.`;
}

export function getDemoCategorizedFindings(
  findings: string[],
  categories: string[]
): Record<string, string> {
  const result: Record<string, string> = {};

  // Simple assignment for demo - distribute findings across categories
  findings.forEach((finding, index) => {
    const categoryIndex = index % categories.length;
    result[finding] = categories[categoryIndex];
  });

  return result;
}
