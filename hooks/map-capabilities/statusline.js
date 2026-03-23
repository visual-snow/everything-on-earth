#!/usr/bin/env node

/**
 * Hook: statusline.js
 * Trigger: Notification
 * Purpose: Real-time progress display for map-capabilities runs.
 *
 * Output format:
 *   map-capabilities | {catalog_name} | {done}/{total} | {pct}%
 *
 * Mutual exclusion: This hook and massive-crawl/statusline.js both register on
 * Notification without matchers. Each checks for its own config file
 * (map-capabilities-config.json vs swarm-config.json) and exits 0 if absent.
 * No runtime collision is possible — only one config exists at a time.
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
  const catalogPath = config.catalog;

  // Read catalog for total count
  if (!fs.existsSync(catalogPath)) {
    process.exit(0);
  }
  const catalog = JSON.parse(fs.readFileSync(catalogPath, 'utf8'));
  const total = Array.isArray(catalog) ? catalog.length : 0;

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
