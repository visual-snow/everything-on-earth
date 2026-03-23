#!/usr/bin/env node

/**
 * Hook: pre-teamcreate.js
 * Trigger: PreToolUse on TeamCreate
 * Purpose: Gate — validates swarm-config.json and firecrawl setup before team creation.
 *
 * Exit behavior:
 *   - stdout JSON with { decision: "block", reason } → blocks TeamCreate
 *   - stdout JSON with { decision: "allow" } → allows TeamCreate
 *   - exit 0 with no JSON → allows (passthrough for non-eoe teams)
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const input = JSON.parse(fs.readFileSync('/dev/stdin', 'utf8'));
const teamName = input.tool_input?.name || '';

// Only gate our teams
if (!teamName.startsWith('eoe-')) {
  process.exit(0);
}

const errors = [];
const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();
const configPath = path.join(projectDir, 'swarm-config.json');

// 1. Config file exists
if (!fs.existsSync(configPath)) {
  errors.push('swarm-config.json not found in project directory');
} else {
  try {
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

    // 2. Minimum sub-domains
    if (!config.sub_domains || config.sub_domains.length < 3) {
      errors.push(`Need >= 3 sub-domains, found ${config.sub_domains?.length || 0}`);
    }

    // 3. Seed queries per sub-domain
    if (config.sub_domains) {
      for (const sd of config.sub_domains) {
        const qCount = sd.seed_queries?.length || 0;
        if (qCount < 8) {
          errors.push(`Sub-domain "${sd.id}" has ${qCount} seed queries (need 8-10)`);
        }
      }
    }

    // 4. Schema version
    if (config.schema_version !== '2.0.0') {
      errors.push(`Unsupported schema_version: ${config.schema_version} (expected 2.0.0)`);
    }
  } catch (e) {
    errors.push(`Invalid JSON in swarm-config.json: ${e.message}`);
  }
}

// 5. Firecrawl CLI exists
try {
  execSync('which firecrawl', { stdio: 'pipe' });
} catch {
  errors.push('firecrawl CLI not found in PATH. Install: npm install -g firecrawl');
}

// 6. FIRECRAWL_API_KEY is set
if (!process.env.FIRECRAWL_API_KEY) {
  errors.push('FIRECRAWL_API_KEY environment variable not set');
}

if (errors.length > 0) {
  const result = {
    decision: 'block',
    reason: `Pre-TeamCreate validation failed:\n${errors.map(e => `  - ${e}`).join('\n')}`
  };
  process.stdout.write(JSON.stringify(result));
} else {
  const result = { decision: 'allow' };
  process.stdout.write(JSON.stringify(result));
}
