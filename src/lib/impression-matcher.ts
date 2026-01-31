import { ImpressionPattern, SectionName } from './types';

/**
 * Three-tier impression matching algorithm
 * Ported from Python implementation (utils/supabase_client.py:172-233)
 *
 * Matching tiers:
 * 1. Exact match (case-insensitive)
 * 2. Partial match with scoring (longer pattern = higher score, prefix bonus)
 * 3. Word-based matching (common words threshold)
 */
export function matchImpression(
  finding: string,
  patterns: ImpressionPattern[],
  sectionName: SectionName
): string | null {
  const findingLower = finding.toLowerCase().trim();

  // Filter patterns by section
  const sectionPatterns = patterns.filter(
    (p) => p.section_name === sectionName
  );

  if (sectionPatterns.length === 0) {
    return null;
  }

  // ============================================
  // Tier 1: Exact match (case-insensitive)
  // ============================================
  const exactMatch = sectionPatterns.find(
    (p) => p.finding_pattern.toLowerCase().trim() === findingLower
  );

  if (exactMatch) {
    return exactMatch.impression_text;
  }

  // ============================================
  // Tier 2: Partial match with scoring
  // Score = pattern length + 5 (if prefix match)
  // ============================================
  interface ScoredMatch {
    score: number;
    impression: string;
  }

  const partialMatches: ScoredMatch[] = [];

  for (const pattern of sectionPatterns) {
    const patternLower = pattern.finding_pattern.toLowerCase().trim();

    // Check if pattern is contained in finding
    if (findingLower.includes(patternLower)) {
      let score = patternLower.length;

      // Bonus for prefix match
      if (findingLower.startsWith(patternLower)) {
        score += 5;
      }

      partialMatches.push({
        score,
        impression: pattern.impression_text,
      });
    }
  }

  if (partialMatches.length > 0) {
    // Sort by score descending and return highest
    partialMatches.sort((a, b) => b.score - a.score);
    return partialMatches[0].impression;
  }

  // ============================================
  // Tier 3: Word-based matching
  // Require at least min(2, pattern_word_count) common words
  // ============================================
  const findingWords = findingLower.split(/\s+/).filter((w) => w.length > 2);
  const wordMatches: ScoredMatch[] = [];

  for (const pattern of sectionPatterns) {
    const patternWords = pattern.finding_pattern
      .toLowerCase()
      .split(/\s+/)
      .filter((w) => w.length > 2);

    // Find common words
    const commonWords = findingWords.filter((w) => patternWords.includes(w));
    const threshold = Math.min(2, patternWords.length);

    if (commonWords.length >= threshold) {
      wordMatches.push({
        score: commonWords.length,
        impression: pattern.impression_text,
      });
    }
  }

  if (wordMatches.length > 0) {
    // Sort by score descending and return highest
    wordMatches.sort((a, b) => b.score - a.score);
    return wordMatches[0].impression;
  }

  // No match found
  return null;
}

/**
 * Batch process findings and return impressions
 */
export function matchImpressions(
  findings: string[],
  patterns: ImpressionPattern[],
  sectionName: SectionName
): { matched: Map<string, string>; unmatched: string[] } {
  const matched = new Map<string, string>();
  const unmatched: string[] = [];

  for (const finding of findings) {
    const impression = matchImpression(finding, patterns, sectionName);

    if (impression) {
      matched.set(finding, impression);
    } else {
      unmatched.push(finding);
    }
  }

  return { matched, unmatched };
}
