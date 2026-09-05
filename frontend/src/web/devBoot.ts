/**
 * Bootstrap values for the Vite dev server.
 *
 * In production `www/books.html` injects `frappe.boot`, the CSRF token and
 * `books_boot` through Jinja. The dev server serves `index.html` without a
 * Jinja pass, so the same values are read from the site over the API instead.
 */
export async function loadDevBoot(): Promise<void> {
  if (window.frappe?.boot) {
    return;
  }

  const response = await fetch(
    '/api/method/frappe_books.ui_api.get_boot',
    { credentials: 'same-origin', headers: { Accept: 'application/json' } }
  );

  if (response.status === 401 || response.status === 403) {
    window.location.href = `/login?redirect-to=${encodeURIComponent('/books')}`;
    return;
  }

  if (response.status === 404) {
    throw new Error(
      'The Frappe site did not recognise this request. Open the dev server on ' +
        'your site host, such as http://<site>:6969/, or start it with ' +
        'FRAPPE_SITE=<site> yarn dev.'
    );
  }

  if (!response.ok) {
    throw new Error(
      `Could not load boot data from the Frappe site (${response.status}). ` +
        'Check that bench is running.'
    );
  }

  const { message } = (await response.json()) as {
    message: {
      boot: Window['frappe']['boot'];
      books_boot: Window['books_boot'];
      csrf_token?: string;
    };
  };

  window.frappe = window.frappe || {};
  window.frappe.boot = message.boot;
  window.frappe.csrf_token = message.csrf_token;
  window.csrf_token = message.csrf_token;
  window.books_boot = message.books_boot;
}
