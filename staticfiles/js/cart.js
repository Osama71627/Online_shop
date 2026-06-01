document.addEventListener('DOMContentLoaded', function () {
  initQtySelectors();
  initCartRemoveButtons();
  updateCartBadge();
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

/* ===================== Quantity +/- Buttons ===================== */
function initQtySelectors() {
  document.querySelectorAll('.qty-selector').forEach(function (selector) {
    var input = selector.querySelector('input[type="number"]');
    if (!input) return;

    var min = parseInt(input.getAttribute('min'), 10) || 1;

    var decBtn = selector.querySelector('.qty-dec');
    var incBtn = selector.querySelector('.qty-inc');

    if (decBtn) {
      decBtn.addEventListener('click', function () {
        var val = parseInt(input.value, 10) || min;
        if (val > min) {
          input.value = val - 1;
          triggerQtyChange(input);
        }
      });
    }

    if (incBtn) {
      incBtn.addEventListener('click', function () {
        var val = parseInt(input.value, 10) || min;
        input.value = val + 1;
        triggerQtyChange(input);
      });
    }

    input.addEventListener('change', function () {
      var val = parseInt(this.value, 10);
      if (isNaN(val) || val < min) this.value = min;
      triggerQtyChange(this);
    });

    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        this.blur();
      }
    });
  });
}

function triggerQtyChange(input) {
  var event = new CustomEvent('qtychange', { detail: { input: input } });
  input.dispatchEvent(event);

  var row = input.closest('tr') || input.closest('.cart-item');
  if (row) {
    var itemId = row.dataset.itemId || getItemIdFromRow(row);
    if (itemId) {
      updateCartQuantity(itemId, input.value);
    }
  }
}

/* ===================== Update Cart Quantity ===================== */
function updateCartQuantity(itemId, quantity) {
  var csrf = getCSRFToken();

  fetch('/cart/update/' + itemId + '/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrf,
      'X-Requested-With': 'XMLHttpRequest'
    },
    body: 'quantity=' + encodeURIComponent(quantity)
  })
    .then(function (res) {
      if (!res.ok) throw new Error('Failed to update quantity');
      return res.json();
    })
    .then(function (data) {
      updateCartTotals(data);
      updateCartBadge();
      if (typeof showToast === 'function') {
        showToast('Cart updated', 'success');
      }
    })
    .catch(function () {
      if (typeof showToast === 'function') {
        showToast('Failed to update quantity', 'error');
      }
    });
}

/* ===================== Remove Cart Item ===================== */
function removeCartItem(itemId) {
  var csrf = getCSRFToken();

  fetch('/cart/remove/' + itemId + '/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrf,
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
    .then(function (res) {
      if (!res.ok) throw new Error('Failed to remove item');
      return res.json();
    })
    .then(function (data) {
      var row = document.querySelector(
        'tr[data-item-id="' + itemId + '"], .cart-item[data-item-id="' + itemId + '"]'
      );
      if (row) {
        row.style.transition = 'all 0.3s ease';
        row.style.transform = 'translateX(40px)';
        row.style.opacity = '0';
        setTimeout(function () {
          if (row.parentElement) row.parentElement.removeChild(row);
          updateCartTotals(data);
          updateCartBadge();
          checkEmptyCart();
        }, 300);
      } else {
        updateCartTotals(data);
        updateCartBadge();
        checkEmptyCart();
      }
      if (typeof showToast === 'function') {
        showToast('Item removed from cart', 'success');
      }
    })
    .catch(function () {
      if (typeof showToast === 'function') {
        showToast('Failed to remove item', 'error');
      }
    });
}

function initCartRemoveButtons() {
  document.querySelectorAll('.cart-remove-btn').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      var itemId = this.dataset.itemId || this.getAttribute('data-item-id');
      if (!itemId) {
        var row = this.closest('tr') || this.closest('.cart-item');
        if (row) itemId = row.dataset.itemId;
      }
      if (itemId && confirm('Remove this item from your cart?')) {
        removeCartItem(itemId);
      }
    });
  });
}

