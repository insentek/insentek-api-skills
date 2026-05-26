import fs from 'node:fs/promises';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { ASSETS_DIR, SKILL_ID } from '../constants.js';
import { readBundledManifest, validateManifest } from '../core/manifest.js';
import { resolveInstallLocation, RUNTIMES } from '../runtime/index.js';
import { getInstallStatus } from './status.js';
import { formatPath, pathExists, printInfo, printSuccess, printWarn } from '../utils.js';
import {
  getScopesForRuntime,
  normalizeScope,
  validateScopeForRuntime,
} from '../core/scope.js';

function findPythonCommand() {
  const candidates = process.platform === 'win32'
    ? ['python', 'py', 'python3']
    : ['python3', 'python'];

  for (const candidate of candidates) {
    const result = spawnSync(candidate, ['--version'], {
      encoding: 'utf8',
      stdio: 'pipe',
      shell: process.platform === 'win32',
    });
    if (result.status === 0) {
      return { command: candidate, version: result.stdout.trim() || result.stderr.trim() };
    }
  }
  return null;
}

function checkLineEndings(content) {
  if (content.includes('\r\n')) {
    return { ok: true, message: 'CRLF detected (Windows)' };
  }
  if (content.includes('\n')) {
    return { ok: true, message: 'LF detected (Unix)' };
  }
  return { ok: false, message: 'No line endings detected' };
}

async function checkBundledAssets() {
  const manifest = await readBundledManifest();
  await validateManifest(manifest);
  const skillPath = path.join(ASSETS_DIR, 'SKILL.md');
  if (!(await pathExists(skillPath))) {
    throw new Error('Bundled SKILL.md not found');
  }
  return manifest;
}

async function checkRuntimeInstall(runtimeId, scope, context) {
  const runtime = RUNTIMES[runtimeId];
  const location = resolveInstallLocation(runtimeId, scope, context);
  const status = await getInstallStatus({ runtimeId, scope, context });
  const checks = [];

  checks.push({
    name: `${runtime.label} install directory`,
    ok: status.installed,
    message: status.installed
      ? `Installed at ${formatPath(status.installDir)}`
      : `Not installed (expected: ${formatPath(location.installDir)})`,
  });

  if (status.installed) {
    checks.push({
      name: `${runtime.label} manifest`,
      ok: Boolean(status.manifest?.id === SKILL_ID),
      message: status.manifest
        ? `skill.json id=${status.manifest.id}, version=${status.manifest.version}`
        : 'skill.json missing',
    });

    const skillContent = await fs.readFile(path.join(status.installDir, 'SKILL.md'), 'utf8');
    checks.push({
      name: `${runtime.label} SKILL.md`,
      ok: skillContent.includes('name: insentek-openapi'),
      message: 'SKILL.md present and id matches',
    });

    checks.push({
      name: `${runtime.label} line endings`,
      ...checkLineEndings(skillContent),
    });

    const cliScript = path.join(status.installDir, 'scripts', 'insentek_cli.py');
    checks.push({
      name: `${runtime.label} scripts`,
      ok: await pathExists(cliScript),
      message: await pathExists(cliScript) ? 'scripts/insentek_cli.py found' : 'scripts missing',
    });
  }

  return checks;
}

export async function runDoctor({ runtimeIds, scope, context }) {
  const checks = [];
  let allPassed = true;

  printInfo('Running doctor checks...');

  try {
    const bundled = await checkBundledAssets();
    checks.push({
      name: 'Bundled manifest',
      ok: true,
      message: `${bundled.id} v${bundled.version}`,
    });
  } catch (error) {
    allPassed = false;
    checks.push({ name: 'Bundled manifest', ok: false, message: error.message });
  }

  for (const runtimeId of runtimeIds) {
    const allowed = getScopesForRuntime(runtimeId);
    checks.push({
      name: `${RUNTIMES[runtimeId].label} scopes`,
      ok: allowed.includes(normalizeScope(scope)),
      message: allowed.join(', '),
    });
  }

  const python = findPythonCommand();
  checks.push({
    name: 'Python',
    ok: Boolean(python),
    message: python ? `${python.command}: ${python.version}` : 'Python 3.8+ not found in PATH',
  });

  const git = spawnSync(process.platform === 'win32' ? 'where' : 'which', ['git'], { stdio: 'pipe', shell: process.platform === 'win32' });
  checks.push({
    name: 'Git',
    ok: git.status === 0,
    message: git.status === 0 ? 'git available' : 'git not found (optional)',
  });

  for (const runtimeId of runtimeIds) {
    validateScopeForRuntime(runtimeId, scope);
    const runtimeChecks = await checkRuntimeInstall(runtimeId, scope, context);
    checks.push(...runtimeChecks);
  }

  console.log('\nDoctor report:\n');
  for (const check of checks) {
    const icon = check.ok ? '✔' : '✖';
    console.log(`  ${icon} ${check.name}: ${check.message}`);
    if (!check.ok) {
      allPassed = false;
    }
  }

  console.log('');
  if (allPassed) {
    printSuccess('All doctor checks passed');
  } else {
    printWarn('Some doctor checks failed');
  }

  return { allPassed, checks };
}
