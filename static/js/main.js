/* ══════════════════════════════════════════════════════
   LuxScent — main.js
   ══════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

  // ── NAVBAR scroll effect ──────────────────────────────
  const navbar = document.getElementById('navbar');
  window.addEventListener('scroll', () => {
    navbar?.classList.toggle('scrolled', window.scrollY > 50);
  }, { passive: true });

  // ── HAMBURGER menu ────────────────────────────────────
  const hamburger = document.getElementById('hamburger');
  const navLinks  = document.getElementById('navLinks');
  hamburger?.addEventListener('click', () => {
    navLinks?.classList.toggle('open');
    hamburger.classList.toggle('active');
  });

  // ── SEARCH dropdown ───────────────────────────────────
  const searchToggle   = document.getElementById('searchToggle');
  const searchDropdown = document.getElementById('searchDropdown');
  const quickSearch    = document.getElementById('quickSearch');
  const searchResults  = document.getElementById('searchResults');

  searchToggle?.addEventListener('click', (e) => {
    e.stopPropagation();
    searchDropdown?.classList.toggle('open');
    if (searchDropdown?.classList.contains('open')) quickSearch?.focus();
  });

  document.addEventListener('click', (e) => {
    if (!searchDropdown?.contains(e.target) && e.target !== searchToggle) {
      searchDropdown?.classList.remove('open');
    }
  });

  let searchTimer;
  quickSearch?.addEventListener('input', function () {
    clearTimeout(searchTimer);
    const q = this.value.trim();
    if (!q) { searchResults.innerHTML = ''; return; }
    searchTimer = setTimeout(() => {
      fetch(`/api/produtos?q=${encodeURIComponent(q)}`)
        .then(r => r.json())
        .then(products => {
          if (!products.length) {
            searchResults.innerHTML = '<div style="padding:14px 16px;color:#888;font-size:.85rem">Nenhum resultado.</div>';
            return;
          }
          searchResults.innerHTML = products.slice(0, 6).map((p, i) => `
            <a class="search-result-item" href="/produto/${p.id}">
              <div class="search-result-img product-img-placeholder" style="background:var(--grad-${(i%4)+1});width:36px;height:36px;font-size:.7rem;gap:0">
                ${p.name.substring(0,2).toUpperCase()}
              </div>
              <div class="search-result-info">
                <div class="search-result-name">${p.name}</div>
                <div class="search-result-price">R$ ${p.price.toFixed(2).replace('.',',')}</div>
              </div>
            </a>
          `).join('');
        })
        .catch(() => {});
    }, 280);
  });

  // ── AJAX CART forms ───────────────────────────────────
  initAjaxForms();

  // ── AUTO-DISMISS flash messages ───────────────────────
  setTimeout(() => {
    document.querySelectorAll('.flash').forEach(el => {
      el.style.transition = 'opacity .4s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 400);
    });
  }, 4500);

  // ── SCROLL reveal (simple IntersectionObserver) ───────
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.style.opacity = '1';
        e.target.style.transform = 'translateY(0)';
        observer.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.product-card, .testimonial, .cat-card, .bestseller-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(24px)';
    el.style.transition = 'opacity .5s ease, transform .5s ease';
    observer.observe(el);
  });

});

// ── AJAX CART init (called after dynamic render too) ──────
function initAjaxForms() {
  document.querySelectorAll('.ajax-cart-form').forEach(form => {
    if (form.dataset.bound) return;          // evitar rebind
    form.dataset.bound = 'true';

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const btn = this.querySelector('button');
      if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>'; }

      fetch(this.action, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        body: new FormData(this)
      })
        .then(r => r.json())
        .then(data => {
          if (data.success) {
            // Atualizar badge do carrinho
            document.querySelectorAll('#cartBadge').forEach(el => el.textContent = data.cart_count);
            showToast(data.message || 'Adicionado ao carrinho!', 'success');
          }
        })
        .catch(() => showToast('Erro ao adicionar. Tente novamente.', 'danger'))
        .finally(() => {
          if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fas fa-shopping-bag"></i>'; }
        });
    });
  });
}

// ── TOAST NOTIFICATION ────────────────────────────────────
function showToast(message, type = 'success') {
  let container = document.getElementById('flashContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'flashContainer';
    container.className = 'flash-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `flash flash-${type}`;
  toast.innerHTML = `<span>${message}</span><button onclick="this.parentElement.remove()">✕</button>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = 'opacity .4s';
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 400);
  }, 3500);
}