/* ===================== Add to Cart ===================== */
function addToCart(productId) {
  var csrf = getCSRFToken();
  var quantity = 1;

  var qtyInput = document.querySelector('.qty-selector input');
  if (qtyInput) {
    quantity = parseInt(qtyInput.value, 10) || 1;
  }

  fetch('/cart/add/' + productId + '/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrf,
      'X-Requested-With': 'XMLHttpRequest'
    },
    body: 'quantity=' + encodeURIComponent(quantity)
  })
    .then(function (res) {
      if (!res.ok) throw new Error('Failed to add to cart');
      return res.json();
    })
    .then(function (data) {
      updateCartBadge();
      if (typeof showToast === 'function') {
        showToast(data.message || 'Added to cart!', 'success');
      }
      var addBtn = document.querySelector('.add-to-cart-btn');
      if (addBtn) {
        addBtn.textContent = '✓ Added';
        addBtn.classList.remove('btn-primary');
        addBtn.classList.add('btn-success');
        setTimeout(function () {
          addBtn.textContent = 'Add to Cart';
          addBtn.classList.remove('btn-success');
          addBtn.classList.add('btn-primary');
        }, 2000);
      }
    })
    .catch(function () {
      if (typeof showToast === 'function') {
        showToast('Failed to add to cart', 'error');
      }
    });
}

/* ===================== Update Cart Badge ===================== */
function updateCartBadge() {
  var badge = document.querySelector('.cart-badge');
  if (!badge) return;

  fetch('/cart/count/', {
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
    .then(function (res) {
      if (!res.ok) throw new Error('Failed to fetch count');
      return res.json();
    })
    .then(function (data) {
      var count = data.count || data.cart_count || data.total_items || 0;
      badge.textContent = count;
      badge.style.display = count > 0 ? 'flex' : 'none';
    })
    .catch(function () {
      // keep current badge value
    });
}

/* ===================== Cart Totals ===================== */
function updateCartTotals(data) {
  if (data.subtotal !== undefined) {
    var subtotalEl = document.querySelector('.cart-subtotal');
    if (subtotalEl) subtotalEl.textContent = '$' + parseFloat(data.subtotal).toFixed(2);
  }

  if (data.total !== undefined) {
    var totalEls = document.querySelectorAll('.cart-total');
    totalEls.forEach(function (el) {
      el.textContent = '$' + parseFloat(data.total).toFixed(2);
    });
  }

  if (data.discount !== undefined) {
    var discountEl = document.querySelector('.cart-discount');
    if (discountEl) {
      discountEl.textContent = '-$' + parseFloat(data.discount).toFixed(2);
    }
  }

  if (data.shipping !== undefined) {
    var shippingEl = document.querySelector('.cart-shipping');
    if (shippingEl) {
      shippingEl.textContent =
        data.shipping === 0 || data.shipping === '0.00'
          ? 'Free'
          : '$' + parseFloat(data.shipping).toFixed(2);
    }
  }

  if (data.item_count !== undefined) {
    var itemCountEl = document.querySelector('.cart-item-count');
    if (itemCountEl) {
      itemCountEl.textContent = data.item_count + ' item' + (data.item_count !== 1 ? 's' : '');
    }
  }
}

/* ===================== Helpers ===================== */
function getItemIdFromRow(row) {
  return row.dataset.itemId || null;
}

function checkEmptyCart() {
  var rows = document.querySelectorAll('.cart-table tbody tr, .cart-item');
  if (!rows.length) {
    var container = document.querySelector('.cart-container') || document.querySelector('.cart-table');
    if (container) {
      container.innerHTML =
        '<div class="empty-cart" style="text-align:center;padding:60px 20px;">' +
        '<div style="font-size:3rem;margin-bottom:16px;opacity:0.3;">🛒</div>' +
        '<h2>Your cart is empty</h2>' +
        '<p style="color:var(--gray);margin:12px 0 24px;">Looks like you have not added anything yet.</p>' +
        '<a href="/products/" class="btn btn-primary">Continue Shopping</a>' +
        '</div>';
    }
  }
}
