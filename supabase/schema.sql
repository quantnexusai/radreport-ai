-- RadReport AI Database Schema
-- Run this in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- FACILITIES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.facilities (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    technique_template_chest TEXT NOT NULL DEFAULT '',
    technique_template_abdomen TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- REPORT TEMPLATES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.report_templates (
    id SERIAL PRIMARY KEY,
    section_name TEXT NOT NULL UNIQUE,
    default_findings JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default templates
INSERT INTO public.report_templates (section_name, default_findings) VALUES
('chest', '{
    "Heart": "Normal size and configuration",
    "Lungs": "Clear. No focal consolidation, pleural effusion, or pneumothorax",
    "Mediastinum": "Unremarkable. No lymphadenopathy",
    "Pleura": "No effusion or thickening",
    "Osseous structures": "No acute osseous abnormality"
}'::jsonb),
('abdomen_pelvis', '{
    "Liver": "Normal size and attenuation. No focal lesion",
    "Gallbladder": "Unremarkable. No stones or wall thickening",
    "Pancreas": "Normal. No focal lesion or ductal dilatation",
    "Spleen": "Normal size",
    "Adrenal glands": "Unremarkable",
    "Kidneys": "Normal size and enhancement. No hydronephrosis or stones",
    "Bowel": "No obstruction or wall thickening",
    "Bladder": "Unremarkable",
    "Pelvic organs": "Unremarkable",
    "Vasculature": "Unremarkable",
    "Lymph nodes": "No pathologic lymphadenopathy",
    "Osseous structures": "No acute osseous abnormality"
}'::jsonb)
ON CONFLICT (section_name) DO NOTHING;

-- ============================================
-- IMPRESSION LOOKUP TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.impression_lookup (
    id SERIAL PRIMARY KEY,
    finding_pattern TEXT NOT NULL,
    section_name TEXT NOT NULL,
    impression_text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for faster pattern lookups
CREATE INDEX IF NOT EXISTS idx_impression_lookup_section
    ON public.impression_lookup(section_name);

-- ============================================
-- UNMATCHED FINDINGS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.unmatched_findings (
    id SERIAL PRIMARY KEY,
    finding TEXT NOT NULL,
    section_name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for ordering by created_at
CREATE INDEX IF NOT EXISTS idx_unmatched_findings_created
    ON public.unmatched_findings(created_at DESC);

-- ============================================
-- USER PROFILES TABLE (for auth)
-- ============================================
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    first_name TEXT,
    last_name TEXT,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- ROW LEVEL SECURITY POLICIES
-- ============================================

-- Enable RLS on all tables
ALTER TABLE public.facilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.report_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.impression_lookup ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.unmatched_findings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Public read access for reference tables
CREATE POLICY "Public read facilities" ON public.facilities
    FOR SELECT USING (true);

CREATE POLICY "Public read templates" ON public.report_templates
    FOR SELECT USING (true);

CREATE POLICY "Public read impressions" ON public.impression_lookup
    FOR SELECT USING (true);

-- Authenticated users can read unmatched findings
CREATE POLICY "Authenticated read unmatched" ON public.unmatched_findings
    FOR SELECT TO authenticated USING (true);

-- Admin write policies
CREATE POLICY "Admin manage facilities" ON public.facilities
    FOR ALL TO authenticated
    USING (EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND is_admin = true))
    WITH CHECK (EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND is_admin = true));

CREATE POLICY "Admin manage impressions" ON public.impression_lookup
    FOR ALL TO authenticated
    USING (EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND is_admin = true))
    WITH CHECK (EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND is_admin = true));

CREATE POLICY "Admin manage unmatched" ON public.unmatched_findings
    FOR ALL TO authenticated
    USING (EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND is_admin = true))
    WITH CHECK (EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND is_admin = true));

-- Users can only see and update their own profile
CREATE POLICY "Users view own profile" ON public.profiles
    FOR SELECT TO authenticated
    USING (auth.uid() = id);

CREATE POLICY "Users update own profile" ON public.profiles
    FOR UPDATE TO authenticated
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- Allow inserting unmatched findings (for logging)
CREATE POLICY "Insert unmatched findings" ON public.unmatched_findings
    FOR INSERT TO authenticated
    WITH CHECK (true);

-- ============================================
-- TRIGGER: Auto-create profile on user signup
-- ============================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, first_name, last_name)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.raw_user_meta_data->>'first_name',
        NEW.raw_user_meta_data->>'last_name'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ============================================
-- TRIGGER: Update updated_at timestamp
-- ============================================
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_facilities_updated_at ON public.facilities;
CREATE TRIGGER update_facilities_updated_at
    BEFORE UPDATE ON public.facilities
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

DROP TRIGGER IF EXISTS update_profiles_updated_at ON public.profiles;
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();
