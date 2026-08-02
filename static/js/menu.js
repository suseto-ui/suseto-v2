document.addEventListener('DOMContentLoaded', function () {
  var groups = document.querySelectorAll('.nav-group');
  if (!groups.length) return;

  // menu-delay.js resi desktop hover/chovani.
  // Tady nechame jen bezpecne mobilni/klik chovani, aby se skripty netloukly.
  groups.forEach(function (group) {
    var summary = group.querySelector('summary');
    if (!summary) return;

    summary.addEventListener('click', function () {
      var isDesktop = window.matchMedia('(hover:hover) and (pointer:fine)').matches;
      if (isDesktop) {
        document.querySelectorAll('.nav-group[open]').forEach(function (x) {
          if (x !== group) x.removeAttribute('open');
        });
        return;
      }

      setTimeout(function () {
        document.querySelectorAll('.nav-group[open]').forEach(function (x) {
          if (x !== group) x.removeAttribute('open');
        });
      }, 0);
    });
  });
});
