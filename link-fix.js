// Attempts to correct common footer links when site may be served from / or /website/
document.addEventListener('DOMContentLoaded', function () {
    const targets = ['blog.html','privacy.html','contact.html','index.html'];
    const anchors = Array.from(document.querySelectorAll('a')).filter(a => {
        const href = a.getAttribute('href');
        if (!href) return false;
        return targets.some(t => href.endsWith(t) || href === '/' || href === '/index.html');
    });

    if (!anchors.length) return;

    // Candidate prefixes to try (order matters)
    const candidates = ['/', '/website/', '', 'website/', './', '../'];

    function findWorkingPath(target) {
        // Try candidates sequentially, return Promise resolving to path or null
        const tries = candidates.map(pref => {
            // ensure we don't produce double slashes like //blog.html
            const p = (pref.endsWith('/') ? pref.slice(0, -1) : pref) + '/' + target;
            // normalize
            let norm = p.replace(/\/g, '/').replace(/\/\//g,'/');
            // remove leading './'
            norm = norm.replace(/(^|\/)\.\//g,'$1');
            return fetch(norm, { method: 'HEAD', cache: 'no-store' })
                .then(res => res.ok ? norm : null)
                .catch(() => null);
        });
        // run sequentially to minimize requests
        return tries.reduce((acc, cur) => acc.then(found => found || cur), Promise.resolve(null));
    }

    // For each anchor, attempt to resolve a working path
    anchors.forEach(a => {
        const href = a.getAttribute('href');
        let target;
        if (href === '/' || href === '/index.html' || href === 'index.html') target = 'index.html';
        else if (href.endsWith('blog.html')) target = 'blog.html';
        else if (href.endsWith('privacy.html')) target = 'privacy.html';
        else if (href.endsWith('contact.html')) target = 'contact.html';
        else return;

        findWorkingPath(target).then(path => {
            if (path) {
                // If the current href already matches, skip
                if (a.getAttribute('href') !== path) {
                    a.setAttribute('href', path);
                }
            }
        });
    });
});
