document.addEventListener('DOMContentLoaded', () => {
    const isDesktop = () => window.matchMedia('(hover:hover) and (pointer:fine)').matches;
    const nav = document.querySelector('.topnav');
    if (!nav) return;

    let timer = null;

    function closeAll() {
        nav.querySelectorAll('details[open]').forEach(det => {
            det.removeAttribute('open');
        });
    }

    function cancelClose() {
        if (timer) clearTimeout(timer);
    }

    function armClose() {
        if (!isDesktop()) return;
        cancelClose();
        timer = setTimeout(closeAll, 3000);
    }

    // Pro CSS hover v core.css musíme nahradit CSS hover chováním přes JS na desktopu, 
    // protože HTML <details> s CSS se zavře hned jak ujede myš.

    const groups = nav.querySelectorAll('.nav-group');

    groups.forEach(group => {
        const summary = group.querySelector('summary');

        group.addEventListener('mouseenter', () => {
            if (!isDesktop()) return;
            cancelClose();
            // Zavřít ostatní, otevřít tohle
            nav.querySelectorAll('.nav-group[open]').forEach(d => {
                if(d !== group) d.removeAttribute('open');
            });
            group.setAttribute('open', '');
        });

        group.addEventListener('mouseleave', () => {
            armClose();
        });
    });

    // Celá nav plocha
    nav.addEventListener('mouseenter', cancelClose);
    nav.addEventListener('mouseleave', armClose);
});
