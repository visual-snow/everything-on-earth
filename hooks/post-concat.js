#!/usr/bin/env node

/**
 * Hook: post-concat.js
 * Trigger: PostToolUse on Bash
 * Purpose: Detect when lead concatenates discovery files, auto-trigger dedup.
 *
 * Looks for raw-discovery.json in the Bash command output.
 * If found, runs pipeline Stage 1 (dedup) and injects summary into conversation.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const input = JSON.parse(fs.readFileSync('/dev/stdin', 'utf8'));
const command = input.tool_input?.command || '';
const output = input.tool_result?.stdout || '';

// Only trigger on jq concat commands that produce raw-discovery.json
if (!command.includes('raw-discovery.json') || !command.includes('discovery/')) {
  process.exit(0);
}

const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();
const rawPath = path.join(projectDir, 'raw-discovery.json');

if (!fs.existsSync(rawPath)) {
  process.exit(0);
}

// Run dedup stage
try {
  const configPath = path.join(projectDir, 'swarm-config.json');
  const pipelinePath = path.join(projectDir, 'pipeline', 'pipeline.py');

  const result = execSync(
    `python3 "${pipelinePath}" --config "${configPath}" --stage dedup`,
    { cwd: projectDir, encoding: 'utf8', timeout: 60000 }
  );

  // Read dedup results for summary
  const dedupPath = path.join(projectDir, 'dedup.json');
  if (fs.existsSync(dedupPath)) {
    const dedup = JSON.parse(fs.readFileSync(dedupPath, 'utf8'));
    const raw = JSON.parse(fs.readFileSync(rawPath, 'utf8'));

    const summary = [
      `Pipeline Stage 1 (dedup) complete:`,
      `  Raw entries: ${raw.length}`,
      `  After dedup: ${dedup.length}`,
      `  Duplicates removed: ${raw.length - dedup.length}`,
      ``,
      `Ask the user for pruning thresholds (min score, min stars, active since) before running Stage 2.`,
    ].join('\n');

    const hookOutput = {
      hookSpecificOutput: {
        hookEventName: 'PostToolUse',
        additionalContext: summary,
      }
    };
    process.stdout.write(JSON.stringify(hookOutput));
  }
} catch (e) {
  // Don't block on pipeline failure — let the lead handle it
  console.error(`[post-concat] Pipeline dedup failed: ${e.message}`);
}

process.exit(0);
