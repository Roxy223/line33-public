from flask import Flask, render_template

app = Flask(__name__)

# Your index route
@app.route("/")
def index():
    stops_render = ["Stop A", "Stop B", "Stop C"]  # example stops
    uploaded_sample = "sample.png"  # example image path

    routes = {
        "1": {"title": "33 Naar Zaandamse Weg", "stops": ["Stop A", "Stop B"]},
        "2": {"title": "Route 2", "stops": ["Stop C", "Stop D"]},
    }

    return render_template(
        "index.html",
        stops=stops_render,
        routes=routes,  # this is crucial
        title="33 Naar Zaandamse Weg - Oosterblok (Via: Rembrand Centraal en Zaandam Centrum)",
        sample_image=uploaded_sample
    )

if __name__ == "__main__":
    app.run(debug=True)
