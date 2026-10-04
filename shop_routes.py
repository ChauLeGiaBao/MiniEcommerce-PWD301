from flask import Blueprint, render_template, redirect, url_for, request, session, flash

# Khởi tạo Blueprint cho shop (tên biến tùy thuộc vào khung project chung)
shop_bp = Blueprint('shop', __name__, template_folder='templates')

# Dữ liệu sản phẩm mẫu tạm thời (nếu Kiên chưa gửi database, dùng danh sách này để chạy test giao diện)
PRODUCTS = [
    {"id": 1, "name": "Áo Thun Nam Basic", "price": 150000, "image": "https://via.placeholder.com/150", "desc": "Áo thun cotton thoáng mát."},
    {"id": 2, "name": "Quần Jean Slimfit", "price": 350000, "image": "https://via.placeholder.com/150", "desc": "Quần jean form đẹp, co giãn tốt."},
    {"id": 3, "name": "Giày Sneaker Thể Thao", "price": 600000, "image": "https://via.placeholder.com/150", "desc": "Giày nhẹ, êm chân, phù hợp đi học đi chơi."}
]

# 1. Trang danh sách sản phẩm (/products)
@shop_bp.route('/products')
def product_list():
    return render_template('shop/products.html', products=PRODUCTS)

# 2. Trang chi tiết sản phẩm (/products/)
@shop_bp.route('/products/')
def product_detail(product_id):
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if not product:
        flash("Không tìm thấy sản phẩm!", "danger")
        return redirect(url_for('shop.product_list'))
    return render_template('shop/detail.html', product=product)

# 3. Trang giỏ hàng (/cart)
@shop_bp.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    total_price = 0
    
    for product_id, quantity in cart.items():
        product = next((p for p in PRODUCTS if p['id'] == int(product_id)), None)
        if product:
            subtotal = product['price'] * quantity
            total_price += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
            
    return render_template('shop/cart.html', cart_items=cart_items, total_price=total_price)

# Thêm vào giỏ hàng
@shop_bp.route('/cart/add/', methods=['POST'])
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    str_id = str(product_id)
    
    # Nếu sản phẩm đã có trong giỏ thì tăng số lượng lên 1, chưa có thì gán bằng 1
    if str_id in cart:
        cart[str_id] += 1
    else:
        cart[str_id] = 1
        
    session.modified = True
    flash("Đã thêm sản phẩm vào giỏ hàng!", "success")
    return redirect(url_for('shop.view_cart'))

# Xóa sản phẩm khỏi giỏ hàng
@shop_bp.route('/cart/remove/')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    str_id = str(product_id)
    if str_id in cart:
        del cart[str_id]
        session.modified = True
        flash("Đã xóa sản phẩm khỏi giỏ hàng!", "info")
    return redirect(url_for('shop.view_cart'))

# Cập nhật số lượng sản phẩm trong giỏ hàng
@shop_bp.route('/cart/update/', methods=['POST'])
def update_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    cart = session.get('cart', {})
    str_id = str(product_id)
    
    if str_id in cart:
        if quantity > 0:
            cart[str_id] = quantity
        else:
            del cart[str_id]
        session.modified = True
        flash("Đã cập nhật giỏ hàng thành công!", "success")
        
    return redirect(url_for('shop.view_cart'))

# 4. Trang thanh toán (/checkout)
@shop_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        # Xử lý đặt hàng cơ bản (xóa session giỏ hàng sau khi đặt thành công)
        session.pop('cart', None)
        flash("Đặt hàng thành công! Cảm ơn bạn đã mua sắm.", "success")
        return redirect(url_for('shop.product_list'))
        
    return render_template('shop/checkout.html')