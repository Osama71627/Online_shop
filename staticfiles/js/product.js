document.addEventListener('DOMContentLoaded', function () {
  initImageGallery();
  initImageZoom();
  initWishlistButtons();
  initReviewForm();
  initProductTabs();
});

/* ===================== CSRF Token ===================== */
function getCSRFToken() {
  var cookies = document.cookie.split(';');
  for (var i = 0; i < cookies.length; i++) {
    var c = cookies[i].trim();
    if (c.startsWith('csrftoken=')) return c.substring(10);
  }
  var meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.getAttribute('content') : '';
}

/* ===================== Product Image Gallery ===================== */
function initImageGallery() {
  var mainImage = document.querySelector('.product-main-image img');
  var thumbnails = document.querySelectorAll('.product-thumbnail');
  if (!mainImage || !thumbnails.length) return;

  thumbnails.forEach(function (thumb) {
    thumb.addEventListener('click', function () {
      var src = this.dataset.image || this.getAttribute('src');
      if (!src) {
        var img = this.querySelector('img');
        if (img) src = img.dataset.src || img.getAttribute('src');
      }
      if (!src) return;

      thumbnails.forEach(function (t) { t.classList.remove('active'); });
      this.classList.add('active');

      mainImage.style.opacity = '0';
      setTimeout(function () {
        mainImage.setAttribute('src', src);
        mainImage.style.opacity = '1';
      }, 150);
    });
  });
}

/* ===================== Image Zoom (Magnifying Glass) ===================== */
function initImageZoom() {
  var container = document.querySelector('.product-main-image');
  if (!container) return;

  var img = container.querySelector('img');
  if (!img) return;

  var lens = document.createElement('div');
  lens.className = 'image-zoom-lens';
  lens.style.cssText =
    'position:absolute;width:120px;height:120px;border:2px solid rgba(255,255,255,0.5);' +
    'border-radius:50%;background-repeat:no-repeat;pointer-events:none;' +
    'display:none;z-index:10;box-shadow:0 0 20px rgba(0,0,0,0.2);' +
    'background-color:rgba(255,255,255,0.3);';
  container.appendChild(lens);

  var zoomResult = null;

  container.addEventListener('mouseenter', function () {
    if (window.innerWidth < 768) return;
    lens.style.display = 'block';
  });

  container.addEventListener('mouseleave', function () {
    lens.style.display = 'none';
  });

  container.addEventListener('mousemove', function (e) {
    if (window.innerWidth < 768) return;

    var rect = container.getBoundingClientRect();
    var x = e.clientX - rect.left;
    var y = e.clientY - rect.top;

    var lw = lens.offsetWidth / 2;
    var lh = lens.offsetHeight / 2;

    var lensX = Math.max(0, Math.min(x - lw, rect.width - lens.offsetWidth));
    var lensY = Math.max(0, Math.min(y - lh, rect.height - lens.offsetHeight));

    lens.style.left = lensX + 'px';
    lens.style.top = lensY + 'px';

    var cx = (lensX / rect.width) * 100;
    var cy = (lensY / rect.height) * 100;

    lens.style.backgroundImage = 'url(' + img.getAttribute('src') + ')';
    lens.style.backgroundSize = (rect.width * 2.5) + 'px ' + (rect.height * 2.5) + 'px';
    lens.style.backgroundPosition = '-' + (lensX * 2.5) + 'px -' + (lensY * 2.5) + 'px';
  });
}

/* ===================== Add to Wishlist ===================== */
function initWishlistButtons() {
  document.querySelectorAll('.wishlist-btn').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      var productId = this.dataset.productId || this.getAttribute('data-product-id');
      if (!productId) return;

      var csrf = getCSRFToken();
      var self = this;

      fetch('/wishlist/toggle/' + productId + '/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': csrf,
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
        .then(function (res) {
          if (!res.ok) throw new Error('Failed');
          return res.json();
        })
        .then(function (data) {
          var isInWishlist = data.in_wishlist || data.added;
          self.classList.toggle('in-wishlist', isInWishlist);
          if (typeof showToast === 'function') {
            showToast(
              isInWishlist ? 'Added to wishlist' : 'Removed from wishlist',
              'success'
            );
          }
        })
        .catch(function () {
          if (typeof showToast === 'function') {
            showToast('Failed to update wishlist', 'error');
          }
        });
    });
  });
}

/* ===================== Review Form ===================== */
function initReviewForm() {
  var form = document.querySelector('.review-form');
  if (!form) return;

  form.addEventListener('submit', function (e) {
    e.preventDefault();

    var formData = new FormData(form);
    var csrf = getCSRFToken();

    var submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Submitting...';
    }

    var url = form.getAttribute('action') || window.location.pathname + 'review/';

    fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrf,
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: formData
    })
      .then(function (res) {
        if (!res.ok) throw new Error('Failed to submit review');
        return res.json();
      })
      .then(function (data) {
        form.reset();

        if (data.review_html) {
          var list = document.querySelector('.reviews-list');
          if (list) {
            list.insertAdjacentHTML('afterbegin', data.review_html);
          }
        }

        if (typeof showToast === 'function') {
          showToast(data.message || 'Review submitted successfully!', 'success');
        }

        var ratingSummary = document.querySelector('.rating-summary');
        if (ratingSummary && data.rating_avg !== undefined) {
          ratingSummary.innerHTML = formatRatingSummary(data.rating_avg, data.rating_count);
        }
      })
      .catch(function () {
        if (typeof showToast === 'function') {
          showToast('Failed to submit review. Please try again.', 'error');
        }
      })
      .finally(function () {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Submit Review';
        }
      });
  });

  initStarRating();
}

function initStarRating() {
  var stars = document.querySelectorAll('.star-rating-input .star');
  if (!stars.length) return;

  var input = document.querySelector('.star-rating-input input[type="hidden"]');

  stars.forEach(function (star) {
    star.addEventListener('click', function () {
      var value = parseInt(this.dataset.value, 10);
      if (input) input.value = value;

      stars.forEach(function (s, i) {
        s.classList.toggle('active', i < value);
        s.textContent = i < value ? '★' : '☆';
      });
    });

    star.addEventListener('mouseenter', function () {
      var value = parseInt(this.dataset.value, 10);
      stars.forEach(function (s, i) {
        s.classList.toggle('hover', i < value);
      });
    });

    star.addEventListener('mouseleave', function () {
      stars.forEach(function (s) {
        s.classList.remove('hover');
      });
    });
  });
}

function formatRatingSummary(avg, count) {
  var full = Math.round(avg);
  var html = '<div class="stars">';
  for (var i = 1; i <= 5; i++) {
    html += '<span class="star ' + (i <= full ? 'filled' : '') + '">' + (i <= full ? '★' : '☆') + '</span>';
  }
  html += '<span class="rating-count">(' + (count || 0) + ' reviews)</span></div>';
  return html;
}

/* ===================== Product Tabs ===================== */
function initProductTabs() {
  var tabs = document.querySelectorAll('.product-tab');
  if (!tabs.length) return;

  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      var target = this.dataset.tab || this.getAttribute('data-target');
      if (!target) return;

      tabs.forEach(function (t) { t.classList.remove('active'); });
      this.classList.add('active');

      document.querySelectorAll('.tab-panel').forEach(function (panel) {
        panel.classList.remove('active');
      });

      var targetPanel = document.querySelector(target);
      if (targetPanel) targetPanel.classList.add('active');
    });
  });

  // activate first tab if none active
  var activeTab = document.querySelector('.product-tab.active');
  if (!activeTab && tabs.length) {
    tabs[0].click();
  }
}
