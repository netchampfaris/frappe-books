import vue from '@vitejs/plugin-vue';
import fs from 'node:fs';
import path from 'node:path';
import { defineConfig, type Plugin } from 'vite';

const frontendRoot = __dirname;
const appRoot = path.resolve(frontendRoot, '..');
const sitesRoot = path.resolve(appRoot, '../../sites');

const backendPort = process.env.FRAPPE_WEB_SERVER_PORT ?? '8000';

/**
 * The site to fall back to when the browser's host names none, which is the
 * case for plain `localhost`. Hard-coding a site name here only works on the
 * bench that happens to use it, so the bench is asked instead.
 */
function resolveDefaultSite(): string | undefined {
  if (process.env.FRAPPE_SITE) {
    return process.env.FRAPPE_SITE;
  }

  const currentSite = path.join(sitesRoot, 'currentsite.txt');
  if (fs.existsSync(currentSite)) {
    const name = fs.readFileSync(currentSite, 'utf8').trim();
    if (name) {
      return name;
    }
  }

  // No default site on this bench, so look for the one that has this app.
  const installedOn = readSiteNames().filter((site) => {
    const config = path.join(sitesRoot, site, 'site_config.json');
    try {
      const installed = JSON.parse(fs.readFileSync(config, 'utf8'))
        .installed_apps as string[] | undefined;
      return installed?.includes('frappe_books') ?? false;
    } catch {
      return false;
    }
  });

  return installedOn.length === 1 ? installedOn[0] : undefined;
}

function readSiteNames(): string[] {
  try {
    return fs
      .readdirSync(sitesRoot, { withFileTypes: true })
      .filter((entry) => entry.isDirectory())
      .map((entry) => entry.name);
  } catch {
    return [];
  }
}

const defaultSite = resolveDefaultSite();

// The router mounts the app under /books/, which is also where the built
// www/books.html is served from. Dev has to agree with it or every navigation
// leaves the range of URLs Vite answers on.
const routerBase = '/books/';
const assetBase = '/assets/frappe_books/books/';

// Frappe picks the site from the Host header, so the browser's host is
// forwarded unchanged and `http://<site>:6969/` works for any bench site.
// Plain localhost names no site, so it is rewritten to FRAPPE_SITE.
const backend = {
  ws: true,
  target: `http://127.0.0.1:${backendPort}`,
  configure(proxy: {
    on(
      event: 'proxyReq',
      cb: (
        proxyReq: { setHeader(name: string, value: string): void },
        req: { headers: { host?: string } }
      ) => void
    ): void;
  }) {
    proxy.on('proxyReq', (proxyReq, req) => {
      if (defaultSite && namesNoSite(req.headers.host)) {
        proxyReq.setHeader('host', `${defaultSite}:${backendPort}`);
      }
    });
  },
};

function namesNoSite(host?: string): boolean {
  const name = host?.split(':')[0];
  return !name || name === 'localhost' || name === '127.0.0.1';
}

// Vite prints the localhost URL, which carries no site name. Say which site
// that falls back to, or how to choose one when it cannot be worked out.
function booksDevSite(): Plugin {
  return {
    name: 'books-dev-site',
    apply: 'serve',
    configureServer(server) {
      const printUrls = server.printUrls.bind(server);
      server.printUrls = () => {
        printUrls();
        if (defaultSite) {
          server.config.logger.info(
            `  \u279c  Site:    ${defaultSite} (override with FRAPPE_SITE)`
          );
        } else {
          server.config.logger.warn(
            '  \u279c  Site:    none resolved. Open the dev server on your ' +
              'site host, or start it with FRAPPE_SITE=<site> yarn dev'
          );
        }
      };
    },
  };
}

// The build output is copied to frappe_books/www/books.html, which Frappe
// renders through Jinja. Keeping the template tags out of index.html is what
// lets the same file be served as plain HTML by the dev server — raw `{{ }}`
// is a syntax error in the bootstrap script, which used to leave
// `window.frappe` undefined and stop the app on load.
function jinjaBootData(): Plugin {
  return {
    name: 'books-jinja-boot-data',
    apply: 'build',
    transformIndexHtml(html) {
      return html
        .replace(/<html[^>]*>/, '<html lang="{{ lang }}" dir="{{ layout_direction }}">')
        .replace(/<title>[^<]*<\/title>/, '<title>Frappe Books | {{ app_name }}</title>')
        .replace(
          '</body>',
          `  <script>
      window.csrf_token = '{{ frappe.session.csrf_token }}';
      window.frappe = window.frappe || {};
      frappe.csrf_token = window.csrf_token;
      frappe.boot = JSON.parse({{ boot }});
      frappe.boot.layout_direction = '{{ layout_direction }}';
      window.books_boot = {{ books_boot }};
    </script>
  </body>`
        );
    },
  };
}

export default defineConfig(async ({ command }) => {
  const { lucideIconsPlugin } =
    await import('frappe-ui/vite/lucideIconsPlugin');

  return {
    base: command === 'build' ? assetBase : routerBase,
    plugins: [lucideIconsPlugin(), vue(), jinjaBootData(), booksDevSite()],
    resolve: {
      alias: {
        vue: 'vue/dist/vue.esm-bundler.js',
        fyo: path.resolve(frontendRoot, 'fyo'),
        src: path.resolve(frontendRoot, 'src'),
        schemas: path.resolve(frontendRoot, 'schemas'),
        backend: path.resolve(frontendRoot, 'backend'),
        models: path.resolve(frontendRoot, 'models'),
        utils: path.resolve(frontendRoot, 'utils'),
        regional: path.resolve(frontendRoot, 'regional'),
        reports: path.resolve(frontendRoot, 'reports'),
        fixtures: path.resolve(frontendRoot, 'fixtures'),
        'frappe-ui-command-palette': path.resolve(
          frontendRoot,
          'node_modules/frappe-ui/experimental/CommandPalette/index.ts',
        ),
      },
    },
    optimizeDeps: {
      // frappe-ui's package.json `imports` map ("#utils/*" -> "./src/utils/*")
      // is extensionless, which esbuild cannot resolve while pre-bundling.
      // Serving frappe-ui from source lets Vite's own resolver handle it.
      exclude: ['frappe-ui'],
    },
    define: {
      'import.meta.env.VITE_ROUTER_BASE': JSON.stringify(routerBase),
    },
    build: {
      outDir: path.resolve(appRoot, 'frappe_books/public/books'),
      emptyOutDir: true,
      target: 'es2020',
      sourcemap: false,
    },
    server: {
      host: '0.0.0.0',
      port: 6969,
      proxy: {
        '^/(desk|app|login|api|assets|files|private)(?:[/?]|$)': backend,
      },
    },
  };
});
