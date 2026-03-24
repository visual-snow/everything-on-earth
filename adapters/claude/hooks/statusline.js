#!/usr/bin/env node

/**
 * Hook: statusline.js
 * Trigger: Notification
 * Purpose: Real-time progress display for massive-crawl runs.
 *
 * Output format:
 *   massive-crawl | {topic} | tasks: {done}/{total} | repos: {count} | {pct}%
 */

const fs = require('fs');
const path = require('path');

const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();
const configPath = path.join(projectDir, 'swarm-config.json');

// Only show status if a run is in progress
if (!fs.existsSync(configPath)) {
  process.exit(0);
}

try {
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  const topic = config.topic || 'unknown';
  const totalDomains = (config.sub_domains?.length || 0) + 1; // +1 for awesome-lists

  // Count completed discovery files
  const discoveryDir = path.join(projectDir, 'discovery');
  let completedFiles = 0;
  let totalRepos = 0;

  if (fs.existsSync(discoveryDir)) {
    const files = fs.readdirSync(discoveryDir).filter(f => f.endsWith('.json'));
    completedFiles = files.length;

    for (const file of files) {
      try {
        const data = JSON.parse(fs.readFileSync(path.join(discoveryDir, file), 'utf8'));
        totalRepos += Array.isArray(data) ? data.length : 0;
      } catch {
        // skip malformed files
      }
    }
  }

  const pct = totalDomains > 0 ? Math.round((completedFiles / totalDomains) * 100) : 0;
  const status = `massive-crawl | ${topic} | tasks: ${completedFiles}/${totalDomains} | repos: ${totalRepos} | ${pct}%`;

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
