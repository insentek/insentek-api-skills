#!/usr/bin/env node

import { runCli } from '../lib/cli.js';

runCli(process.argv).catch((error) => {
  console.error(`\n✖ ${error.message}`);
  process.exit(1);
});
