const http = require('http');
const fs = require('fs');
const path = require('path');

const root = path.resolve('C:/Users/11193/Desktop/www');
const PORT = 8080;

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.gif': 'image/gif',
  '.ico': 'image/x-icon',
  '.woff2': 'font/woff2',
  '.woff': 'font/woff',
  '.ttf': 'font/ttf',
};

const server = http.createServer((req, res) => {
  // Strip query string and leading/trailing slashes
  let urlPath = req.url.split('?')[0];
  urlPath = '/' + urlPath.replace(/^\/|\/$/g, '');
  if (urlPath === '/') urlPath = '/index.html';

  const filePath = path.join(root, urlPath);

  // Security: prevent path traversal
  if (!filePath.startsWith(root)) {
    res.writeHead(403);
    res.end('Forbidden');
    return;
  }

  fs.stat(filePath, (err, stat) => {
    if (err || !stat || !stat.isFile()) {
      res.writeHead(404);
      res.end('Not found: ' + urlPath);
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    const ct = MIME[ext] || 'application/octet-stream';

    res.writeHead(200, {
      'Content-Type': ct,
      'Cache-Control': 'no-cache',
    });

    fs.createReadStream(filePath).pipe(res);
  });
});

server.listen(PORT, () => {
  console.log('Server running at http://localhost:' + PORT + '/');
});
