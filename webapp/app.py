from flask import Flask, render_template, request
import sys
import requests
from utils.PluginManager import PluginManager

app = Flask(__name__)
manager = PluginManager()

def process(input_text, architecture):
    preprocessed_text = input_text.replace(' ', '')
    pluginResults = manager.runPlugins(preprocessed_text, architecture)
    return pluginResults

@app.route('/', methods=['GET', 'POST'])
def index():
    submitted_text = ""
    pluginResults = ""
    if request.method == 'POST':
        submitted_text = request.form['text_input']
        architecture = request.form['architecture']
        if manager.is32BitPython() and architecture == "x64":
            response = requests.post("http://localhost:5000", data={'text_input': submitted_text, 'architecture': architecture})
            return response.text
        elif not manager.is32BitPython() and architecture == "x86":
            response = requests.post("http://localhost:5001", data={'text_input': submitted_text, 'architecture': architecture})
            return response.text
        pluginResults = process(submitted_text, architecture)
    return render_template('index.html', 
                           submitted_text=submitted_text, 
                           pluginResults=pluginResults,
                           plugins_to_include = manager.getHtmlFiles())

if __name__ == '__main__':
    manager.loadPlugins(sys.argv[1])
    if manager.is32BitPython():
        app.run(debug=True, port=5001)
    else:
        app.run(debug=True, port=5000)
    #app.run(host='192.168.100.66', port=5000, debug=True)
