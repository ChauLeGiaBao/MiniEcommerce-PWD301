import os
import subprocess
import sys
import time
from PIL import Image

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUT_DIR = r"D:\FPT\Kì 5\PWD301\MiniEcommerce-PWD301\docs\screenshots"

TARGETS = [
    {
        "url": "http://127.0.0.1:5000/products",
        "png": os.path.join(OUT_DIR, "real_01.png"),
        "jpg": os.path.join(OUT_DIR, "01_product_catalog.jpg"),
        "label": "Trang Danh Sách & Tìm Kiếm Sản Phẩm",
    },
    {
        "url": "http://127.0.0.1:5000/auth/dev-screenshot-helper?role=customer&page=cart",
        "png": os.path.join(OUT_DIR, "real_02.png"),
        "jpg": os.path.join(OUT_DIR, "02_cart_checkout.jpg"),
        "label": "Trang Giỏ Hàng & Thanh Toán",
    },
    {
        "url": "http://127.0.0.1:5000/auth/dev-screenshot-helper?role=admin&page=admin",
        "png": os.path.join(OUT_DIR, "real_03.png"),
        "jpg": os.path.join(OUT_DIR, "03_admin_dashboard.jpg"),
        "label": "Trang Admin Dashboard & Thống Kê",
    },
    {
        "url": "http://127.0.0.1:5000/auth/dev-screenshot-helper?role=customer&page=product",
        "png": os.path.join(OUT_DIR, "real_04.png"),
        "jpg": os.path.join(OUT_DIR, "04_product_reviews.jpg"),
        "label": "Trang Chi Tiết Sản Phẩm & Đánh Giá",
    },
]

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for target in TARGETS:
        print(f"Capturing: {target['label']} -> {target['url']}")
        cmd = [
            CHROME_PATH,
            "--headless=new",
            f"--screenshot={target['png']}",
            "--window-size=1400,900",
            "--disable-gpu",
            "--hide-scrollbars",
            target["url"],
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        print(f"Chrome exit code: {res.returncode}")
        time.sleep(1)

        if os.path.exists(target["png"]):
            # Convert PNG to high quality JPG
            img = Image.open(target["png"])
            rgb_img = img.convert("RGB")
            rgb_img.save(target["jpg"], "JPEG", quality=95)
            print(f"Saved JPG: {target['jpg']} ({os.path.getsize(target['jpg'])} bytes)")
            # Clean up temp png
            try:
                os.remove(target["png"])
            except OSError:
                pass
        else:
            print(f"FAILED to capture {target['png']}")

if __name__ == "__main__":
    main()
