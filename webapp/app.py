from flask import Flask, render_template, request
from utils.logic import get_disasm, get_emulation
from utils.instruction import Flag

app = Flask(__name__)

def process(input_text, architecture):
    preprocessed_text = input_text.replace(' ', '')
    instructions = get_disasm(preprocessed_text, architecture)
    emulation = get_emulation(preprocessed_text, architecture)
    address_flags = emulation.split(';')[:-1]
    flagId = 0
    for address_flag in address_flags:
        address = int(address_flag.split(',')[0])
        flag = address_flag.split(',')[1]
        for instruction in instructions:
            if instruction.address_num == address:
                instruction.flags.append(Flag(flagId, flag))
        flagId = flagId + 1
    return instructions

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
