from flask import Flask, request, render_template
from flask_cors import CORS
from ElEx import *

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/how_to_use')
def how_to_use():
    return render_template("how_to_use.html")

@app.route('/theoretical_background')
def theoretical_background():
    return render_template("theoretical_background.html")

@app.route('/tableau', methods=['POST'])
def tableau():
    if request.method == 'POST':
        data = request.get_json()  # Get data posted as a json
        axioms = data['axioms']
        to_prove = data['to_prove']
        tableau,counter_examples = solver(axioms,to_prove)
        to_return = {'tableau':tableau,
                     'counter_examples':counter_examples}
        return to_return


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
