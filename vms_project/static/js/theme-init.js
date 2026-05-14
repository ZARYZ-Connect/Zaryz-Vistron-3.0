(function () {
  try {
    // If the page explicitly requests to stay dark (e.g. Registration/Landing)
    if (window.VMS_FORCE_DARK) return;

    const key = window.VMS_THEME_KEY || 'zaryz-theme';
    var saved = localStorage.getItem(key);
    if (saved === 'light') {
      document.documentElement.setAttribute('data-theme', 'light');
    }
  } catch (e) {}
})();
