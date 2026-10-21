(() => {
    const timers = new WeakMap();
    const saveChains = new WeakMap();
    const revisions = new WeakMap();
    const money = value => new Intl.NumberFormat('vi-VN', { maximumFractionDigits: 0 }).format(Number(value) || 0) + ' đ';

    const showMessage = (message, success = true) => {
        let box = document.querySelector('[data-cart-messages]');
        if (!box) {
            box = document.createElement('div');
            box.dataset.cartMessages = '';
            box.setAttribute('aria-live', 'polite');
            document.querySelector('.container')?.prepend(box);
        }
        if (!box) return;
        box.replaceChildren();
        const alert = document.createElement('div');
        alert.className = `alert alert-${success ? 'success' : 'danger'}`;
        alert.textContent = message || (success ? 'Thao tác thành công.' : 'Đã xảy ra lỗi.');
        box.appendChild(alert);
    };

    const post = async (url, body) => {
        const options = { method: 'POST', headers: { Accept: 'application/json', 'X-Requested-With': 'XMLHttpRequest' } };
        const csrf = document.querySelector('meta[name="csrf-token"]')?.content ||
            document.querySelector('input[name="csrf_token"]')?.value;
        if (csrf) options.headers['X-CSRFToken'] = csrf;
        if (body) {
            options.headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(body);
        }
        const response = await fetch(url, options);
        let data;
        try { data = await response.json(); } catch (_) { throw new Error('Máy chủ trả về dữ liệu không hợp lệ.'); }
        if (!response.ok || !data.success) throw new Error(data.message || 'Không thể thực hiện thao tác.');
        return data;
    };

    const updateCartCount = count => {
        if (count === undefined || count === null) return;
        document.querySelectorAll('[data-cart-count], #cart-count, .cart-count').forEach(el => { el.textContent = count; });
    };

    const updateTotals = () => {
        let total = 0;
        document.querySelectorAll('[data-cart-row]').forEach(row => {
            const price = Number(row.dataset.price) || 0;
            const quantity = Number(row.querySelector('[name="quantity"]')?.value) || 0;
            const subtotal = price * quantity;
            total += subtotal;
            const line = row.querySelector('[data-line-subtotal]');
            if (line) line.textContent = money(subtotal);
        });
        const totalEl = document.querySelector('[data-cart-total]');
        if (totalEl) totalEl.textContent = money(total);
    };

    const saveQuantity = input => {
        const revision = (revisions.get(input) || 0) + 1;
        revisions.set(input, revision);
        const run = async () => {
            if (revisions.get(input) !== revision) return;
            const form = input.closest('form');
            const quantity = Number(input.value);
            const previous = Number(input.dataset.savedQuantity || input.defaultValue || 1);
            const max = Number(input.max);
            if (!Number.isInteger(quantity) || quantity < 1 || (max > 0 && quantity > max)) {
                input.value = previous;
                updateTotals();
                showMessage(max > 0 && quantity > max ? `Số lượng tối đa hiện có là ${max}.` : 'Số lượng phải là số nguyên lớn hơn 0.', false);
                return;
            }
            const accepted = quantity;
            input.disabled = true;
            try {
                const data = await post(form.action, { quantity: accepted });
                input.dataset.savedQuantity = String(accepted);
                input.defaultValue = String(accepted);
                updateCartCount(data.cart_count);
                if (revisions.get(input) === revision) showMessage(data.message, true);
            } catch (error) {
                if (revisions.get(input) === revision) {
                    input.value = previous;
                    showMessage(error.message, false);
                }
            } finally {
                input.disabled = false;
                updateTotals();
            }
        };
        const previousChain = saveChains.get(input) || Promise.resolve();
        const chain = previousChain.catch(() => {}).then(run);
        saveChains.set(input, chain);
        return chain;
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
            const input = form.querySelector('[name="quantity"]');
            if (input) {
                if (timers.has(input)) clearTimeout(timers.get(input));
                await saveQuantity(input);
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

    document.addEventListener('input', event => {
        const input = event.target;
        if (!input.matches('[data-cart-row] [name="quantity"]')) return;
        revisions.set(input, (revisions.get(input) || 0) + 1);
        updateTotals();
        if (timers.has(input)) clearTimeout(timers.get(input));
        timers.set(input, setTimeout(() => saveQuantity(input), 400));
    });
    document.addEventListener('change', event => {
        const input = event.target;
        if (!input.matches('[data-cart-row] [name="quantity"]')) return;
        if (timers.has(input)) clearTimeout(timers.get(input));
        saveQuantity(input);
    });
})();
