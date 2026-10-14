(() => {
    const messageBox = () => {
        let box = document.querySelector('[data-cart-messages]');
        if (!box) {
            box = document.createElement('div');
            box.dataset.cartMessages = '';
            box.setAttribute('aria-live', 'polite');
            box.className = 'mb-3';
            const container = document.querySelector('main .container, .container');
            if (container) container.prepend(box);
        }
        return box;
    };

    const showMessage = (message, success = true) => {
        const box = messageBox();
        if (!box) return;
        box.replaceChildren();
        const alert = document.createElement('div');
        alert.className = `alert alert-${success ? 'success' : 'danger'}`;
        alert.textContent = message || (success ? 'Thao tác thành công.' : 'Đã xảy ra lỗi.');
        box.appendChild(alert);
    };

    const money = value => new Intl.NumberFormat('vi-VN', {
        maximumFractionDigits: 0
    }).format(Number(value) || 0) + ' đ';

    const post = async (url, body) => {
        const options = {
            method: 'POST',
            headers: { 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }
        };
        if (body) {
            options.headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(body);
        }
        const response = await fetch(url, options);
        let data;
        try { data = await response.json(); }
        catch (_) { throw new Error('Máy chủ trả về dữ liệu không hợp lệ.'); }
        if (!response.ok || !data.success) throw new Error(data.message || 'Không thể thực hiện thao tác.');
        return data;
    };

    const updateCartCount = count => {
        document.querySelectorAll('[data-cart-count], #cart-count, .cart-count').forEach(el => {
            el.textContent = count;
        });
    };

    const updateTotals = () => {
        let total = 0;
        document.querySelectorAll('[data-cart-row]').forEach(row => {
            const price = Number(row.dataset.price) || 0;
            const quantity = Number(row.querySelector('[name="quantity"]')?.value) || 0;
            const subtotal = price * quantity;
            total += subtotal;
            const subtotalEl = row.querySelector('[data-line-subtotal]');
            if (subtotalEl) subtotalEl.textContent = money(subtotal);
        });
        const totalEl = document.querySelector('[data-cart-total]');
        if (totalEl) totalEl.textContent = money(total);
    };

    document.addEventListener('submit', async event => {
        const form = event.target;
        if (!(form instanceof HTMLFormElement)) return;
        const addMatch = form.action.match(/\/cart\/add\/(\d+)(?:\?|$)/);
        if (addMatch) {
            event.preventDefault();
            try {
                const data = await post(form.action);
                updateCartCount(data.cart_count);
                showMessage(data.message, true);
            } catch (error) { showMessage(error.message, false); }
            return;
        }

        if (form.action.includes('/cart/update/')) {
            event.preventDefault();
            const row = form.closest('[data-cart-row]');
            const quantity = Number(form.querySelector('[name="quantity"]')?.value);
            if (!Number.isInteger(quantity) || quantity <= 0) {
                showMessage('Số lượng phải là số nguyên lớn hơn 0.', false);
                return;
            }
            try {
                const data = await post(form.action, { quantity });
                updateCartCount(data.cart_count);
                updateTotals();
                showMessage(data.message, true);
            } catch (error) {
                showMessage(error.message, false);
                if (row) updateTotals();
            }
            return;
        }

        if (form.action.includes('/cart/remove/')) {
            event.preventDefault();
            try {
                const data = await post(form.action);
                form.closest('[data-cart-row]')?.remove();
                updateCartCount(data.cart_count);
                updateTotals();
                showMessage(data.message, true);
                if (!document.querySelector('[data-cart-row]')) {
                    document.querySelector('#cart-content')?.classList.add('d-none');
                    document.querySelector('#cart-empty')?.classList.remove('d-none');
                }
            } catch (error) { showMessage(error.message, false); }
        }
    });

    document.addEventListener('change', event => {
        if (event.target.matches('[data-cart-row] [name="quantity"]')) updateTotals();
    });
})();
