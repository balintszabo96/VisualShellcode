from flask import Flask, render_template, request
from utils.logic import get_disasm

app = Flask(__name__)

def process(input_text, architecture):
    disasm = get_disasm(input_text.replace(' ', ''), architecture).split('\n')
    return disasm

@app.route('/', methods=['GET', 'POST'])
def index():
    processed_text = ""
    submitted_text = ""
    if request.method == 'POST':
        submitted_text = request.form['text_input']
        architecture = request.form['architecture']
        processed_text = process(submitted_text, architecture)
    return render_template('index.html', submitted_text=submitted_text, processed_text=processed_text)

if __name__ == '__main__':
    app.run(debug=True)
