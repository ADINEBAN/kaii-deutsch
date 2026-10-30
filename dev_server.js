#!/usr/bin/env node
/**
 * WordFeather Local Development Server & Safe TTS Proxy (Node.js)
 * =============================================================
 * Zero-dependency alternative to dev_server.py.
 * Serves static assets and safely proxies /api/tts to Thorsten-Voice Kokoro TTS.
 */

const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const url = require('url');

const REPO_ROOT = path.resolve(__dirname);
const PORT = parseInt(process.env.PORT || '8080', 10);
const HOST = process.env.HOST || '127.0.0.1';
const TTS_BACKEND = process.env.TTS_BACKEND || 'http://127.0.0.1:8000';

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.wav': 'audio/wav',
  '.mp3': 'audio/mpeg',
  '.txt': 'text/plain; charset=utf-8',
  '.xml': 'application/xml; charset=utf-8'
};

function setCorsHeaders(res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Accept');
}

function logDiag(msg) {
  const time = new Date().toTimeString().split(' ')[0];
  console.log(`[${time}] [TTS Proxy] ${msg}`);
}

function proxyHealth(req, res) {
  const target = new URL('/health', TTS_BACKEND);
  logDiag(`GET /api/tts/health -> Forwarding to ${target}`);
  const clientReq = http.request(target, { method: 'GET', timeout: 5000 }, (backendRes) => {
    setCorsHeaders(res);
    logDiag(`Health response: status=${backendRes.statusCode}, content-type=${backendRes.headers['content-type']}`);
    res.writeHead(backendRes.statusCode, backendRes.headers);
    backendRes.pipe(res);
  });

  clientReq.on('timeout', () => {
    clientReq.destroy();
    setCorsHeaders(res);
    logDiag('Health check timed out');
    res.writeHead(504, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'error', message: 'TTS health check timed out' }));
  });

  clientReq.on('error', (err) => {
    setCorsHeaders(res);
    logDiag(`Health connection error: ${err.message}`);
    res.writeHead(503, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'error', message: `Cannot connect to TTS backend at ${target}: ${err.message}` }));
  });

  clientReq.end();
}

function proxyTts(req, res) {
  let body = '';
  req.on('data', chunk => {
    body += chunk;
    if (body.length > 65536) {
      req.destroy();
      setCorsHeaders(res);
      logDiag('POST /api/tts - Payload too large');
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Payload too large (max 64KB)' }));
    }
  });

  req.on('end', () => {
    let payload;
    try {
      payload = JSON.parse(body);
    } catch (e) {
      setCorsHeaders(res);
      logDiag(`POST /api/tts - Invalid JSON body: ${e.message}`);
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Invalid JSON body' }));
      return;
    }

    if (!payload.text || typeof payload.text !== 'string' || !payload.text.trim()) {
      setCorsHeaders(res);
      logDiag('POST /api/tts - Missing or empty text field');
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Missing or empty text field' }));
      return;
    }

    const speed = typeof payload.speed === 'number' ? Math.max(0.2, Math.min(3.0, payload.speed)) : 0.9;
    const lang = String(payload.lang || 'de-DE').trim().toLowerCase();
    const preview = payload.text.trim().substring(0, 40) + (payload.text.trim().length > 40 ? '...' : '');

    if (lang.startsWith('en')) {
      const gUrl = `https://translate.google.com/translate_tts?ie=UTF-8&tl=en&client=tw-ob&q=${encodeURIComponent(payload.text.trim())}`;
      logDiag(`POST /api/tts [English] -> Fetching: "${preview}"`);
      const gReq = https.get(gUrl, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        },
        timeout: 8000
      }, (gRes) => {
        setCorsHeaders(res);
        res.writeHead(gRes.statusCode, {
          'Content-Type': gRes.headers['content-type'] || 'audio/mpeg',
          'Cache-Control': 'public, max-age=86400'
        });
        gRes.pipe(res);
      });
      gReq.on('error', (err) => {
        setCorsHeaders(res);
        logDiag(`POST /api/tts [English] error: ${err.message}`);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: err.message }));
      });
      return;
    }

    const sanitized = JSON.stringify({
      text: payload.text.trim(),
      speed: speed
    });

    const target = new URL('/tts', TTS_BACKEND);
    logDiag(`POST /api/tts [German] -> Forwarding to ${target} (text="${preview}", speed=${speed})`);
    const clientReq = http.request(target, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(sanitized),
        'Accept': 'audio/wav, audio/*;q=0.9, */*;q=0.8'
      },
      timeout: 15000
    }, (backendRes) => {
      setCorsHeaders(res);
      logDiag(`TTS response: status=${backendRes.statusCode}, content-type=${backendRes.headers['content-type']}`);
      res.writeHead(backendRes.statusCode, {
        ...backendRes.headers,
        'Cache-Control': 'public, max-age=86400'
      });
      backendRes.pipe(res);
    });

    clientReq.on('timeout', () => {
      clientReq.destroy();
      setCorsHeaders(res);
      logDiag('TTS generation timed out');
      res.writeHead(504, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ status: 'error', message: 'TTS generation timed out' }));
    });

    clientReq.on('error', (err) => {
      setCorsHeaders(res);
      logDiag(`TTS backend error: ${err.message}`);
      res.writeHead(503, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ status: 'error', message: `TTS backend error: ${err.message}` }));
    });

    clientReq.write(sanitized);
    clientReq.end();
  });
}

