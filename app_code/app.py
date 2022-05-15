import os
from os.path import dirname, join

from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, url_for, redirect, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from app_code.controller.controller import Controller

app = Flask(__name__, template_folder='templates', static_folder='static')
controller = Controller()
dotenv_path = join(dirname(__file__), 'config.env')
load_dotenv(dotenv_path)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

login_manager = LoginManager()
login_manager.init_app(app)

# TODO: Сделать создание решений не сразу после создания заказа, а при просмотре заказов
# TODO: Сделать удаление заказа


@login_manager.user_loader
def load_user(user_id: str):
    return controller.get_user_by_id(user_id)


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/make_order', methods=['GET'])
@login_required
def create_order():
    return render_template('order.html')


@app.route('/make_order/order', methods=['POST'])
@login_required
def send_order():
    received_data = request.form.to_dict()
    # TODO: сначала сделать просто заказ. Решения создавать после запроса пользователя, а не сразу
    controller.create_order(current_user, received_data)
    return redirect(url_for('root'))


@app.route('/solutions/<order_id>', methods=['GET'])
@login_required
def give_solutions(order_id):
    controller.make_solutions_by_order(current_user, order_id)
    solutions = controller.extract_solutions_from_bd(order_id)
    if not solutions:
        flash('К сожалению, мы не смогли составить решения из-за высокой нагрузки на систему')
    return render_template('solutions.html', order_id=order_id, solutions=solutions)


@app.route('/solutions/<order_id>/<solution_id>', methods=['GET'])
@login_required
def confirm_solution(order_id, solution_id):
    controller.confirm_solution(current_user, order_id, solution_id)
    return redirect(url_for('show_orders'))


@app.route('/orders/<order_id>/agreement', methods=['GET'])
@login_required
def show_agreement(order_id):
    agreement = controller.create_agreement(current_user, order_id)
    return render_template('agreement.html', order_id=order_id, agreement=agreement)


@app.route('/orders/<order_id>/agreement/confirm', methods=['GET'])
@login_required
def confirm_agreement(order_id):
    controller.confirm_agreement(current_user, order_id)
    return redirect(url_for('show_orders'))


@app.route('/orders/<order_id>/payments', methods=['GET'])
@login_required
def show_payments(order_id):
    payments = controller.show_payments(current_user, order_id)
    return render_template('payments.html', order_id=order_id, payments=payments)


@app.route('/orders/<order_id>/payments/confirm', methods=['GET'])
@login_required
def confirm_payments(order_id):
    controller.confirm_payments(current_user, order_id)
    return redirect(url_for('show_orders'))


@app.route('/orders/<order_id>/done', methods=['GET'])
@login_required
def close_order(order_id):
    controller.accomplish_order(current_user, order_id)
    return redirect(url_for('show_orders'))


@app.route('/login', methods=['GET', 'POST'])
def login_form():
    if request.method == 'POST':
        try:
            customer = controller.login_user(request.form.to_dict())
            login_user(customer)
        except Exception:
            flash('Аккаунта с такой почтой и паролем не существует')
            return redirect(url_for('login_form'))
        return redirect(url_for('root'))
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if not controller.sign_up_user(request.form.to_dict()):
            flash('Аккаунт с такой почтой или телефоном уже зарегистрирован')
            return redirect(url_for('signup'))
    return redirect(url_for('root'))


@app.route('/orders', methods=['GET'])
@login_required
def show_orders():
    orders = controller.get_orders_by_user(current_user)
    return render_template('orders.html', orders=orders)


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('root'))


if __name__ == '__main__':
    app.run(debug=True)
