'use client';

import { useState, useEffect } from 'react';
import { Plus, Trash2, Edit2, ChevronDown, ChevronUp } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import {
  isDemoMode,
  DEMO_FACILITIES,
  DEMO_PATTERNS,
  DEMO_UNMATCHED_FINDINGS,
} from '@/lib/demo-data';
import {
  Facility,
  ImpressionPattern,
  UnmatchedFinding,
  SectionName,
} from '@/lib/types';
import { Button } from '../../ui/Button';
import { Input } from '../../ui/Input';
import { TextArea } from '../../ui/TextArea';
import { Select } from '../../ui/Select';
import { Card, CardHeader, CardTitle, CardContent } from '../../ui/Card';
import { Tabs, TabList, Tab, TabPanel } from '../../ui/Tabs';
import { LoadingSpinner } from '../../ui/LoadingSpinner';

const SECTION_OPTIONS = [
  { value: 'chest', label: 'Chest' },
  { value: 'abdomen_pelvis', label: 'Abdomen and Pelvis' },
];

export function AdminPanel() {
  const { isDemo } = useAuth();

  // Data state
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [patterns, setPatterns] = useState<ImpressionPattern[]>([]);
  const [unmatchedFindings, setUnmatchedFindings] = useState<UnmatchedFinding[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch all data
  useEffect(() => {
    const fetchData = async () => {
      try {
        if (isDemoMode()) {
          setFacilities(DEMO_FACILITIES);
          setPatterns(DEMO_PATTERNS);
          setUnmatchedFindings(DEMO_UNMATCHED_FINDINGS);
          setIsLoading(false);
          return;
        }

        const [facilitiesRes, patternsRes, unmatchedRes] = await Promise.all([
          fetch('/api/facilities'),
          fetch('/api/impression-patterns'),
          fetch('/api/unmatched-findings'),
        ]);

        const facilitiesData = await facilitiesRes.json();
        const patternsData = await patternsRes.json();
        const unmatchedData = await unmatchedRes.json();

        setFacilities(Array.isArray(facilitiesData) ? facilitiesData : []);
        setPatterns(Array.isArray(patternsData) ? patternsData : []);
        setUnmatchedFindings(Array.isArray(unmatchedData) ? unmatchedData : []);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  if (isLoading) {
    return <LoadingSpinner size="lg" text="Loading admin data..." />;
  }

  return (
    <Tabs defaultTab="facilities">
      <TabList>
        <Tab value="facilities">Facilities</Tab>
        <Tab value="templates">Templates</Tab>
        <Tab value="patterns">Impression Patterns</Tab>
        <Tab value="unmatched">Unmatched Findings</Tab>
      </TabList>

      <TabPanel value="facilities">
        <FacilitiesTab
          facilities={facilities}
          setFacilities={setFacilities}
          isDemo={isDemo}
        />
      </TabPanel>

      <TabPanel value="templates">
        <TemplatesTab facilities={facilities} isDemo={isDemo} />
      </TabPanel>

      <TabPanel value="patterns">
        <PatternsTab
          patterns={patterns}
          setPatterns={setPatterns}
          isDemo={isDemo}
        />
      </TabPanel>

      <TabPanel value="unmatched">
        <UnmatchedTab
          findings={unmatchedFindings}
          setFindings={setUnmatchedFindings}
          isDemo={isDemo}
        />
      </TabPanel>
    </Tabs>
  );
}

// ============================================
// Facilities Tab
// ============================================

interface FacilitiesTabProps {
  facilities: Facility[];
  setFacilities: (facilities: Facility[]) => void;
  isDemo: boolean;
}

function FacilitiesTab({ facilities, setFacilities }: FacilitiesTabProps) {
  const [name, setName] = useState('');
  const [chestTemplate, setChestTemplate] = useState('');
  const [abdomenTemplate, setAbdomenTemplate] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleAdd = async () => {
    if (!name || !chestTemplate || !abdomenTemplate) {
      setError('All fields are required');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const response = await fetch('/api/facilities', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          technique_template_chest: chestTemplate,
          technique_template_abdomen: abdomenTemplate,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to add facility');
      }

      const newFacility = await response.json();
      setFacilities([...facilities, newFacility]);
      setName('');
      setChestTemplate('');
      setAbdomenTemplate('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add facility');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this facility?')) return;

    try {
      const response = await fetch(`/api/facilities/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Failed to delete facility');

      setFacilities(facilities.filter((f) => f.id !== id));
    } catch {
      setError('Failed to delete facility');
    }
  };

  return (
    <div className="space-y-6">
      {/* Add New Facility */}
      <Card>
        <CardHeader>
          <CardTitle>Add New Facility</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            label="Facility Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., City Hospital Radiology"
          />
          <TextArea
            label="Chest Technique Template"
            value={chestTemplate}
            onChange={(e) => setChestTemplate(e.target.value)}
            placeholder="Enter the technique template for chest CT..."
            rows={3}
          />
          <TextArea
            label="Abdomen Technique Template"
            value={abdomenTemplate}
            onChange={(e) => setAbdomenTemplate(e.target.value)}
            placeholder="Enter the technique template for abdomen CT..."
            rows={3}
          />
          {error && <p className="text-sm text-red-600">{error}</p>}
          <Button onClick={handleAdd} isLoading={isSubmitting}>
            <Plus className="h-4 w-4 mr-2" />
            Add Facility
          </Button>
        </CardContent>
      </Card>

      {/* Existing Facilities */}
      <Card>
        <CardHeader>
          <CardTitle>Existing Facilities ({facilities.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {facilities.map((facility) => (
              <FacilityItem
                key={facility.id}
                facility={facility}
                onDelete={() => handleDelete(facility.id)}
              />
            ))}
            {facilities.length === 0 && (
              <p className="text-gray-500 text-center py-4">No facilities yet</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function FacilityItem({
  facility,
  onDelete,
}: {
  facility: Facility;
  onDelete: () => void;
}) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <div
        className="flex items-center justify-between p-4 bg-gray-50 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span className="font-medium">{facility.name}</span>
        <div className="flex items-center gap-2">
          <Button
            variant="danger"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              onDelete();
            }}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
          {isExpanded ? (
            <ChevronUp className="h-5 w-5 text-gray-400" />
          ) : (
            <ChevronDown className="h-5 w-5 text-gray-400" />
          )}
        </div>
      </div>
      {isExpanded && (
        <div className="p-4 space-y-3">
          <div>
            <p className="text-sm font-medium text-gray-700">Chest Template:</p>
            <p className="text-sm text-gray-600 mt-1">
              {facility.technique_template_chest}
            </p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-700">Abdomen Template:</p>
            <p className="text-sm text-gray-600 mt-1">
              {facility.technique_template_abdomen}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================
// Templates Tab
// ============================================

interface TemplatesTabProps {
  facilities: Facility[];
  isDemo: boolean;
}

function TemplatesTab({ facilities }: TemplatesTabProps) {
  const [selectedFacility, setSelectedFacility] = useState<Facility | null>(
    facilities[0] || null
  );
  const [chestTemplate, setChestTemplate] = useState('');
  const [abdomenTemplate, setAbdomenTemplate] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (selectedFacility) {
      setChestTemplate(selectedFacility.technique_template_chest);
      setAbdomenTemplate(selectedFacility.technique_template_abdomen);
    }
  }, [selectedFacility]);

  const handleUpdate = async () => {
    if (!selectedFacility) return;

    setIsSubmitting(true);
    setMessage('');

    try {
      const response = await fetch(
        `/api/facilities/${selectedFacility.id}/templates`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            technique_template_chest: chestTemplate,
            technique_template_abdomen: abdomenTemplate,
          }),
        }
      );

      if (!response.ok) throw new Error('Failed to update templates');

      setMessage('Templates updated successfully!');
    } catch {
      setMessage('Failed to update templates');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Edit Facility Templates</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Select
          label="Select Facility"
          options={facilities.map((f) => ({ value: f.id.toString(), label: f.name }))}
          value={selectedFacility?.id.toString() || ''}
          onChange={(e) => {
            const facility = facilities.find((f) => f.id.toString() === e.target.value);
            setSelectedFacility(facility || null);
          }}
        />
        {selectedFacility && (
          <>
            <TextArea
              label="Chest Technique Template"
              value={chestTemplate}
              onChange={(e) => setChestTemplate(e.target.value)}
              rows={5}
            />
            <TextArea
              label="Abdomen Technique Template"
              value={abdomenTemplate}
              onChange={(e) => setAbdomenTemplate(e.target.value)}
              rows={5}
            />
            {message && (
              <p
                className={`text-sm ${
                  message.includes('success') ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {message}
              </p>
            )}
            <Button onClick={handleUpdate} isLoading={isSubmitting}>
              <Edit2 className="h-4 w-4 mr-2" />
              Update Templates
            </Button>
          </>
        )}
      </CardContent>
    </Card>
  );
}

// ============================================
// Patterns Tab
// ============================================

interface PatternsTabProps {
  patterns: ImpressionPattern[];
  setPatterns: (patterns: ImpressionPattern[]) => void;
  isDemo: boolean;
}

function PatternsTab({ patterns, setPatterns }: PatternsTabProps) {
  const [findingPattern, setFindingPattern] = useState('');
  const [sectionName, setSectionName] = useState<SectionName>('chest');
  const [impressionText, setImpressionText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleAdd = async () => {
    if (!findingPattern || !impressionText) {
      setError('All fields are required');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const response = await fetch('/api/impression-patterns', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          finding_pattern: findingPattern,
          section_name: sectionName,
          impression_text: impressionText,
        }),
      });

      if (!response.ok) throw new Error('Failed to add pattern');

      const newPattern = await response.json();
      setPatterns([...patterns, newPattern]);
      setFindingPattern('');
      setImpressionText('');
    } catch {
      setError('Failed to add pattern');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this pattern?')) return;

    try {
      const response = await fetch(`/api/impression-patterns/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Failed to delete pattern');

      setPatterns(patterns.filter((p) => p.id !== id));
    } catch {
      setError('Failed to delete pattern');
    }
  };

  return (
    <div className="space-y-6">
      {/* Add New Pattern */}
      <Card>
        <CardHeader>
          <CardTitle>Add New Impression Pattern</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Select
            label="Section"
            options={SECTION_OPTIONS}
            value={sectionName}
            onChange={(e) => setSectionName(e.target.value as SectionName)}
          />
          <Input
            label="Finding Pattern"
            value={findingPattern}
            onChange={(e) => setFindingPattern(e.target.value)}
            placeholder="e.g., enlarged liver"
          />
          <TextArea
            label="Impression Text"
            value={impressionText}
            onChange={(e) => setImpressionText(e.target.value)}
            placeholder="e.g., Hepatomegaly noted. Clinical correlation recommended."
            rows={3}
          />
          {error && <p className="text-sm text-red-600">{error}</p>}
          <Button onClick={handleAdd} isLoading={isSubmitting}>
            <Plus className="h-4 w-4 mr-2" />
            Add Pattern
          </Button>
        </CardContent>
      </Card>

      {/* Existing Patterns */}
      <Card>
        <CardHeader>
          <CardTitle>Existing Patterns ({patterns.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {patterns.map((pattern) => (
              <div
                key={pattern.id}
                className="flex items-start justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex-1">
                  <span className="inline-block px-2 py-0.5 text-xs font-medium bg-primary-100 text-primary-700 rounded mb-1">
                    {pattern.section_name}
                  </span>
                  <p className="font-medium text-sm">{pattern.finding_pattern}</p>
                  <p className="text-sm text-gray-600 mt-1">
                    {pattern.impression_text}
                  </p>
                </div>
                <Button
                  variant="danger"
                  size="sm"
                  onClick={() => handleDelete(pattern.id)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
            {patterns.length === 0 && (
              <p className="text-gray-500 text-center py-4">No patterns yet</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// ============================================
// Unmatched Findings Tab
// ============================================

interface UnmatchedTabProps {
  findings: UnmatchedFinding[];
  setFindings: (findings: UnmatchedFinding[]) => void;
  isDemo: boolean;
}

function UnmatchedTab({ findings, setFindings }: UnmatchedTabProps) {
  const handleDelete = async (id: number) => {
    try {
      const response = await fetch(`/api/unmatched-findings/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Failed to delete finding');

      setFindings(findings.filter((f) => f.id !== id));
    } catch (err) {
      console.error('Failed to delete finding:', err);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Unmatched Findings ({findings.length})</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-gray-600 mb-4">
          These findings did not match any existing patterns. Review them to create
          new impression patterns.
        </p>
        <div className="space-y-3">
          {findings.map((finding) => (
            <div
              key={finding.id}
              className="flex items-start justify-between p-3 bg-amber-50 border border-amber-200 rounded-lg"
            >
              <div className="flex-1">
                <span className="inline-block px-2 py-0.5 text-xs font-medium bg-amber-100 text-amber-700 rounded mb-1">
                  {finding.section_name}
                </span>
                <p className="text-sm">{finding.finding}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {new Date(finding.created_at).toLocaleDateString()}
                </p>
              </div>
              <Button
                variant="danger"
                size="sm"
                onClick={() => handleDelete(finding.id)}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          ))}
          {findings.length === 0 && (
            <p className="text-gray-500 text-center py-4">
              No unmatched findings
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
