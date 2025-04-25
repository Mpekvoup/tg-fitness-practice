from flask import Flask, render_template, request, redirect, url_for, jsonify
from database import get_bookings, init_db, delete_booking, add_booking

app = Flask(__name__)

init_db()

@app.route("/")
def bookings():
    data = get_bookings()
    return render_template("bookings.html", bookings=data)

@app.route("/delete/<int:booking_id>", methods=["POST"])
def delete(booking_id):
    delete_booking(booking_id)
    return redirect(url_for("bookings"))

@app.route("/booking", methods=["POST"])
def add_new_booking():
    data = request.json
    add_booking(
        data["name"],
        data["phone"],
        data["trainer"],
        data["workout"],
        data["date"],
        data["time"],
        data["gym"],
    )
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)