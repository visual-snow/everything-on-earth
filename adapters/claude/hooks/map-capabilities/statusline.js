#!/usr/bin/env node

/**
 * Hook: statusline.js
 * Trigger: Notification
 * Purpose: Real-time progress display for map-capabilities runs.
 *
 * Output format:
 *   map-capabilities | {catalog_name} | {done}/{total} | {pct}%
 */

const fs = require('fs');
const path = require('path');

const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();
const configPath = path.join(projectDir, 'map-capabilities-config.json');

// Only show status if a run is in progress
if (!fs.existsSync(configPath)) {
  process.exit(0);
}

try {
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  const catalogName = config.catalog_name || 'unknown';
  const outputDir = config.output_dir;

  // Use cached total from config (written once at run start) to avoid re-reading catalog
  const total = typeof config.total_entries === 'number' ? config.total_entries : 0;

  if (total === 0) {
    process.exit(0);
  }

  // Read progress
  const progressPath = path.join(outputDir, 'wave-progress.json');
  let done = 0;
  let failed = 0;
  let inProgress = 0;

  if (fs.existsSync(progressPath)) {
    const progress = JSON.parse(fs.readFileSync(progressPath, 'utf8'));
    done = Array.isArray(progress.completed) ? progress.completed.length : 0;
    failed = progress.failed ? Object.keys(progress.failed).length : 0;
    inProgress = Array.isArray(progress.in_progress) ? progress.in_progress.length : 0;
  }

  // Silent exit once run is fully complete — avoids work between runs
  if (done >= total && failed === 0) {
    process.exit(0);
  }

  const pct = Math.round((done / total) * 100);

  let status = `map-capabilities | ${catalogName} | ${done}/${total} | ${pct}%`;
  if (inProgress > 0) {
    status += ` | ${inProgress} in flight`;
  }
  if (failed > 0) {
    status += ` | ${failed} to retry`;
  }

  const hookOutput = {
    hookSpecificOutput: {
      hookEventName: 'Notification',
      statusMessage: status,
    }
  };
  process.stdout.write(JSON.stringify(hookOutput));
} catch {
  // Silently exit on any error — status is non-critical
  process.exit(0);
}
