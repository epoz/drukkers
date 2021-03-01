import os, json
from flask import Flask, jsonify, send_file
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from htmltree import *
import io

app = Flask(__name__)

DATA = None


@app.route("/main.js")
def main_js():
    return open("main.js").read()


@app.route("/data")
def data():
    if not DATA:
        fetch_data()
    return jsonify(DATA)


def fetch_data():
    global DATA
    DATA = DATA or {}

    # use creds to create a client to interact with the Google Drive API
    scope = ["https://spreadsheets.google.com/feeds"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "client_secret.json", scope
    )
    client = gspread.authorize(creds)
    ss = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/1MMBS0HXemRLqBYbdymyXvv4kxgEfIu6zh7flDMZaCpc/edit#gid=0"
    )
    meta_ws = [ws for ws in ss.worksheets() if ws.title == "Meta"][0]

    fieldnames = {}
    for i, x in enumerate(meta_ws.get("Fieldnames")[0]):
        fieldnames[i] = x.upper()
    fieldindex = {}
    for k, v in fieldnames.items():
        fieldindex[v] = k

    ws = [ws for ws in ss.worksheets() if ws.title == "ALL"][0]
    all_values = ws.get_all_values()

    # The current spreadsheet contains the data in one denormalized list,
    # but we would like to have multiple addresses per printer, which are uniquely identifief by their STCN number

    for row_i, row in enumerate(all_values):
        record = row[fieldindex.get("RECORD")]
        tmp = DATA.setdefault(record, [])
        row_data = {"ROW": [row_i]}
        for i, val in enumerate(row):
            row_data.setdefault(fieldnames.get(i, "MISC"), []).append(val)
        tmp_ll = [
            ll.split(",")
            for ll in row_data.get("LATLON", [])
            if ll and ll.find(",") > 0
        ]
        tmp_ll = [ll for ll in tmp_ll if len(ll) == 2]
        tmp_ll = [(float(lat), float(lon)) for lat, lon in tmp_ll]
        row_data["LATLON"] = tmp_ll
        for f in ("BEGIN", "END"):
            try:
                row_data[f] = [int(x) for x in row_data.get(f, [])]
            except:
                row_data[f] = []
        tmp.append(row_data)

    return DATA


@app.route("/githublogo")
def githublogo():
    return send_file(
        io.BytesIO(open("GitHub-Mark-32px.png", "rb").read()), mimetype="image/png"
    )


@app.route("/about")
def about():
    return """<h1>About this map</h1>
 
<p>The records of booksellers, printers and publishers shown on this map are from different sources. Most of them come from the Short Title Catalogue, Netherlands (STCN). All of them are curated.</p>
<p>On the one hand research by bibliographers was kept to a minimum and information on printers and publishers was taken from the title-page and colophon. On the other hand information has been incorporated from published sources such as Weller or Simoni.</p>
<p>Mistakes - or information perceived as such - have been corrected but each record that was created for this map links to the original STCN Thesaurus record. Additional information was and will be added from printed sources and archival matter.</p>
<p>The most important addition lies in the lists of publishers and printers that are added to each record. In time this will make it possible to explore networks and also to examine in detail how the world of the book evolved over time.</p>
"""


