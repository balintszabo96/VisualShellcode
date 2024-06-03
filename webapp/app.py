from flask import Flask, render_template, request
from utils.logic import get_disasm

app = Flask(__name__)

def process(input_text):
    # Here, you can process the input text in any way you like.
    # For simplicity, let's just reverse the text.
    #return input_text.replace(' ', '')
    disasm = get_disasm(input_text.replace(' ', '')).split('\n')
    return disasm

@app.route('/', methods=['GET', 'POST'])
def index():
    processed_text = ""
    if request.method == 'POST':
        submitted_text = request.form['text_input']
        processed_text = process(submitted_text)
    return render_template('index.html', processed_text=processed_text)

if __name__ == '__main__':
    app.run(debug=True)
