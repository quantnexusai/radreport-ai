'use client';

import { useState, useEffect } from 'react';
import { RotateCcw, CheckCircle, Download, Upload, Image as ImageIcon } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { isDemoMode, generateDemoReport, DEMO_FACILITIES } from '@/lib/demo-data';
import { Facility, StudyType, SectionsData } from '@/lib/types';
import { Button } from '../ui/Button';
import { Select } from '../ui/Select';
import { TextArea } from '../ui/TextArea';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { LoadingSpinner } from '../ui/LoadingSpinner';

const STUDY_TYPES: { value: StudyType; label: string }[] = [
  { value: 'Full Body', label: 'Full Body' },
  { value: 'Chest', label: 'Chest' },
  { value: 'Abdomen and Pelvis', label: 'Abdomen and Pelvis' },
];

export function ReportGenerator() {
  const { isDemo } = useAuth();

  // Form state
  const [studyType, setStudyType] = useState<StudyType>('Full Body');
  const [selectedFacility, setSelectedFacility] = useState('');
  const [chestFindings, setChestFindings] = useState('');
  const [abdomenFindings, setAbdomenFindings] = useState('');
  const [imageData, setImageData] = useState<string | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  // Data state
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [isLoadingFacilities, setIsLoadingFacilities] = useState(true);

  // Report state
  const [report, setReport] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');

  // Fetch facilities on mount
  useEffect(() => {
    const fetchFacilities = async () => {
      try {
        if (isDemoMode()) {
          setFacilities(DEMO_FACILITIES);
          setSelectedFacility(DEMO_FACILITIES[0]?.name || '');
          setIsLoadingFacilities(false);
          return;
        }

        const response = await fetch('/api/facilities');
        if (!response.ok) throw new Error('Failed to fetch facilities');
        const data = await response.json();
        setFacilities(data);
        if (data.length > 0) {
          setSelectedFacility(data[0].name);
        }
      } catch (err) {
        console.error('Error fetching facilities:', err);
        setError('Failed to load facilities');
      } finally {
        setIsLoadingFacilities(false);
      }
    };

    fetchFacilities();
  }, []);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Please upload an image file (JPEG or PNG)');
      return;
    }

    // Validate file size (10MB max)
    if (file.size > 10 * 1024 * 1024) {
      setError('Image must be less than 10MB');
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      const result = event.target?.result as string;
      setImagePreview(result);
      // Extract base64 data
      const base64 = result.split(',')[1];
      setImageData(base64);
      setError('');
    };
    reader.readAsDataURL(file);
  };

  const handleReset = () => {
    setStudyType('Full Body');
    setSelectedFacility(facilities[0]?.name || '');
    setChestFindings('');
    setAbdomenFindings('');
    setImageData(null);
    setImagePreview(null);
    setReport('');
    setError('');
  };

  const handleGenerate = async () => {
    if (!selectedFacility) {
      setError('Please select a facility');
      return;
    }

    const sectionsData: SectionsData = {
      chest: chestFindings,
      abdomen_pelvis: abdomenFindings,
    };

    // Check if at least one section has findings
    const hasFindings =
      (studyType !== 'Abdomen and Pelvis' && chestFindings.trim()) ||
      (studyType !== 'Chest' && abdomenFindings.trim());

    setIsGenerating(true);
    setError('');

    try {
      // Demo mode
      if (isDemoMode()) {
        const demoReport = generateDemoReport(selectedFacility, studyType, sectionsData);
        setReport(demoReport);
        setIsGenerating(false);
        return;
      }

      const response = await fetch('/api/reports/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          facility_name: selectedFacility,
          study_type: studyType,
          sections_data: sectionsData,
          image_data: imageData,
        }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Failed to generate report');
      }

      setReport(data.report);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate report');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = () => {
    if (!report) return;

    const blob = new Blob([report], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `radreport-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const showChestSection = studyType === 'Full Body' || studyType === 'Chest';
  const showAbdomenSection = studyType === 'Full Body' || studyType === 'Abdomen and Pelvis';

  if (isLoadingFacilities) {
    return <LoadingSpinner size="lg" text="Loading..." />;
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Input Section */}
      <div className="space-y-6">
        {/* Study Type & Facility */}
        <Card>
          <CardHeader>
            <CardTitle>Study Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Select
              label="Study Type"
              options={STUDY_TYPES}
              value={studyType}
              onChange={(e) => setStudyType(e.target.value as StudyType)}
            />
            <Select
              label="Facility"
              options={facilities.map((f) => ({ value: f.name, label: f.name }))}
              value={selectedFacility}
              onChange={(e) => setSelectedFacility(e.target.value)}
              placeholder="Select a facility"
            />
          </CardContent>
        </Card>

        {/* Findings Input */}
        <Card>
          <CardHeader>
            <CardTitle>Findings</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {showChestSection && (
              <TextArea
                label="Chest Findings"
                placeholder="Enter chest findings..."
                value={chestFindings}
                onChange={(e) => setChestFindings(e.target.value)}
                rows={6}
              />
            )}
            {showAbdomenSection && (
              <TextArea
                label="Abdomen and Pelvis Findings"
                placeholder="Enter abdomen and pelvis findings..."
                value={abdomenFindings}
                onChange={(e) => setAbdomenFindings(e.target.value)}
                rows={6}
              />
            )}
          </CardContent>
        </Card>

        {/* Image Upload */}
        <Card>
          <CardHeader>
            <CardTitle>Image Upload (Optional)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-primary-400 hover:bg-gray-50 transition-colors">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <Upload className="w-8 h-8 mb-2 text-gray-400" />
                  <p className="text-sm text-gray-500">
                    Click to upload or drag and drop
                  </p>
                  <p className="text-xs text-gray-400">
                    JPEG or PNG (max 10MB)
                  </p>
                </div>
                <input
                  type="file"
                  className="hidden"
                  accept="image/jpeg,image/png"
                  onChange={handleImageUpload}
                />
              </label>
              {imagePreview && (
                <div className="relative">
                  <img
                    src={imagePreview}
                    alt="Preview"
                    className="w-full h-48 object-cover rounded-lg"
                  />
                  <button
                    onClick={() => {
                      setImageData(null);
                      setImagePreview(null);
                    }}
                    className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600"
                  >
                    <RotateCcw className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Output Section */}
      <div className="space-y-6">
        <Card className="h-full flex flex-col">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Generated Report</CardTitle>
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={handleReset}
                  disabled={isGenerating}
                >
                  <RotateCcw className="h-4 w-4 mr-1" />
                  Reset
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleGenerate}
                  isLoading={isGenerating}
                >
                  <CheckCircle className="h-4 w-4 mr-1" />
                  Generate
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col">
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm">
                {error}
              </div>
            )}
            <textarea
              value={report}
              onChange={(e) => setReport(e.target.value)}
              className="flex-1 w-full p-4 border border-gray-300 rounded-md font-mono text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Generated report will appear here..."
              rows={20}
            />
            {report && (
              <Button
                variant="accent"
                className="mt-4"
                onClick={handleDownload}
              >
                <Download className="h-4 w-4 mr-2" />
                Download Report
              </Button>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
