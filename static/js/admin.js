/* ══════════════════════════════════════════════════════
   LuxScent — admin.js
   ══════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

  // ── Auto-dismiss flash ────────────────────────────────
  setTimeout(() => {
    document.querySelectorAll('.flash').forEach(el => {
      el.style.transition = 'opacity .4s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 400);
    });
  }, 4000);

  // ── Table row hover highlight ─────────────────────────
  document.querySelectorAll('.admin-table tbody tr').forEach(row => {
    row.addEventListener('mouseenter', () => row.style.background = 'rgba(201,168,76,0.05)');
    row.addEventListener('mouseleave', () => row.style.background = '');
  });

  // ── Image preview on upload ───────────────────────────
  const imageInput = document.querySelector('input[type="file"][name="image"]');
  if (imageInput) {
    imageInput.addEventListener('change', function () {
      const file = this.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = e => {
        let preview = document.getElementById('imagePreview');
        if (!preview) {
          preview = document.createElement('img');
          preview.id = 'imagePreview';
          preview.style.cssText = 'max-width:200px;max-height:200px;margin-top:10px;border-radius:6px;border:1px solid rgba(201,168,76,.3)';
          this.parentElement.appendChild(preview);
        }
        preview.src = e.target.result;
      };
      reader.readAsDataURL(file);
    });
  }

  // ── Confirm deletes ───────────────────────────────────
  document.querySelectorAll('form[data-confirm]').forEach(form => {
    form.addEventListener('submit', function (e) {
      if (!confirm(this.dataset.confirm)) e.preventDefault();
    });
  });

  // ── Sidebar active link ───────────────────────────────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.admin-nav-link').forEach(link => {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });

});
