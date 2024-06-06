from flask import Flask, render_template, request
from utils.logic import get_disasm, get_emulation
from utils.flag import Flag

app = Flask(__name__)

def process(input_text, architecture):
    preprocessed_text = input_text.replace(' ', '')
    instructions = get_disasm(preprocessed_text, architecture)
    flags, passed_instructions = get_emulation(preprocessed_text, architecture)
    return instructions, flags, passed_instructions

@app.route('/', methods=['GET', 'POST'])
def index():
    instructions = ""
    flags = ""
    submitted_text = ""
    passed_instructions = ""
    if request.method == 'POST':
        submitted_text = request.form['text_input']
        architecture = request.form['architecture']
        instructions, flags, passed_instructions = process(submitted_text, architecture)
    return render_template('index.html', submitted_text=submitted_text, instructions=instructions, flags=flags, passed_instructions=passed_instructions)

if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host='192.168.100.66', port=5000, debug=True)
