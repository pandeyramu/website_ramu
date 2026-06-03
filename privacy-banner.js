(function () {
  const STORAGE_KEY = 'privacyConsent';
  const banner = document.createElement('aside');
  banner.className = 'privacy-consent-banner is-hidden';
  banner.setAttribute('role', 'dialog');
  banner.setAttribute('aria-live', 'polite');
  banner.innerHTML = '<p>This site uses basic cookies and analytics-related cookies for functionality and site improvement. Accept or reject your preference.</p><div class="banner-actions"><button type="button" data-choice="accept">Accept</button><button type="button" data-choice="reject">Reject</button></div>';

  function showBanner() {
    document.body.appendChild(banner);
    banner.classList.remove('is-hidden');
  }

  function hideBanner() {
    banner.classList.add('is-hidden');
  }

  function saveChoice(choice) {
    localStorage.setItem(STORAGE_KEY, choice);
    hideBanner();
  }

  if (!localStorage.getItem(STORAGE_KEY)) {
    showBanner();
  }

  banner.addEventListener('click', function (event) {
    const button = event.target.closest('button[data-choice]');
    if (!button) return;
    saveChoice(button.dataset.choice);
  });
})();
