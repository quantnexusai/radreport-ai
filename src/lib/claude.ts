import Anthropic from '@anthropic-ai/sdk';
import { SectionName, StudyType } from './types';

// Initialize Anthropic client
const getAnthropicClient = () => {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    throw new Error('ANTHROPIC_API_KEY is not configured');
  }
  return new Anthropic({ apiKey });
};

const MODEL = 'claude-sonnet-4-20250514';
const MAX_RETRIES = 3;

/**
 * Retry wrapper with exponential backoff
 * Ported from Python implementation (utils/claude_client.py:44-104)
 */
async function withRetry<T>(fn: () => Promise<T>): Promise<T> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;

      // Check for rate limit error
      if (error instanceof Anthropic.RateLimitError) {
        const waitTime = Math.min(Math.pow(2, attempt + 1), 60) * 1000;
        console.log(`Rate limited, waiting ${waitTime / 1000}s before retry...`);
        await new Promise((resolve) => setTimeout(resolve, waitTime));
        continue;
      }

      // Check for timeout/overload
      if (error instanceof Anthropic.APIConnectionError) {
        const waitTime = Math.pow(2, attempt) * 1000;
        console.log(`Connection error, waiting ${waitTime / 1000}s before retry...`);
        await new Promise((resolve) => setTimeout(resolve, waitTime));
        continue;
      }

      // For other errors, throw immediately
      throw error;
    }
  }

  throw lastError || new Error('Max retries exceeded');
}

/**
 * Process raw findings into properly formatted text
 * Ported from Python implementation (utils/claude_client.py:106-142)
 */
export async function processFindings(
  findings: string,
  section: SectionName
): Promise<string> {
  const sectionLabel = section === 'chest' ? 'chest' : 'abdomen and pelvis';

  const prompt = `Please convert these radiology findings into properly formatted, grammatically correct complete sentences for a ${sectionLabel} CT report:

${findings}

Return only the formatted findings with no additional commentary. Each finding should be on its own line. Maintain all medical details exactly as provided.`;

  const anthropic = getAnthropicClient();

  const response = await withRetry(() =>
    anthropic.messages.create({
      model: MODEL,
      max_tokens: 1000,
      temperature: 0,
      system:
        'You are a radiology report assistant that helps format findings into proper medical terminology and grammar. You never change measurements or clinical observations.',
      messages: [{ role: 'user', content: prompt }],
    })
  );

  const textContent = response.content.find((c) => c.type === 'text');
  return textContent ? textContent.text : findings;
}

/**
 * Analyze CT scan image using Claude's vision capabilities
 * Ported from Python implementation (utils/claude_client.py:144-206)
 */
export async function analyzeImage(
  imageData: string,
  studyType: StudyType
): Promise<string> {
  const prompt = `Please analyze this ${studyType} CT scan image and provide any notable observations that might complement the radiologist's findings. Focus only on obvious abnormalities visible in this single image. Be conservative and specific in your assessment.

If you identify any clear abnormalities, describe them in detail including:
1. Location (which anatomical structure/region)
2. Size (if measurable)
3. Characteristics (density, shape, borders)
4. Significance (normal variant, potentially concerning, etc.)

If no significant abnormalities are evident, state that clearly.`;

  const anthropic = getAnthropicClient();

  try {
    // Ensure proper base64 format
    const base64Data = imageData.includes('base64,')
      ? imageData.split('base64,')[1]
      : imageData;

    const response = await withRetry(() =>
      anthropic.messages.create({
        model: MODEL,
        max_tokens: 1000,
        temperature: 0,
        system:
          'You are a radiology AI assistant. Be conservative in your assessments. Only report findings you are confident about. Always recommend radiologist review for final interpretation.',
        messages: [
          {
            role: 'user',
            content: [
              {
                type: 'image',
                source: {
                  type: 'base64',
                  media_type: 'image/jpeg',
                  data: base64Data,
                },
              },
              {
                type: 'text',
                text: prompt,
              },
            ],
          },
        ],
      })
    );

    const textContent = response.content.find((c) => c.type === 'text');
    return textContent ? textContent.text : 'Unable to analyze image.';
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);

    // Handle specific error cases
    if (errorMessage.includes('413') || errorMessage.includes('too large')) {
      return 'The image was too large to process. Please use a smaller image.';
    }

    if (errorMessage.includes('unsupported') || errorMessage.includes('format')) {
      return 'The image format is not supported. Please use JPEG or PNG.';
    }

    console.error('Error analyzing image:', error);
    return 'Unable to analyze image due to an error.';
  }
}

