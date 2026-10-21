/**
 * Admin Panel JavaScript
 * MiniEcommerce-PWD301 - Long
 */
document.addEventListener('DOMContentLoaded', function () {
    // 1. Tự động ẩn các thông báo alert flash sau 5 giây (trừ alert-danger để admin kịp đọc lỗi)
    const alerts = document.querySelectorAll('.alert:not(.alert-danger)');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            if (window.bootstrap && bootstrap.Alert) {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                if (bsAlert) {
                    bsAlert.close();
                }
            } else {
                alert.style.transition = 'opacity 0.5s ease';
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 500);
            }
        }, 5000);
    });

    // 2. Chống double-submit trên các form quan trọng
    const forms = document.querySelectorAll('form');
    forms.forEach(function (form) {
        form.addEventListener('submit', function () {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.dataset.originalText = submitBtn.innerHTML;
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Đang xử lý...';
                // Khôi phục sau 8s phòng trường hợp lỗi mạng không chuyển trang
                setTimeout(function () {
                    if (submitBtn.disabled) {
                        submitBtn.disabled = false;
                        if (submitBtn.dataset.originalText) {
                            submitBtn.innerHTML = submitBtn.dataset.originalText;
                        }
                    }
                }, 8000);
            }
        });
    });
});
