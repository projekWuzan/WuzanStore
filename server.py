from flask import Flask, request, jsonify, session, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_mail import Mail, Message
import os

app = Flask(__name__, static_folder='publik')  
app.secret_key = 'your_secret_key'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wuzanstore.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Konfigurasi Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'wucayuxan14@gmail.com'  
app.config['MAIL_PASSWORD'] = 'onnd gwkw yton jfes'  
app.config['MAIL_DEFAULT_SENDER'] = 'wucayuxan14@gmail.com'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)
mail = Mail(app)

# Model untuk pengguna
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# Model untuk pesanan
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    buyer = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    product = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User', backref=db.backref('orders', lazy=True))

# Inisialisasi database
with app.app_context():
    db.create_all()

# Route untuk login page
@app.route('/login')
def login_page():
    return send_from_directory(os.path.join(app.root_path, 'publik'), 'login.html')

# Route untuk register page
@app.route('/register')
def register_page():
    return send_from_directory(os.path.join(app.root_path, 'publik'), 'register.html')

# Route untuk index page (Webstore page)
@app.route('/')
def index_page():
    return send_from_directory(os.path.join(app.root_path, 'publik'), 'index.html')

# Route Register
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('username')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email sudah digunakan!"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Registrasi berhasil! Silakan login."}), 200

# Route Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"message": "Email atau password salah!"}), 401

    session['user_id'] = user.id
    return jsonify({"message": "Login berhasil!"}), 200

# Route untuk memeriksa status login
@app.route('/user', methods=['GET'])
def get_user_info():
    if 'user_id' not in session:
        return jsonify({"message": "Harus login terlebih dahulu!"}), 401
    
    user = User.query.get(session['user_id'])
    return jsonify({"message": "User logged in", "email": user.email}), 200

# Route untuk logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logout berhasil!"}), 200

# Route untuk menerima formulir kontak dan mengirim email
@app.route('/contact', methods=['POST'])
def contact():
    data = request.get_json()  
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    if not name or not email or not message:
        return jsonify({"message": "Semua field wajib diisi!"}), 400

    try:
        msg = Message(
            subject="Pesan Baru dari Formulir Kontak",
            recipients=['wucayuxan14@gmail.com'],  
            body=f"Nama: {name}\nEmail: {email}\n\nPesan:\n{message}"
        )
        mail.send(msg)

        return jsonify({"message": "Pesan berhasil dikirim!"}), 200
    except Exception as e:
        return jsonify({"message": f"Gagal mengirim pesan: {str(e)}"}), 500

# Route untuk membuat pesanan
@app.route('/api/orders', methods=['POST'])
def create_order():
    if 'user_id' not in session:
        return jsonify({"message": "Harus login terlebih dahulu!"}), 401
    
    data = request.get_json()
    buyer = data.get('buyer')
    phone = data.get('phone')
    address = data.get('address')
    product = data.get('product')
    price = data.get('price')
    payment_method = data.get('paymentMethod')

    if not buyer or not phone or not address or not product or not price or not payment_method:
        return jsonify({"message": "Semua field wajib diisi!"}), 400
    
    user = User.query.get(session['user_id'])

    new_order = Order(
        user_id=user.id,
        buyer=buyer,
        phone=phone,
        address=address,
        product=product,
        price=price,
        payment_method=payment_method
    )
    db.session.add(new_order)
    db.session.commit()

    return jsonify({"message": "Pesanan berhasil dibuat!"}), 201

# Route untuk mengambil pesanan pengguna
@app.route('/api/orders', methods=['GET'])
def get_orders():
    if 'user_id' not in session:
        return jsonify({"message": "Harus login terlebih dahulu!"}), 401
    
    user = User.query.get(session['user_id'])
    
    # Ambil pesanan dari database yang terkait dengan pengguna
    orders = Order.query.filter_by(user_id=user.id).all()
    
    order_list = []
    for order in orders:
        order_data = {
            'id': order.id,  # Menambahkan ID untuk membatalkan pesanan
            'buyer': order.buyer,
            'phone': order.phone,
            'address': order.address,
            'product': order.product,
            'price': order.price,
            'paymentMethod': order.payment_method
        }
        order_list.append(order_data)
    
    return jsonify({"orders": order_list}), 200

# Route untuk membatalkan pesanan
@app.route('/api/orders/<int:order_id>', methods=['DELETE'])
def cancel_order(order_id):
    if 'user_id' not in session:
        return jsonify({"message": "Harus login terlebih dahulu!"}), 401
    
    user = User.query.get(session['user_id'])
    order = Order.query.filter_by(id=order_id, user_id=user.id).first()
    
    if not order:
        return jsonify({"message": "Pesanan tidak ditemukan!"}), 404

    db.session.delete(order)
    db.session.commit()

    return jsonify({"message": "Pesanan berhasil dibatalkan!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
    
    


