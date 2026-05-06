// theme.js — load this in <head> to prevent FOUC
(function() {
  const key = window.VMS_THEME_KEY || 'zaryz-theme';
  const saved = localStorage.getItem(key);

  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const theme = saved || (prefersDark ? 'dark' : 'light');
  document.documentElement.setAttribute('data-theme', theme);
  document.documentElement.classList.add('no-transition');
  
  if (document.readyState === 'loading') {
    document.addEventListener("DOMContentLoaded", () => {
      setTimeout(() => document.documentElement.classList.remove('no-transition'), 100);
    });
  } else {
    setTimeout(() => document.documentElement.classList.remove('no-transition'), 100);
  }
})();

function toggleTheme() {
  const html = document.documentElement;
  const currentTheme = html.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', newTheme);
  
  const key = window.VMS_THEME_KEY || 'zaryz-theme';
  localStorage.setItem(key, newTheme);
  
  updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
  const sunIcon = document.getElementById('theme-icon-sun');
  const moonIcon = document.getElementById('theme-icon-moon');
  if (sunIcon && moonIcon) {
    if (theme === 'light') {
      sunIcon.style.display = 'block';
      moonIcon.style.display = 'none';
    } else {
      sunIcon.style.display = 'none';
      moonIcon.style.display = 'block';
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
  updateThemeIcon(currentTheme);
});
