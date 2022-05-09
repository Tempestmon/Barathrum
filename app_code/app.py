import os
from os.path import dirname, join
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from app_code.controller.controller import Controller

app = Flask(__name__, template_folder='templates')
controller = Controller()
dotenv_path = join(dirname(__file__), 'config.env')
load_dotenv(dotenv_path)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

login_manager = LoginManager()
login_manager.init_app(app)


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
    controller.make_solutions_by_order(received_data)
    return render_template('index.html')


@app.route('/solutions', methods=['GET'])
@login_required
def give_solutions():
    solutions = controller.extract_solutions_from_bd()
    return 'kek'


@app.route('/login', methods=['GET', 'POST'])
def login_form():
    if request.method == 'POST':
        try:
            customer = controller.login_user(request.form.to_dict())
            login_user(customer)
        except Exception:
            flash('Аккаунта с такой почтой и паролем не существует')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if not controller.sign_up_user(request.form.to_dict()):
            flash('Аккаунт с такой почтой уже зарегистрирован')
    return render_template('login.html')


@app.route('/orders', methods=['GET'])
@login_required
def show_orders():
    return render_template('index.html')


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