@app.route("/")
def index():
    if not DATA:
        fetch_data()

    head = Head(
        Meta(name="author", content="Etienne Posthumus"),
        Title("Early Modern Printers"),
        Link(
            href="data:image/x-icon;base64,AAABAAEAEBAAAAAAAABoBQAAFgAAACgAAAAQAAAAIAAAAAEACAAAAAAAAAEAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP//AAD8fwAA/H8AAPxjAAD/4wAA/+MAAMY/AADGPwAAxjEAAP/xAAD/8QAA4x8AAOMfAADjHwAA//8AAP//AAA=",
            rel="icon",
            type="image/x-icon",
        ),
        Link(rel="preconnect", href="https://fonts.gstatic.com"),
        Link(
            href="https://fonts.googleapis.com/css2?family=Literata&display=swap",
            rel="stylesheet",
        ),
        Link(
            rel="stylesheet",
            href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css",
            integrity="sha512-xodZBNTC5n17Xt2atTPuE1HxjVMSvLVW9ocqUKLsCC5CXdbqCmblAshOMAS6/keqq/sMZMZ19scR4PsZChSR7A==",
            crossorigin="",
        ),
        Script(
            src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js",
            integrity="sha512-XQoYMqMTK8LvdxXYG3nZ448hOEQiglfqkJs1NOQV44cWnUrBc8PkAOcXy20w0vlaXaVUearIOBhiXZ5V3ynxwA==",
            crossorigin="",
        ),
        Script(
            _async="",
            defer="",
            data_domain="bookhistory.typograaf.com",
            src="https://plausible.io/js/plausible.js",
        ),
    )
    body = Body(
        Header(
            *[
                H1(
                    "Early Modern Printers",
                    _class="banner",
                    style={"color": "#eee", "margin": "1vw 0 0 2vw"},
                ),
                Div(
                    *[
                        A(
                            Img(src="/githublogo",),
                            href="https://github.com/epoz/drukkers",
                        ),
                    ],
                    style={
                        "position": "absolute",
                        "top": "0",
                        "right": "0",
                        "padding": "10px 10px 0 0",
                    },
                ),
            ]
        ),
        Div(
            Div(
                Div(
                    Input(
                        id="input_filter",
                        type="text",
                        placeholder="Type here to Filter Names",
                        style={"width": "100%"},
                    ),
                    style={"margin-bottom": "1ch"},
                ),
                Div(
                    *[
                        Div(
                            *[
                                P(
                                    obj[0].get("NAAM", ["&middot;"])[0],
                                    style={"margin": "0", "display": "inline"},
                                ),
                                A(
                                    "STCN",
                                    href=f"https://picarta.oclc.org/psi/xslt/DB=3.11/XMLPRS=Y/PPN?PPN={obj[0].get('RECORD', '_')[0]}",
                                    style={
                                        "text-decoration": "none",
                                        "color": "#ddd",
                                        "font-size": "75%",
                                        "margin-left": "4ch",
                                    },
                                    target="_STCN",
                                ),
                            ],
                            style={"margin": "0", "cursor": "pointer"},
                        )
                        for obj in sorted(
                            DATA.values(), key=lambda x: x[0].get("NAAM", [""])[0]
                        )
                    ],
                    id="printer_names",
                ),
                style={
                    "color": "#ccc",
                    "height": "90vh",
                    "overflow-y": "scroll",
                    "width": "30vw",
                },
            ),
            Div(
                Div(
                    Span("Begin 1450", id="span_begin"),
                    Input(
                        type="range",
                        min="1450",
                        max="1800",
                        value="1500",
                        id="slider_begin",
                        _class="dateslider",
                    ),
                    Span("End 1800", id="span_end", style={"margin-left": "1ch"}),
                    Input(
                        type="range",
                        min="1450",
                        max="1800",
                        value="1800",
                        id="slider_end",
                        _class="dateslider",
                    ),
                    style={
                        "margin-bottom": "0.5vw",
                        "text-align": "right",
                        "color": "#eee",
                    },
                ),
                Div(
                    id="mapid",
                    style={
                        "height": "88vh",
                        "width": "100%",
                        "border": "1px solid black",
                    },
                ),
                style={"height": "90vh", "width": "65vw"},
            ),
            style={"display": "flex", "margin": "1vw 0 0 2vw",},
        ),
        style={"background-color": "#444", "font-family": "'Literata', serif",},
    )

    indivs = []
    for obj in DATA.values():
        for addr in obj:
            continue
            bla = """<h3>%s</h3><p>%s-%s</p><p>%s</p>""" % (
                addr["NAAM"][0],
                addr["BEGIN"][0],
                addr["EIND"][0],
                addr["STRAAT"][0],
            )
            tmp = """L.marker([%s]).addTo(mymap).bindPopup("%s");""" % (
                addr["LATLON"][0],
                bla,
            )
            indivs.append(tmp)
    doc = Html(
        head,
        body,
        Script("DATA = %s" % json.dumps(DATA)),
        Script(open("main.js").read()),
    )

    return doc.render()


def make_md_from_ss(destination):
    "For the given [data] create a Markdown file for each printer with the basics in folder [destination]"
    if not DATA:
        fetch_data()

    normalized = {}
    for obj in DATA.values():
        for addr in obj:
            RECORD = addr.get("RECORD")[0]
            tmp = normalized.setdefault(RECORD, {})
            tmp["naam"] = addr.get("NAAM")
            tmp["plaats"] = addr.get("PLAATS")
            if (
                addr.get("STRAAT")
                and addr.get("STRAAT")[0]
                and addr.get("STRAAT")[0] != "geen"
            ):
                tmpA = {
                    "begin": addr.get("BEGIN", [""]),
                    "end": addr.get("END", [""]),
                    "straat": addr.get("STRAAT"),
                    "latlon": addr.get("LATLON"),
                }
                tmp.setdefault("addressen", []).append(tmpA)

    for k, v in normalized.items():
        with open(os.path.join(destination, "markdown", f"{k}.md"), "w") as F:
            F.write(f"# {v['naam'][0]}\n\n## {v['plaats'][0]}\n\n")
            for a in v.get("addressen", []):
                aaa = {}
                for aa in "begin end straat".split(" "):
                    aaa[aa] = [""]
                    if aa in a:
                        aa_val = a.get(aa)
                        if aa_val:
                            aaa[aa] = aa_val

                F.write(f"{aaa['begin'][0]} - {aaa['end'][0]}  {aaa['straat'][0]}  ")
                ll = a.get("latlon")
                if ll:
                    ll = ll[0]
                    F.write(
                        f"[map](https://www.openstreetmap.org/#map=16/{ll[0]}/{ll[1]})\n\n"
                    )
        mdfile = os.path.join(destination, "markdown", f"{k}.md")
        outfile = os.path.join(destination, "html", f"{k}")
        os.system(f"pandoc -o {outfile}.html {mdfile}")
        outfile = os.path.join(destination, "doc", f"{k}")
        os.system(f"pandoc -o {outfile}.docx {mdfile}")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
