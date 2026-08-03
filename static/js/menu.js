document.addEventListener('DOMContentLoaded', function () {
  const groups = Array.from(document.querySelectorAll('.nav-group'));
  if (!groups.length) return;

  // Zavře všechny otevřené skupiny v horní navigaci.
  function closeAll() {
    groups.forEach(group => group.removeAttribute('open'));
  }

  // Zavře všechny skupiny kromě právě aktivní.
  function closeOthers(activeGroup) {
    groups.forEach(group => {
      if (group !== activeGroup) group.removeAttribute('open');
    });
  }

  groups.forEach(group => {
    const summary = group.querySelector('summary');
    if (!summary) return;

    summary.addEventListener('click', function (event) {
      event.preventDefault();
      const isOpen = group.hasAttribute('open');
      closeOthers(group);
      if (isOpen) group.removeAttribute('open');
      else group.setAttribute('open', '');
    });

    group.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', function () {
        closeAll();
      });
    });
  });

  document.addEventListener('click', function (event) {
    if (!event.target.closest('.topnav')) closeAll();
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') closeAll();
  });
});
