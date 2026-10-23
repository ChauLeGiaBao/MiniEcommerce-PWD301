# -*- coding: utf-8 -*-
"""
Script tải và nạp ảnh thực tế cho toàn bộ sản phẩm trong MiniEcommerce:
1. Tải ảnh chất lượng cao từ CDN Unsplash vào app/static/img/products/
2. Cập nhật trường HINHANH của tất cả sản phẩm trong database SQLite (dev.db)
3. Cập nhật seed.py và seed_data.sql
"""

import os
import urllib.request
from app import create_app
from app.extensions import db
from app.models import SanPham

# Map tên sản phẩm -> (URL Unsplash, tên file local)
PRODUCT_IMAGES = {
    "Samsung Galaxy S22": (
        "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?auto=format&fit=crop&w=800&q=80",
        "samsung-galaxy-s22.jpg"
    ),
    "iPhone 14": (
        "https://images.unsplash.com/photo-1695048133142-1a20484d2569?auto=format&fit=crop&w=800&q=80",
        "iphone-14.jpg"
    ),
    "Xiaomi Redmi Note 12": (
        "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=800&q=80",
        "xiaomi-redmi-note-12.jpg"
    ),
    "Oppo Reno 8": (
        "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=800&q=80",
        "oppo-reno-8.jpg"
    ),
    "Vivo V27": (
        "https://images.unsplash.com/photo-1580910051074-3eb694886505?auto=format&fit=crop&w=800&q=80",
        "vivo-v27.jpg"
    ),

    "MacBook Air M2": (
        "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=800&q=80",
        "macbook-air-m2.jpg"
    ),
    "Dell Inspiron 15": (
        "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?auto=format&fit=crop&w=800&q=80",
        "dell-inspiron-15.jpg"
    ),
    "Asus Vivobook 14": (
        "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=800&q=80",
        "asus-vivobook-14.jpg"
    ),
    "Lenovo ThinkPad E14": (
        "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&w=800&q=80",
        "lenovo-thinkpad-e14.jpg"
    ),
    "HP Pavilion Gaming": (
        "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=800&q=80",
        "hp-pavilion-gaming.jpg"
    ),

    "Áo sơ mi nam trắng": (
        "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=800&q=80",
        "ao-so-mi-nam-trang.jpg"
    ),
    "Quần jean nam xanh": (
        "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=800&q=80",
        "quan-jean-nam-xanh.jpg"
    ),
    "Áo thun nam basic": (
        "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=800&q=80",
        "ao-thun-nam-basic.jpg"
    ),
    "Áo khoác nam bomber": (
        "https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=800&q=80",
        "ao-khoac-nam-bomber.jpg"
    ),
    "Quần short nam kaki": (
        "https://images.unsplash.com/photo-1591195853828-11db59a44f6b?auto=format&fit=crop&w=800&q=80",
        "quan-short-nam-kaki.jpg"
    ),

    "Đầm nữ công sở": (
        "https://images.unsplash.com/photo-1595777457583-95e059d581b8?auto=format&fit=crop&w=800&q=80",
        "dam-nu-cong-so.jpg"
    ),
    "Áo kiểu nữ tay phồng": (
        "https://images.unsplash.com/photo-1564257631407-4deb1f99d992?auto=format&fit=crop&w=800&q=80",
        "ao-kieu-nu-tay-phong.jpg"
    ),
    "Chân váy nữ xếp ly": (
        "https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?auto=format&fit=crop&w=800&q=80",
        "chan-vay-nu-xep-ly.jpg"
    ),
    "Áo len nữ cổ lọ": (
        "https://images.unsplash.com/photo-1576566588028-4147f3842f27?auto=format&fit=crop&w=800&q=80",
        "ao-len-nu-co-lo.jpg"
    ),
    "Quần culottes nữ": (
        "https://images.unsplash.com/photo-1509551388413-e18d0ac5d495?auto=format&fit=crop&w=800&q=80",
        "quan-culottes-nu.jpg"
    ),

    "Tai nghe Bluetooth X1": (
        "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=800&q=80",
        "tai-nghe-bluetooth-x1.jpg"
    ),
    "Sạc nhanh 20W": (
        "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?auto=format&fit=crop&w=800&q=80",
        "sac-nhanh-20w.jpg"
    ),
    "Ốp lưng iPhone 14": (
        "https://images.unsplash.com/photo-1601593346740-925612772716?auto=format&fit=crop&w=800&q=80",
        "op-lung-iphone-14.jpg"
    ),
}

def download_images(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    print(f"Downloading images to {output_dir}...")
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for product_name, (url, filename) in PRODUCT_IMAGES.items():
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            print(f"  [EXISTS] {filename}")
            continue
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response, open(filepath, "wb") as f:
                f.write(response.read())
            print(f"  [OK] {filename}")
        except Exception as e:
            print(f"  [ERROR] {filename}: {e}")

def update_database():
    app = create_app()
    with app.app_context():
        count = 0
        products = SanPham.query.all()
        for p in products:
            if p.TENSPH in PRODUCT_IMAGES:
                url, filename = PRODUCT_IMAGES[p.TENSPH]
                p.HINHANH = url
                count += 1
        db.session.commit()
        print(f"Updated HINHANH for {count} products in database.")

if __name__ == "__main__":
    static_img_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "static", "img", "products")
    download_images(static_img_dir)
    update_database()
