#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

function die(message) {
  console.error(`[capsule-validate] ${message}`);
  process.exit(1);
}

function ok(message) {
  console.log(`[capsule-validate] ${message}`);
}

const targetDir = process.argv[2] || 'capsules/hiro';
const dirPath = path.resolve(process.cwd(), targetDir);

if (!fs.existsSync(dirPath)) {
  die(`Directory not found: ${dirPath}`);
}

const REQUIRED_LINES = [
  '///▙▖▙▖▞▞▙',
  '▛//▞▞',
  '▛///▞ PROMPT TITLE ▞▞//▟',
  '//▞ SECTION::',
  '▞▞ Nest ::',
  '▚▚ sub-nest:',
  ':: ∎',
  '〘・.°𝚫〙'
];

function validateFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const missing = REQUIRED_LINES.filter(line => !content.includes(line));
  if (missing.length > 0) {
    die(`Validation failed for ${filePath}. Missing: ${missing.join(', ')}`);
  } else {
    ok(`Validated ${filePath}`);
  }
}

const entries = fs.readdirSync(dirPath);
const mdFiles = entries.filter(f => f.endsWith('.md'));

if (mdFiles.length === 0) {
  die(`No .md files found in ${dirPath}`);
}

mdFiles.forEach(f => validateFile(path.join(dirPath, f)));

ok('All capsules valid.');
