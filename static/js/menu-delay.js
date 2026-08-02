document.addEventListener('DOMContentLoaded', function() {
  var isDesktop = function() {
    return window.matchMedia('(hover:hover) and (pointer:fine)').matches;
  };
  var nav = document.querySelector('.topnav');
  if (!nav) return;

  var timer = null;

  function closeAll() {
    nav.querySelectorAll('details[open]').forEach(function(det) {
      det.removeAttribute('open');
    });
  }

  function cancelClose() {
    if (timer) { clearTimeout(timer); timer = null; }
  }

  function armClose() {
    if (!isDesktop()) return;
    cancelClose();
    timer = setTimeout(closeAll, 2500);
  }

  var groups = nav.querySelectorAll('.nav-group');
  groups.forEach(function(group) {
    group.addEventListener('mouseenter', function() {
      if (!isDesktop()) return;
      cancelClose();
      nav.querySelectorAll('.nav-group[open]').forEach(function(d) {
        if (d !== group) d.removeAttribute('open');
      });
      group.setAttribute('open', '');
    });
    group.addEventListener('mouseleave', function() {
      armClose();
    });
  });

  nav.addEventListener('mouseenter', cancelClose);
  nav.addEventListener('mouseleave', armClose);

  // Hash-link kliknuti v nav-menu: naviguje A zavira menu
  nav.addEventListener('click', function(e) {
    var link = e.target.closest('a[href*="#"]');
    if (!link) return;
    // zavrit vsechna details
    nav.querySelectorAll('.nav-group[open]').forEach(function(d) {
      d.removeAttribute('open');
    });
    cancelClose();
    // Pokud jsme jiz na /workbench, scrollovat na tab
    var href = link.getAttribute('href');
    var hash = href.indexOf('#') >= 0 ? href.split('#')[1] : null;
    if (hash && window.location.pathname === '/workbench') {
      e.preventDefault();
      var tabBtn = document.querySelector('.wb-tab[data-tab="' + hash.replace('tab-','') + '"]');
      if (tabBtn) tabBtn.click();
      window.scrollTo({top: 0, behavior: 'smooth'});
    }
  });

  // Pokud URL obsahuje hash, aktivovat spravny tab po nacteni
  if (window.location.pathname === '/workbench' && window.location.hash) {
    var tabName = window.location.hash.replace('#tab-','');
    var tabBtn = document.querySelector('.wb-tab[data-tab="' + tabName + '"]');
    if (tabBtn) {
      setTimeout(function() { tabBtn.click(); }, 50);
    }
  }
});
