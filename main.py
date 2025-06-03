from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

app = Flask(__name__)
CORS(app)

# Set up Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

# Open your Google Sheet by name
sheet = client.open("airport").sheet1  # Ensure the sheet exists

@app.route("/submit-airport-form", methods=["POST"])
def submit_form():
    data = request.get_json()

    # Extract data from request
    name = data.get("name")
    employee_code = data.get("employeeCode")
    return_ticket_pnr = data.get("returnTicketPNR")
    airport_name = data.get("airportName")
    flight_timings = data.get("flightTimings")
    goodies_received = data.get("goodiesReceived")
    signature_base64 = data.get("signature")

    # Optional: Save the signature as an image file
    if signature_base64:
        try:
            signature_data = base64.b64decode(signature_base64.split(",")[1])
            with open(f"signatures/{employee_code}_signature.png", "wb") as f:
                f.write(signature_data)
        except Exception as e:
            print("Error saving signature image:", e)

    # Append row to Google Sheet
    sheet.append_row([
        name,
        employee_code,
        return_ticket_pnr,
        airport_name,
        flight_timings,
        goodies_received,
        "Uploaded"
    ])

    return jsonify({"message": "Form data saved successfully"}), 200

if __name__ == "__main__":
    # Create directory for storing signatures if it doesn't exist
    os.makedirs("signatures", exist_ok=True)
    app.run(debug=True)
