from flask import Flask, render_template, request, send_file
import os
import webbrowser
from threading import Timer
from sql_converter import convert_sql_to_snowflake

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    print("Received conversion request")  # Debug print
    if 'file' not in request.files:
        print("No file part in the request")  # Debug print
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        print("No selected file")  # Debug print
        return 'No selected file', 400
    if file:
        print(f"Processing file: {file.filename}")  # Debug print
        input_content = file.read().decode('utf-8')
        converted_content = convert_sql_to_snowflake(input_content)
        output_filename = 'converted_' + file.filename
        with open(output_filename, 'w') as f:
            f.write(converted_content)
        print(f"Conversion complete. Output file: {output_filename}")  # Debug print
        return send_file(output_filename, as_attachment=True)

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(debug=True, use_reloader=False)