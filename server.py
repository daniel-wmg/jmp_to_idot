import json
import os

from flask import Flask, render_template, request, redirect, url_for, send_from_directory

import uuid
import pandas as pd
from werkzeug.utils import secure_filename

from converter import Converter

app = Flask(__name__)
app.config["UPLOAD_DIR"] = "uploads"

ALLOWED_EXTENSIONS = {'csv'}
UPLOAD_FILENAME = "input.csv"
REAGENT_FILENAME = "stocks.json"
OUTPUT_DF_FILENAME = "output.pkl"
OUTPUT_FILENAME = "output.csv"


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    else:
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            session_id = uuid.uuid4().hex
            os.mkdir(os.path.join(app.config['UPLOAD_DIR'], session_id))

            file_location = os.path.join(app.config['UPLOAD_DIR'], session_id, filename)
            new_file_name = os.path.join(app.config['UPLOAD_DIR'], session_id, UPLOAD_FILENAME)
            file.save(file_location)

            os.rename(file_location, new_file_name)

            return redirect(url_for('setup_source_plate', session_id=session_id))


@app.route("/<session_id>/step_2", methods=["GET", "POST"])
def setup_source_plate(session_id):
    if request.method == "GET":
        input_path = os.path.join(app.config['UPLOAD_DIR'], session_id, UPLOAD_FILENAME)
        conv = Converter(jmp_output=input_path, final_vol=1)
        liquids = conv.get_reagents()
        wells = conv.generate_plate_indices(96)
        well_letters = list(map(chr, range(65, 73)))
        return render_template("setup_source.html", session_id=session_id, liquids=liquids, wells=wells,
                               well_letters=well_letters)

    else:
        liquids = {}

        for item in request.form:
            liquid = item.split("_")[0]

            if liquid not in liquids.keys():
                liquids[liquid] = {"stock": 0, "location": ""}

            if "well" in item:
                if "letter" in item:
                    liquids[liquid]["location"] = request.form.get(item)

                if "number" in item:
                    liquids[liquid]["location"] += request.form.get(item)

            if "conc" in item:
                liquids[liquid]["stock"] = int(request.form.get(item))

        with open(os.path.join(app.config["UPLOAD_DIR"], session_id, REAGENT_FILENAME), "w") as f:
            json.dump(liquids, f, indent=4)

        return redirect(url_for("setup_reaction_plate", session_id=session_id))


@app.route("/<session_id>/step_3", methods=["GET", "POST"])
def setup_reaction_plate(session_id):
    if request.method == "GET":
        return render_template("setup_dest.html", session_id=session_id)

    else:
        total_vol = request.form.get("final_vol")

        conv = Converter(os.path.join(app.config['UPLOAD_DIR'], session_id, UPLOAD_FILENAME), final_vol=int(total_vol))

        stocks = {}

        with open(os.path.join(app.config["UPLOAD_DIR"], session_id, REAGENT_FILENAME), "r") as f:
            stocks = json.load(f)

        conv.set_liquid_stocks(stocks)

        output = conv.build_output()
        output.to_pickle(os.path.join(app.config['UPLOAD_DIR'], session_id, OUTPUT_DF_FILENAME))
        conv.write_output(os.path.join(app.config['UPLOAD_DIR'], session_id, OUTPUT_FILENAME), conv.build_header(),
                          output)

        return redirect(url_for("show_output", session_id=session_id))


@app.route("/<session_id>/output", methods=["GET"])
def show_output(session_id):
    df = pd.read_pickle(os.path.join(app.config['UPLOAD_DIR'], session_id, OUTPUT_DF_FILENAME))
    df_cols = df.columns.tolist()
    return render_template("output.html", session_id=session_id, df=json.loads(df.to_json(orient="records")),
                           df_cols=df_cols)


@app.route("/<session_id>/download")
def download(session_id):
    return send_from_directory(os.path.join(app.config['UPLOAD_DIR'], session_id), OUTPUT_FILENAME)
