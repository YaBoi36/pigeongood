// Simple Node.js server to replace Python backend
const { spawn } = require('child_process');
const path = require('path');

// Start TypeScript server using ts-node
const serverPath = path.join(__dirname, 'server.ts');
const server = spawn('npx', ['ts-node', serverPath], {
  cwd: __dirname,
  stdio: 'inherit',
  env: { ...process.env, NODE_ENV: 'production' }
});

server.on('error', (error) => {
  console.error('Failed to start TypeScript server:', error);
  process.exit(1);
});

server.on('close', (code) => {
  console.log(`TypeScript server exited with code ${code}`);
  process.exit(code);
});

// Handle graceful shutdown
process.on('SIGTERM', () => {
  server.kill('SIGTERM');
});

process.on('SIGINT', () => {
  server.kill('SIGINT');
});