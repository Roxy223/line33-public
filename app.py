from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "supersecretkey"  # use env var in production

# Stops (base scheduled times)
STOPS = [
    {"name":"Oosterblok","time":"17:53"},
    {"name":"Baaier","time":"17:54"},
    {"name":"BosWater","time":"17:55"},
    {"name":"De veer QD","time":"17:55"},
    {"name":"brugstraat","time":"17:56"},
    {"name":"Komerplein","time":"17:56"},
    {"name":"Oosterbrug","time":"17:57"},
    {"name":"Oostplein","time":"17:57"},
    {"name":"Rembrand CNTRL","time":"17:58"},
    {"name":"Hoogzandweg","time":"17:59"},
    {"name":"Hogezand Strand","time":"18:00"},
    {"name":"HZ WalenbW","time":"18:01"},
    {"name":"Hoogzand Centrum","time":"18:02"},
    {"name":"Zaandams weg","time":"18:03"},
    {"name":"Bosweg","time":"18:05"},
    {"name":"Bergenlaan","time":"18:06"},
    {"name":"HVBergenlaan","time":"18:07"},
    {"name":"Zaandam Centrum","time":"18:09"},
    {"name":"HVBergenlaan","time":"18:11"},
    {"name":"Bergenlaan","time":"18:12"},
    {"name":"Bosweg","time":"18:13"},
    {"name":"Zaandams Weg","time":"18:14"},
    {"name":"HoogZand Centrum","time":"18:16"},
    {"name":"HZ WalenBW","time":"18:17"},
    {"name":"Hoogzandweg","time":"18:18"},
    {"name":"Rembrand CNTRL","time":"18:19"},
    {"name":"Oostplein","time":"18:22"},
    {"name":"De veer QD","time":"18:25"},
    {"name":"BosWater","time":"18:26"},
    {"name":"Damweg","time":"18:28"},
    {"name":"Schuurplein","time":"18:29"},
    {"name":"Oosterblok","time":"18:30"},
]

def add_minutes(time_str, minutes):
    """Add minutes to HH:MM time string and return HH:MM (wraps past midnight)."""
    h, m = map(int, time_str.split(":"))
    dt = datetime(2000,1,1,h,m) + timedelta(minutes=minutes)
    return dt.strftime("%H:%M")

@app.route("/", methods=["GET", "POST"])
def index():
    # initialize session values
    if "times" not in session:
        session["times"] = [stop["time"] for stop in STOPS]
    if "delays" not in session:
        session["delays"] = [0 for _ in STOPS]

    if request.method == "POST":
        # process edits for each stop
        for i, _ in enumerate(STOPS):
            # time input (HH:MM)
            time_key = f"time_{i}"
            if time_key in request.form:
                new_time = request.form.get(time_key).strip()
                try:
                    datetime.strptime(new_time, "%H:%M")
                    session["times"][i] = new_time
                except Exception:
                    pass  # ignore invalid time formats

            # delay input (integer)
            delay_key = f"delay_{i}"
            if delay_key in request.form:
                val = request.form.get(delay_key).strip()
                try:
                    new_delay = int(float(val))  # accept numbers, e.g. "0" or "3"
                    session["delays"][i] = max(0, new_delay)
                except Exception:
                    pass

        # reset to defaults
        if "reset_all" in request.form:
            session["times"] = [stop["time"] for stop in STOPS]
            session["delays"] = [0 for _ in STOPS]

        session.modified = True
        return redirect(url_for("index"))

    # prepare stops for rendering
    stops_render = []
    for i, stop in enumerate(STOPS):
        base_time = session["times"][i]
        delay = session["delays"][i]
        updated_time = add_minutes(base_time, delay)
        stops_render.append({
            "name": stop["name"],
            "base_time": base_time,
            "delay": delay,
            "updated_time": updated_time,
            "is_delayed": delay > 0
        })

    # pass sample image path (your uploaded image) so front-end can use it if desired
    uploaded_sample = "/mnt/data/48b3c56f-2692-49b6-9e22-bf2e1af7218a.png"

    return render_template("index.html", stops=stops_render, title="33 Naar Zaandamse Weg - Oosterblok (Via: Rembrand Centraal en Zaandam Centrum)", sample_image=uploaded_sample)

if __name__ == "__main__":
    app.run(debug=True)
