import { spawn } from 'node:child_process';

const command = process.platform === 'win32' ? 'cloudflared.exe' : 'cloudflared';
const tunnel = spawn(command, ['tunnel', '--url', 'http://localhost:8000'], { stdio: ['ignore', 'pipe', 'pipe'] });
let output = '';
let started = false;
let expo;
let timeout;

function stop(code = 0) {
  clearTimeout(timeout);
  tunnel.kill();
  expo?.kill();
  process.exitCode = code;
}

function onTunnelData(chunk) {
  const text = chunk.toString();
  process.stdout.write(text);
  output = (output + text).slice(-12000);
  const url = output.match(/https:\/\/[a-z0-9-]+\.trycloudflare\.com/i)?.[0];
  if (!url || started) return;
  started = true;
  clearTimeout(timeout);
  console.log(`\nBackend API: ${url}`);
  const npm = process.platform === 'win32' ? 'npm.cmd' : 'npm';
  expo = spawn(npm, ['start', '--prefix', 'mobile', '--', '--tunnel', '--clear'], {
    stdio: 'inherit',
    shell: process.platform === 'win32',
    env: { ...process.env, EXPO_PUBLIC_API_URL: url, EXPO_PUBLIC_API_LOCKED: 'true', EXPO_PUBLIC_API_AUTO: 'true' },
  });
  expo.on('exit', code => stop(code ?? 1));
}

tunnel.stdout.on('data', chunk => onTunnelData(chunk, 'stdout'));
tunnel.stderr.on('data', chunk => onTunnelData(chunk, 'stderr'));
tunnel.on('error', error => { console.error(`Could not start cloudflared: ${error.message}`); stop(1); });
tunnel.on('exit', code => { if (!started) console.error(`cloudflared exited before producing a tunnel URL (exit ${code}).`); stop(code ?? 1); });
process.on('SIGINT', () => stop(0));
process.on('SIGTERM', () => stop(0));
timeout = setTimeout(() => { if (!started) { console.error('Timed out waiting for Cloudflare Quick Tunnel URL.'); stop(1); } }, 120000);
