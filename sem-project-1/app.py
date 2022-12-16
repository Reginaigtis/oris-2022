from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from my_database import DataBase, UserLogin

app = Flask(__name__)
app.config['SECRET_KEY'] = '22d6g4kgc3f8ade0fr65d4bf1rms4e56c549380da3e7'
login_manager = LoginManager(app)
login_manager.login_view = 'register_page'
db = DataBase()


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, db)


@app.route('/')
def hello_world():
    return redirect(url_for('main_page'))


@app.route('/main_page')
def main_page():
    categories = ['Sweater', 'Hoodie', 'Pants', 'Jeans', 'Accessories', 'Shoes', 'T-shirt', 'Longsleeve',
                  'Jacket',
                  'Coat', 'Underwear', 'Skirt', 'Dress', 'Swimming', 'Other']
    genders = ['male', 'female']
    sort_params = (['Sort by price (low->high)', 'cost'],
                   ['Sort by name (low->high)', 'title'],
                   ['Sort by price (high->low)', 'cost desc'],
                   ['Sort by name (high->low)', 'title desc'])
    sort_parameter = request.args.get('sort_parameter')
    gender_parameter = [request.args.get('gender_parameter')]
    if gender_parameter[0] is None:
        gender_parameter = genders
    category_parameter = [request.args.get('category_parameter')]
    if category_parameter[0] is None:
        category_parameter = categories
    products = db.get_all_products(gender_parameter, category_parameter, sort_parameter)
    products = [(*product, db.is_product_favourite(product[-1])) for product in products]
    context = {
        'title': 'Remova store',
        'categories': categories,
        'products': products,
        'genders': genders,
        'sort_params': sort_params
    }
    return render_template('main_page.html', **context)


@app.route('/product/<int:id>')
def product(id):
    product = db.get_product_by_id(id)
    product = list(product)
    product.append(db.is_product_favourite(id))
    context = {
        'product': tuple(product),
    }

    return render_template('product.html', **context)


@app.route('/random_product')
def get_random_product():
    product = db.get_random_product()
    product = list(product)
    product.append(db.is_product_favourite(product[-1]))
    context = {
        'product': tuple(product),
    }
    return render_template('random_product.html', **context)


@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    is_admin = current_user.is_admin
    if is_admin:
        if request.method == 'POST':
            title = request.form.get('title')
            desc = request.form.get('description')
            gen = request.form.get('gender')
            cat = request.form.get('category')
            cost = request.form.get('cost')
            img_url = request.form.get('img_url')

            db.add_product(title, desc, gen, cat, cost, img_url)

            return redirect(url_for('main_page'))
        else:
            categories = ('Sweater', 'Hoodie', 'Pants', 'Jeans', 'Accessories', 'Shoes', 'T-shirt', 'Longsleeve',
                          'Jacket',
                          'Coat', 'Underwear', 'Skirt', 'Dress', 'Swimming', 'Other')
            context = {
                'categories': categories,
            }
            return render_template('add_product.html', **context)


@app.route('/product/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    is_admin = current_user.is_admin
    if is_admin:
        if request.method == 'POST':
            title = request.form.get('title')
            desc = request.form.get('description')
            gen = request.form.get('gender')
            cat = request.form.get('category')
            cost = request.form.get('cost')
            img_url = request.form.get('img_url')

            db.edit_product(title, desc, gen, cat, cost, img_url, id)

            return redirect(url_for('product', id=id))

        product = db.get_product_by_id(id)
        categories = ('Sweater', 'Hoodie', 'Pants', 'Jeans', 'Accessories', 'Shoes', 'T-shirt', 'Longsleeve',
                      'Jacket',
                      'Coat', 'Underwear', 'Skirt', 'Dress', 'Swimming', 'Other')
        context = {
            'product': product,
            'categories': categories
        }

        return render_template('edit_product.html', **context)


@app.route('/product/<int:id>/delete')
@login_required
def delete_product(id):
    if current_user.is_admin:
        db.delete_product_by_id(id)
        return redirect(url_for('main_page'))
    return redirect(url_for('product', id=id))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile_page():
    if request.method == 'POST':
        new_first_name = request.form.get('first_name')
        new_last_name = request.form.get('last_name')
        db.update_names(current_user.get_id(), new_first_name, new_last_name)
    user = db.get_user_by_id(current_user.get_id())
    context = {
        'title': 'Profile',
        'first_name': user[1],
        'last_name': user[2],
        'email': user[3],
        'phone_num': user[4],
    }
    return render_template('profile_page.html', **context)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main_page'))


@app.route('/cart')
@login_required
def cart_page():
    products, total = db.get_cart_with_total(current_user.get_id())
    context = {
        'title': 'Cart',
        'products': products,
        'total': total
    }
    return render_template('cart_page.html', **context)


@app.route('/cart/order_confirmation')
@login_required
def order_confirmation():
    products, total = db.get_cart_with_total(current_user.get_id())
    context = {
        'title': 'Cart',
        'products': products,
        'total': total
    }
    if not products:
        return redirect(url_for('main_page'))
    return render_template('confirmation_page.html', **context)


@app.route('/product/<int:product_id>/add_to_cart')
@login_required
def add_to_cart(product_id):
    db.add_to_cart(current_user.get_id(), product_id)
    url_from = request.args.get('url_from')
    return redirect(url_from)


@app.route('/product/<int:product_id>/delete_from_cart')
@login_required
def delete_from_cart(product_id):
    db.delete_from_cart(current_user.get_id(), product_id)
    url_from = request.args.get('url_from')
    return redirect(url_from)


@app.route('/orders')
@login_required
def orders_page():
    context = {
        'title': 'Orders',
        'orders': db.get_all_orders(current_user.get_id())
    }
    return render_template('orders_page.html', **context)


@app.route('/orders/create_order')
@login_required
def create_order():
    db.create_order(current_user.get_id())
    db.clear_cart(current_user.get_id())
    return redirect(url_for('orders_page'))


@app.route('/favourite')
@login_required
def favourite_page():
    context = {
        'title': 'Favourite',
        'products': db.get_all_favourites(current_user.get_id())
    }
    return render_template('favourite_page.html', **context)


@app.route('/product/<int:product_id>/add_to_favourite')
@login_required
def add_to_favourite(product_id):
    db.add_to_favourite(current_user.get_id(), product_id)
    url_from = request.args.get('url_from')
    return redirect(url_from)


@app.route('/product/<int:product_id>/delete_from_favourite')
@login_required
def delete_from_favourite(product_id):
    db.delete_from_favourite(current_user.get_id(), product_id)
    url_from = request.args.get('url_from')
    return redirect(url_from)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone_num = request.form.get('phone_num')
        password = request.form.get('password')
        if db.check_user_email_phone(email, phone_num):
            print('Have user with this data')
        else:
            db.register_user(first_name, last_name, email, phone_num, password)
            user = db.get_user_by_email(email)
            user_login = UserLogin().create(user)
            login_user(user_login, remember=True)
            return redirect('main_page')

    context = {
        'title': 'Register'
    }
    return render_template('register_page.html', **context)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form.get('email')
        phone_num = request.form.get('phone_num')
        password = request.form.get('password')
        user = db.get_user_by_email(email)
        if user and user[4] == phone_num and user[5] == password:
            user_login = UserLogin().create(user)
            login_user(user_login, remember=True)
            return redirect('main_page')
        else:
            print("Wrong password/email/phone")

    context = {
        'title': 'Log In'
    }
    return render_template('login_page.html', **context)




if __name__ == '__main__':
    app.run()
