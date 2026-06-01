document.addEventListener('DOMContentLoaded', function () {
  initNavbarScroll();
  initMobileMenu();
  initSearchAutocomplete();
  initHeroSlider();
  initCountdownTimers();
  initSmoothScroll();
  initBackToTop();
  initLazyLoading();
  initNewsletterForm();
});

/* ===================== Navbar Scroll Effect ===================== */
function initNavbarScroll() {
  const navbar = document.querySelector('.navbar-glass');
  if (!navbar) return;

  const checkScroll = () => {
    navbar.classList.toggle('scrolled', window.scrollY > 50);
  };

  checkScroll();
  window.addEventListener('scroll', checkScroll, { passive: true });
}

/* ===================== Mobile Menu ===================== */
function initMobileMenu() {
  const hamburger = document.querySelector('.hamburger');
  const navLinks = document.querySelector('.nav-links');
  if (!hamburger || !navLinks) return;

  hamburger.addEventListener('click', function () {
    navLinks.classList.toggle('open');
    this.classList.toggle('active');
  });

  document.querySelectorAll('.nav-links a').forEach(function (link) {
    link.addEventListener('click', function () {
      navLinks.classList.remove('open');
      hamburger.classList.remove('active');
    });
  });
}

/* ===================== Search Autocomplete ===================== */
function initSearchAutocomplete() {
  const searchInput = document.querySelector('.search-input');
  if (!searchInput) return;

  const dropdown = document.createElement('div');
  dropdown.className = 'search-results-dropdown';
  searchInput.parentElement.appendChild(dropdown);

  let debounceTimer;

  searchInput.addEventListener('input', function () {
    clearTimeout(debounceTimer);
    const q = this.value.trim();
    if (q.length < 2) {
      dropdown.classList.remove('open');
      dropdown.innerHTML = '';
      return;
    }
    debounceTimer = setTimeout(() => fetchSearchResults(q, dropdown), 300);
  });

  document.addEventListener('click', function (e) {
    if (!searchInput.parentElement.contains(e.target)) {
      dropdown.classList.remove('open');
    }
  });

  searchInput.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      dropdown.classList.remove('open');
      this.blur();
    }
  });
}

