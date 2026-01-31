// ============================================
// Database Types
// ============================================

export interface Facility {
  id: number;
  name: string;
  technique_template_chest: string;
  technique_template_abdomen: string;
  created_at: string;
  updated_at: string;
}

export interface ReportTemplate {
  id: number;
  section_name: SectionName;
  default_findings: Record<string, string>;
  created_at: string;
}

export interface ImpressionPattern {
  id: number;
  finding_pattern: string;
  section_name: SectionName;
  impression_text: string;
  created_at: string;
}

export interface UnmatchedFinding {
  id: number;
  finding: string;
  section_name: SectionName;
  created_at: string;
}

export interface Profile {
  id: string;
  email: string | null;
  first_name: string | null;
  last_name: string | null;
  is_admin: boolean;
  created_at: string;
  updated_at: string;
}

// ============================================
// Application Types
// ============================================

export type StudyType = 'Full Body' | 'Chest' | 'Abdomen and Pelvis';

export type SectionName = 'chest' | 'abdomen_pelvis';

export interface SectionsData {
  chest: string;
  abdomen_pelvis: string;
}

export interface ReportGenerationRequest {
  facility_name: string;
  study_type: StudyType;
  sections_data: SectionsData;
  image_data?: string;
}

export interface ReportGenerationResponse {
  report: string;
  success: boolean;
  error?: string;
}

// ============================================
// Claude API Types
// ============================================

export interface ProcessFindingsRequest {
  findings: string;
  section: SectionName;
}

export interface AnalyzeImageRequest {
  image_data: string;
  study_type: StudyType;
}

export interface GenerateImpressionRequest {
  finding: string;
  section_name: SectionName;
}

export interface CategorizeFindingsRequest {
  findings: string[];
  categories: string[];
  section_name: SectionName;
}

export interface ClaudeApiResponse<T = string> {
  result: T;
  preview?: boolean;
  error?: string;
}

// ============================================
// Auth Types
// ============================================

export interface AuthUser {
  id: string;
  email: string;
}

export interface AuthState {
  user: AuthUser | null;
  profile: Profile | null;
  isLoading: boolean;
  isDemo: boolean;
  isAdmin: boolean;
}

// ============================================
// Form Types
// ============================================

export interface FacilityFormData {
  name: string;
  technique_template_chest: string;
  technique_template_abdomen: string;
}

export interface ImpressionPatternFormData {
  finding_pattern: string;
  section_name: SectionName;
  impression_text: string;
}
