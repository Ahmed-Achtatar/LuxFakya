document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form[action*="/cart/add/"]');

    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;

            // Optional: Loading state
            // submitBtn.disabled = true;
            // submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

            const formData = new FormData(form);
            const actionUrl = form.getAttribute('action');

            fetch(actionUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                    return;
                }
                return response.json();
            })
            .then(data => {
                if (data && data.status === 'success') {
                    // Update cart count badges
                    // Select all cart badges (mobile and desktop)
                    const badges = document.querySelectorAll('.fa-shopping-bag + .badge, .fa-shopping-cart + .badge');
                    badges.forEach(badge => {
                        badge.textContent = data.cart_count;
                        badge.style.display = 'inline-block'; // Ensure visible
                    });

                    // Also check for the specific mobile badge if selector differs
                    const mobileBadge = document.querySelector('.navbar-toggler .badge');
                    if (mobileBadge) mobileBadge.textContent = data.cart_count;

                    // Show toast
                    showToast(data.message, 'success');
                } else if (data) {
                    showToast(data.message || 'Error adding to cart', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Fallback to normal submit if AJAX fails
                // form.submit();
                showToast('An error occurred. Please try again.', 'danger');
            })
            .finally(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            });
        });
    });
});

function showToast(message, type='success') {
    // Check if toast container exists
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '1055';
        document.body.appendChild(toastContainer);
    }

    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0 shadow-lg mb-2`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');

    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body fs-6">
                ${type === 'success' ? '<i class="fas fa-check-circle me-2"></i>' : '<i class="fas fa-exclamation-circle me-2"></i>'}
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    toastContainer.appendChild(toastEl);

    // Check if bootstrap is defined
    if (typeof bootstrap !== 'undefined') {
        const toast = new bootstrap.Toast(toastEl, { delay: 3000 });
        toast.show();
        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    } else {
        // Fallback simple visibility
        toastEl.classList.add('show');
        setTimeout(() => {
            toastEl.remove();
        }, 3000);
    }
}