function fetchSearchResults(q, dropdown) {
  dropdown.innerHTML =
    '<div class="search-result-item" style="justify-content:center;color:var(--gray);font-size:0.85rem;">Searching...</div>';
  dropdown.classList.add('open');

  fetch('/search/?q=' + encodeURIComponent(q), {
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
    .then(function (res) {
      if (!res.ok) throw new Error('Search failed');
      return res.json();
    })
    .then(function (data) {
      renderSearchResults(data, dropdown);
    })
    .catch(function () {
      dropdown.innerHTML =
        '<div class="search-result-item" style="justify-content:center;color:var(--gray);font-size:0.85rem;">No results found</div>';
    });
}

function renderSearchResults(data, dropdown) {
  var items = data.results || data.products || data || [];
  if (!items.length) {
    dropdown.innerHTML =
      '<div class="search-result-item" style="justify-content:center;color:var(--gray);font-size:0.85rem;">No products found</div>';
    return;
  }

  dropdown.innerHTML = items
    .slice(0, 8)
    .map(function (item) {
      var name = item.name || item.title || 'Product';
      var price = item.price || '';
      var image = item.image || item.thumbnail || item.img || '';
      var url = item.url || '/product/' + (item.slug || item.id) + '/';
      return (
        '<a href="' +
        url +
        '" class="search-result-item">' +
        (image
          ? '<img src="' + image + '" alt="' + name + '" loading="lazy">'
          : '<div style="width:44px;height:44px;border-radius:6px;background:var(--light-gray)"></div>') +
        '<div class="result-info">' +
        '<h4>' + escapeHtml(name) + '</h4>' +
        (price ? '<span>$' + parseFloat(price).toFixed(2) + '</span>' : '') +
        '</div>' +
        '</a>'
      );
    })
    .join('');
}

/* ===================== Hero Slider ===================== */
function initHeroSlider() {
  const slider = document.querySelector('.hero-slider');
  if (!slider) return;

  const slides = slider.querySelectorAll('.hero-slide');
  const dotsContainer = slider.querySelector('.hero-dots');
  const prevBtn = slider.querySelector('.hero-slider-arrow.prev');
  const nextBtn = slider.querySelector('.hero-slider-arrow.next');
  if (!slides.length) return;

  let current = 0;
  let interval;

  function goTo(index) {
    slides.forEach(function (s, i) {
      s.classList.toggle('active', i === index);
    });
    if (dotsContainer) {
      var dots = dotsContainer.querySelectorAll('.hero-dot');
      dots.forEach(function (d, i) {
        d.classList.toggle('active', i === index);
      });
    }
    current = index;
  }

  function nextSlide() {
    goTo((current + 1) % slides.length);
  }

  function prevSlide() {
    goTo((current - 1 + slides.length) % slides.length);
  }

  function startAutoPlay() {
    stopAutoPlay();
    interval = setInterval(nextSlide, 5000);
  }

  function stopAutoPlay() {
    clearInterval(interval);
  }

  if (dotsContainer) {
    slides.forEach(function (_, i) {
      var dot = document.createElement('button');
      dot.className = 'hero-dot' + (i === 0 ? ' active' : '');
      dot.setAttribute('aria-label', 'Go to slide ' + (i + 1));
      dot.addEventListener('click', function () {
        goTo(i);
        startAutoPlay();
      });
      dotsContainer.appendChild(dot);
    });
  }

  if (prevBtn) prevBtn.addEventListener('click', function () { prevSlide(); startAutoPlay(); });
  if (nextBtn) nextBtn.addEventListener('click', function () { nextSlide(); startAutoPlay(); });

  slider.addEventListener('mouseenter', stopAutoPlay);
  slider.addEventListener('mouseleave', startAutoPlay);

  startAutoPlay();
}

/* ===================== Countdown Timer ===================== */
function initCountdownTimers() {
  document.querySelectorAll('.countdown-timer').forEach(function (el) {
    var endStr = el.getAttribute('data-end') || el.dataset.end;
    if (!endStr) return;

    var end = new Date(endStr.replace(/-/g, '/')).getTime();

    function update() {
      var now = new Date().getTime();
      var diff = end - now;

      if (diff <= 0) {
        el.innerHTML = '<span class="text-gold">Sale ended</span>';
        return;
      }

      var days = Math.floor(diff / (1000 * 60 * 60 * 24));
      var hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      var minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      var seconds = Math.floor((diff % (1000 * 60)) / 1000);

      el.innerHTML =
        '<div class="countdown-unit"><span>' +
        String(days).padStart(2, '0') +
        '</span><small>Days</small></div>' +
        '<span class="countdown-sep">:</span>' +
        '<div class="countdown-unit"><span>' +
        String(hours).padStart(2, '0') +
        '</span><small>Hrs</small></div>' +
        '<span class="countdown-sep">:</span>' +
        '<div class="countdown-unit"><span>' +
        String(minutes).padStart(2, '0') +
        '</span><small>Min</small></div>' +
        '<span class="countdown-sep">:</span>' +
        '<div class="countdown-unit"><span>' +
        String(seconds).padStart(2, '0') +
        '</span><small>Sec</small></div>';
    }

    update();
    setInterval(update, 1000);
  });
}

/* ===================== Toast Notification System ===================== */
function showToast(message, type) {
  type = type || 'info';

  var container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  var icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ'
  };

  var toast = document.createElement('div');
  toast.className = 'toast ' + type;
  toast.innerHTML =
    '<span class="toast-icon">' +
    (icons[type] || icons.info) +
    '</span>' +
    '<span class="toast-message">' +
    escapeHtml(message) +
    '</span>' +
    '<button class="toast-close" aria-label="Close">&times;</button>';

  container.appendChild(toast);

  toast.querySelector('.toast-close').addEventListener('click', function () {
    dismissToast(toast);
  });

  setTimeout(function () {
    dismissToast(toast);
  }, 4000);
}

function dismissToast(toast) {
  if (!toast || toast.dataset.dismissing) return;
  toast.dataset.dismissing = 'true';
  toast.style.animation = 'slideOut 0.4s ease forwards';
  setTimeout(function () {
    if (toast.parentElement) {
      toast.parentElement.removeChild(toast);
      var container = document.querySelector('.toast-container');
      if (container && !container.children.length) {
        container.parentElement.removeChild(container);
      }
    }
  }, 400);
}

/* ===================== Smooth Scroll ===================== */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      var target = document.querySelector(this.getAttribute('href'));
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
}

