/**
 * Admin Panel JavaScript
 * MiniEcommerce-PWD301
 */
document.addEventListener('DOMContentLoaded', function () {
    // Tự động ẩn các thông báo alert flash sau 5 giây (trừ alert-danger để admin kịp đọc lỗi)
    const alerts = document.querySelectorAll('.alert:not(.alert-danger)');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            if (window.bootstrap && bootstrap.Alert) {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                if (bsAlert) {
                    bsAlert.close();
                }
            }
        }, 5000);
    });
});
