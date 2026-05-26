import { createRequire } from 'node:module';
import { buildScriptPaths } from './script-paths.js';
import { CLI_NAME, PACKAGE_NAME, SKILL_ID } from './constants.js';
import { findWorkspaceRoot } from './core/resolver.js';
import { detectOS, getOSLabel } from './os.js';
import { getScopesForRuntime } from './core/scope.js';
import {
  resolveInstallLocation,
  RUNTIME_IDS,
  RUNTIMES,
} from './runtime/index.js';

const require = createRequire(import.meta.url);
const pkg = require('../package.json');

export class CliError extends Error {
  constructor(code, message) {
    super(message);
    this.name = 'CliError';
    this.code = code;
  }
}

export function argvHasJsonFlag(argv = process.argv) {
  return argv.includes('--json');
}

export function getJsonFlag(command) {
  return Boolean(command.parent?.opts()?.json ?? command.opts()?.json);
}

export function assertNonInteractive(json, yes, commandName) {
  if (json && !yes) {
    throw new CliError(
      'NON_INTERACTIVE_REQUIRED',
      `--json requires --yes for ${commandName}. Example: ${CLI_NAME} ${commandName} -r claude -y --json`,
    );
  }
}

export function writeJson(payload) {
  process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
}

export function writeJsonError(error) {
  process.stderr.write(`${JSON.stringify({
    ok: false,
    error: {
      code: error.code ?? 'UNKNOWN_ERROR',
      message: error.message,
    },
  }, null, 2)}\n`);
}

export function serializeInstallResult(item) {
  return {
    runtimeId: item.runtimeId,
    scope: item.scope,
    installDir: item.installDir,
    strategy: item.strategy,
    skill: {
      id: item.manifest.id,
      version: item.manifest.version,
    },
  };
}

export function serializeUpdateResult(item) {
  return {
    ...serializeInstallResult(item),
    previousVersion: item.previousVersion,
    nextVersion: item.nextVersion,
  };
}

export function serializeUninstallResult(item) {
  return {
    runtimeId: item.runtimeId,
    scope: item.scope,
    installDir: item.installDir,
    removed: item.removed,
  };
}

export function serializeInstallLocation(location) {
  return {
    scope: location.scope,
    installDir: location.installDir,
    strategy: location.strategy,
    candidates: location.candidates,
    scripts: buildScriptPaths(location.installDir),
  };
}

export function serializeStatus(item) {
  return {
    runtimeId: item.runtimeId,
    label: item.label,
    scope: item.scope,
    installed: item.installed,
    version: item.version,
    installDir: item.installDir,
    strategy: item.strategy,
    candidates: item.candidates,
    scripts: buildScriptPaths(item.installDir),
  };
}

export function buildInfoPayload(context = {}) {
  const cwd = context.cwd || process.cwd();
  const workspaceRoot = findWorkspaceRoot(cwd);
  return {
    ok: true,
    command: 'info',
    package: {
      name: PACKAGE_NAME,
      version: pkg.version,
      cli: CLI_NAME,
      skillId: SKILL_ID,
    },
    environment: {
      os: getOSLabel(detectOS()),
      workspaceRoot,
      cwd,
    },
    runtimes: RUNTIME_IDS.map((id) => ({
      id,
      label: RUNTIMES[id].label,
      scopes: getScopesForRuntime(id).map((scope) => {
        const location = resolveInstallLocation(id, scope, context);
        return serializeInstallLocation({ ...location, scope });
      }),
    })),
  };
}