function serveStatic(req, res, pathname) {
  let safePath = path.normalize(pathname).replace(/^(\.\.[\/\\])+/, '');
  if (safePath === '/' || safePath === '\\') safePath = '/index.html';

  let filePath = path.join(REPO_ROOT, safePath);
  if (!filePath.startsWith(REPO_ROOT)) {
    res.writeHead(403, { 'Content-Type': 'text/plain' });
    res.end('Forbidden');
    return;
  }

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      // Try appending .html
      if (!path.extname(filePath)) {
        const withHtml = filePath + '.html';
        if (fs.existsSync(withHtml)) {
          filePath = withHtml;
        } else {
          res.writeHead(404, { 'Content-Type': 'text/plain' });
          res.end('File not found');
          return;
        }
      } else {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('File not found');
        return;
      }
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';

    setCorsHeaders(res);
    res.writeHead(200, { 'Content-Type': contentType });
    fs.createReadStream(filePath).pipe(res);
  });
}

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url);
  const pathname = parsedUrl.pathname;

  if (req.method === 'OPTIONS') {
    setCorsHeaders(res);
    res.writeHead(204);
    res.end();
    return;
  }

  if (pathname === '/api/tts/health' && req.method === 'GET') {
    proxyHealth(req, res);
    return;
  }

  if (pathname === '/api/tts' && req.method === 'POST') {
    proxyTts(req, res);
    return;
  }

  serveStatic(req, res, pathname);
});

const PID_FILE = path.join(REPO_ROOT, 'dev_server.pid');

function cleanupPid() {
  try {
    if (fs.existsSync(PID_FILE)) fs.unlinkSync(PID_FILE);
  } catch (e) {}
}

process.on('exit', cleanupPid);
process.on('SIGINT', () => { cleanupPid(); process.exit(0); });
process.on('SIGTERM', () => { cleanupPid(); process.exit(0); });

server.listen(PORT, HOST, () => {
  try {
    fs.writeFileSync(PID_FILE, String(process.pid), 'utf8');
  } catch (e) {}
  console.log('='.repeat(65));
  console.log('  🪶 WordFeather Local Development Server (Node.js)');
  console.log('='.repeat(65));
  console.log(`  Web Root:    ${REPO_ROOT}`);
  console.log(`  Local URL:   http://${HOST}:${PORT}/`);
  console.log(`  TTS Backend: ${TTS_BACKEND}`);
  console.log('='.repeat(65));
});
