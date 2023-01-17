import json
import os
from flask import Flask, request, render_template, send_from_directory, session
import pandas as pd

app = Flask(__name__)
app.secret_key = "super secret key"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def convert_file():
    if 'file' not in request.files:
        return "No file found"

    file = request.files['file']
    if file.filename == '':
        return "No selected file"

    if file and file.filename.endswith('.json'):
        # parse the json file
        json_data = json.loads(file.read())
        # extract the data
        data = []
        for placemark in json_data["kml"]["Document"]["Folder"]["Placemark"]:
            try:
                name = placemark["name"]
            except:
                name = "NOT FILLED"
            try:
                timestamp = placemark["TimeStamp"]["when"]
            except:
                timestamp = "NOT FILLED"
            try:
                cdata = placemark["ExtendedData"]["SchemaData"]["SimpleData"]["__cdata"]
            except:
                cdata = "NOT FILLED"
            try:
                coords = placemark["Point"]
            except:
                coords = "NOT FILLED"
            data.append({'Picture name': name, 'Picture taken:': timestamp, 'Picture names':cdata, '[Long,Lat] Point':coords})

       
        # convert the data to a Pandas DataFrame
        df = pd.DataFrame(data)
        session['df'] = df.to_dict()
        return render_template('table.html',  tables=[df.to_html(classes='data')], titles=df.columns.values)
    return "Invalid file type. Please upload a JSON file."

@app.route("/download", methods=['POST'])
def download():
    df = pd.DataFrame(session['df'])
    df.to_excel("data.xlsx", index=False)
    return send_from_directory(os.getcwd(), 'data.xlsx', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
