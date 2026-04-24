import { copyFile, mkdir } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const currentDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = resolve(currentDir, '..');
const source = resolve(projectRoot, 'node_modules', 'pdfjs-dist', 'build', 'pdf.worker.min.mjs');
const target = resolve(projectRoot, 'public', 'pdf.worker.min.mjs');

await mkdir(dirname(target), { recursive: true });
await copyFile(source, target);

console.log(`Synced pdf.js worker to ${target}`);
