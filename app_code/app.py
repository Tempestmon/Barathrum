from flask import Flask, render_template, request
from app_code.controller.controller import Controller

app = Flask(__name__, template_folder='templates')
controller = Controller()


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/make_order', methods=['GET'])
def create_order():
    return render_template('order.html')


@app.route('/make_order/order', methods=['POST'])
def send_order():
    received_data = request.form.to_dict()
    controller.make_solutions_by_order(received_data)
    return render_template('index.html')


@app.route('/solutions', methods=['GET'])
def give_solutions():
    solutions = controller.extract_solutions_from_bd()
    return 'kek'


if __name__ == '__main__':
    app.run(debug=True)
