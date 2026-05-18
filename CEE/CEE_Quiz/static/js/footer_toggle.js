(function(){
    function updateFooter() {
        var footer = document.querySelector('.footer');
        if (!footer) return;
        var footerHeight = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--footer-height')) || 86;
        // If page content height is less than or equal to viewport, fix the footer
        if (document.body.scrollHeight <= window.innerHeight) {
            footer.classList.add('fixed');
            document.body.style.paddingBottom = footerHeight + 'px';
        } else {
            footer.classList.remove('fixed');
            document.body.style.paddingBottom = '';
        }
    }

    // Run on load and resize
    window.addEventListener('load', updateFooter);
    window.addEventListener('resize', updateFooter);
    // Also run after DOM changes (basic): mutation observer
    var observer = new MutationObserver(function(){ updateFooter(); });
    observer.observe(document.body, { childList: true, subtree: true });
})();
