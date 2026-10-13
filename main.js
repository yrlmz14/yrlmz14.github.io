// Theme management
(function initTheme() {
  const savedTheme = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const currentTheme = savedTheme || (prefersDark ? 'dark' : 'light');
  document.documentElement.setAttribute('data-theme', currentTheme);
})();

document.addEventListener('DOMContentLoaded', () => {
  // Theme Toggle Button
  const toggleBtn = document.getElementById('theme-toggle');
  if (toggleBtn) {
    function updateIcon() {
      const current = document.documentElement.getAttribute('data-theme');
      toggleBtn.textContent = current === 'dark' ? '☀️' : '🌙';
      toggleBtn.setAttribute('title', `Switch to ${current === 'dark' ? 'light' : 'dark'} mode`);
    }
    updateIcon();

    toggleBtn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      updateIcon();
    });
  }

  // 1-Click Copy Code Button
  document.querySelectorAll('pre').forEach((pre) => {
    const code = pre.querySelector('code');
    if (!code) return;

    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-btn';
    copyBtn.textContent = 'Copy';
    pre.appendChild(copyBtn);

    copyBtn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(code.innerText);
        copyBtn.textContent = '✓ Copied';
        copyBtn.classList.add('copied');
        setTimeout(() => {
          copyBtn.textContent = 'Copy';
          copyBtn.classList.remove('copied');
        }, 2000);
      } catch (err) {
        copyBtn.textContent = 'Failed';
      }
    });
  });

  // Reading Progress Bar
  const progressBar = document.getElementById('reading-progress');
  if (progressBar) {
    window.addEventListener('scroll', () => {
      const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
      if (totalHeight > 0) {
        const progress = (window.scrollY / totalHeight) * 100;
        progressBar.style.width = `${Math.min(100, Math.max(0, progress))}%`;
      }
    });
  }

  // Instant Post Search
  const searchInput = document.getElementById('search-input');
  if (searchInput) {
    const postCards = document.querySelectorAll('.post-card');
    searchInput.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase().trim();
      postCards.forEach((card) => {
        const text = card.textContent.toLowerCase();
        if (text.includes(query)) {
          card.style.display = '';
        } else {
          card.style.display = 'none';
        }
      });
    });
  }
});