/**
 * Generate clinical impression for a finding
 * Ported from Python implementation (utils/claude_client.py:251-291)
 */
export async function generateImpression(
  finding: string,
  sectionName: SectionName
): Promise<string> {
  const sectionLabel = sectionName === 'chest' ? 'chest' : 'abdomen and pelvis';

  const prompt = `Generate an appropriate impression for the following radiology finding in the ${sectionLabel} section:

Finding: ${finding}

The impression should:
1. Be concise (typically 1-2 sentences)
2. Use standard radiological terminology
3. Include relevant clinical implications if appropriate
4. Suggest follow-up if needed based on standard guidelines

Return only the impression text with no additional commentary.`;

  const anthropic = getAnthropicClient();

  const response = await withRetry(() =>
    anthropic.messages.create({
      model: MODEL,
      max_tokens: 150,
      temperature: 0,
      system:
        'You are a radiology report assistant that generates appropriate impression text for findings. You follow standard radiological guidelines for follow-up recommendations.',
      messages: [{ role: 'user', content: prompt }],
    })
  );

  const textContent = response.content.find((c) => c.type === 'text');
  return textContent ? textContent.text : `Finding noted: ${finding}`;
}

/**
 * Categorize findings into template categories
 * Ported from Python implementation (utils/claude_client.py:293-376)
 */
export async function categorizeFindings(
  findings: string[],
  categories: string[],
  sectionName: SectionName
): Promise<Record<string, string>> {
  if (findings.length === 0 || categories.length === 0) {
    return {};
  }

  const sectionLabel = sectionName === 'chest' ? 'chest' : 'abdomen and pelvis';
  const categoriesStr = categories.map((c) => `- ${c}`).join('\n');
  const findingsStr = findings.map((f, i) => `${i + 1}. ${f}`).join('\n');

  const prompt = `Categorize each of the following radiology findings into the most appropriate category from the list below. Each finding should be assigned to exactly one category.

Section: ${sectionLabel}

Available categories:
${categoriesStr}

Findings to categorize:
${findingsStr}

For each finding, return only the finding text and the selected category in this exact format:
Finding: [exact finding text]
Category: [exact category name from the list]

Provide this for each finding, with one blank line between entries.`;

  const anthropic = getAnthropicClient();

  const response = await withRetry(() =>
    anthropic.messages.create({
      model: MODEL,
      max_tokens: 1000,
      temperature: 0,
      system:
        'You are a radiology report assistant that categorizes findings into appropriate anatomical sections.',
      messages: [{ role: 'user', content: prompt }],
    })
  );

  const textContent = response.content.find((c) => c.type === 'text');
  if (!textContent) {
    return {};
  }

  // Parse the response
  const result: Record<string, string> = {};
  const lines = textContent.text.split('\n');

  let currentFinding = '';
  for (const line of lines) {
    const trimmed = line.trim();

    if (trimmed.startsWith('Finding:')) {
      currentFinding = trimmed.substring(8).trim();
    } else if (trimmed.startsWith('Category:') && currentFinding) {
      const category = trimmed.substring(9).trim();

      // Validate category is in our list
      if (categories.includes(category)) {
        result[currentFinding] = category;
      }

      currentFinding = '';
    }
  }

  return result;
}