/* ===================== Back to Top Button ===================== */
function initBackToTop() {
  var btn = document.querySelector('.back-to-top');
  if (!btn) {
    btn = document.createElement('button');
    btn.className = 'back-to-top';
    btn.setAttribute('aria-label', 'Back to top');
    btn.innerHTML = '↑';
    document.body.appendChild(btn);

    btn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  var checkVisibility = function () {
    btn.classList.toggle('visible', window.scrollY > 400);
  };

  checkVisibility();
  window.addEventListener('scroll', checkVisibility, { passive: true });
}

/* ===================== Lazy Loading Images ===================== */
function initLazyLoading() {
  if (!('IntersectionObserver' in window)) {
    document.querySelectorAll('[data-src]').forEach(function (img) {
      img.src = img.dataset.src;
    });
    return;
  }

  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var img = entry.target;
          var src = img.dataset.src;
          if (src) {
            img.src = src;
            img.removeAttribute('data-src');
          }
          img.classList.add('loaded');
          observer.unobserve(img);
        }
      });
    },
    {
      rootMargin: '100px 0px',
      threshold: 0.01
    }
  );

  document.querySelectorAll('img[data-src]').forEach(function (img) {
    observer.observe(img);
  });
}

/* ===================== Newsletter Form ===================== */
function initNewsletterForm() {
  var forms = document.querySelectorAll('.newsletter-form');
  if (!forms.length) return;

  forms.forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var input = form.querySelector('input[type="email"]');
      var email = input ? input.value.trim() : '';
      if (!email) return;

      var submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Subscribing...';
      }

      var csrf = getCSRFToken();

      fetch('/newsletter/subscribe/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': csrf,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: 'email=' + encodeURIComponent(email)
      })
        .then(function (res) {
          if (!res.ok) throw new Error('Subscription failed');
          return res.json();
        })
        .then(function (data) {
          if (input) input.value = '';
          showToast(data.message || 'Successfully subscribed!', 'success');
        })
        .catch(function () {
          showToast('Something went wrong. Please try again.', 'error');
        })
        .finally(function () {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Subscribe';
          }
        });
    });
  });
}

/* ===================== Utility Functions ===================== */
function getCSRFToken() {
  var cookies = document.cookie.split(';');
  for (var i = 0; i < cookies.length; i++) {
    var c = cookies[i].trim();
    if (c.startsWith('csrftoken=')) return c.substring(10);
  }
  var meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.getAttribute('content') : '';
}

function escapeHtml(text) {
  if (!text) return '';
  var div = document.createElement('div');
  div.appendChild(document.createTextNode(text));
  return div.innerHTML;
}

/* ===================== Alpine.js Data (if Alpine loaded) ===================== */
if (typeof Alpine !== 'undefined') {
  document.addEventListener('alpine:init', function () {
    Alpine.data('cartStore', function () {
      return {
        count: 0,
        total: 0,
        init: function () {
          if (window.updateCartBadge) updateCartBadge();
        }
      };
    });

    Alpine.data('slider', function () {
      return {
        current: 0,
        slides: [],
        init: function () {
          var self = this;
          this.slides = this.$el.querySelectorAll('.hero-slide');
          this.slides.forEach(function (s, i) {
            if (s.classList.contains('active')) self.current = i;
          });
        },
        goTo: function (i) {
          this.current = i;
        },
        next: function () {
          this.current = (this.current + 1) % this.slides.length;
        },
        prev: function () {
          this.current = (this.current - 1 + this.slides.length) % this.slides.length;
        }
      };
    });

    Alpine.data('productCard', function () {
      return {
        showQuickView: false,
        quickViewData: null,
        openQuickView: function (productId) {
          var self = this;
          fetch('/product/quick-view/' + productId + '/', {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
          })
            .then(function (r) { return r.json(); })
            .then(function (data) {
              self.quickViewData = data;
              self.showQuickView = true;
            });
        },
        closeQuickView: function () {
          this.showQuickView = false;
        }
      };
    });
  });
}
