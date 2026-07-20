/**
 * Cross-platform Git Hooks Installer for LEXIS Platform
 * Configures git to use the custom .githooks directory for security secret scanning.
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

function installHooks() {
  console.log('[LEXIS Security] Installing pre-commit secret scanning hook...');

  const rootDir = path.resolve(__dirname, '..');
  const hooksDir = path.join(rootDir, '.githooks');

  if (!fs.existsSync(hooksDir)) {
    console.error(`[ERROR] Hooks directory missing at ${hooksDir}`);
    process.exit(1);
  }

  try {
    // Set git core.hooksPath to .githooks
    execSync('git config core.hooksPath .githooks', { cwd: rootDir, stdio: 'inherit' });
    console.log('[LEXIS Security] SUCCESS: git core.hooksPath set to ".githooks".');
    console.log('[LEXIS Security] Secret scanning active for all future commits.');
  } catch (err) {
    console.error('[LEXIS Security] ERROR: Failed to configure git hooks path:', err.message);
    process.exit(1);
  }
}

installHooks();
