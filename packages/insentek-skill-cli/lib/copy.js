import fs from 'node:fs/promises';
import path from 'node:path';
import { ASSET_ENTRIES, ASSETS_DIR } from './constants.js';
import { ensureDir, pathExists, removeDir } from './utils.js';

const COPY_IGNORE_DIRS = new Set(['__pycache__']);

function shouldCopyAssetEntry(name) {
  return !COPY_IGNORE_DIRS.has(name);
}

export async function copyDirectoryFiltered(sourcePath, targetPath) {
  await fs.cp(sourcePath, targetPath, {
    recursive: true,
    force: true,
    filter: (src) => shouldCopyAssetEntry(path.basename(src)),
  });
}

async function copyEntry(sourceRoot, entryName, targetRoot) {
  const sourcePath = path.join(sourceRoot, entryName);
  const targetPath = path.join(targetRoot, entryName);

  if (!(await pathExists(sourcePath))) {
    throw new Error(`Missing bundled asset: ${entryName}`);
  }

  const stat = await fs.stat(sourcePath);
  if (stat.isDirectory()) {
    await copyDirectoryFiltered(sourcePath, targetPath);
  } else {
    await ensureDir(path.dirname(targetPath));
    await fs.copyFile(sourcePath, targetPath);
  }
}

export async function copySkillAssets(targetDir, { force = false } = {}) {
  if (!(await pathExists(ASSETS_DIR))) {
    throw new Error(
      'Skill assets not found. Run "npm run sync-assets" inside packages/insentek-skill-cli.',
    );
  }

  if (await pathExists(targetDir)) {
    if (!force) {
      throw new Error(`Target already exists: ${targetDir}. Use --force to overwrite.`);
    }
    await removeDir(targetDir);
  }

  await ensureDir(targetDir);

  for (const entry of ASSET_ENTRIES) {
    await copyEntry(ASSETS_DIR, entry, targetDir);
  }
}
