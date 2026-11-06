import { useColorScheme } from 'frappe-ui';

export function setDarkMode(darkMode: boolean): void {
  // `useColorScheme()` initializes frappe-ui's shared state on first call,
  // restoring whatever was left in `localStorage['theme']`. SystemSettings.darkMode
  // is the app's source of truth, so we set it right after and let it win.
  const { setColorScheme } = useColorScheme();
  setColorScheme(darkMode ? 'dark' : 'light');

  if (darkMode) {
    document.documentElement.classList.add(
      'dark',
      'custom-scroll',
      'custom-scroll-thumb1'
    );
    return;
  }
  document.documentElement.classList.remove('dark');
}
