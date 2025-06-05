from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

app = Flask(__name__)
CORS(app)

# Set up Google Sheets API from base64-encoded environment variable
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Read and decode the base64-encoded creds
encoded_creds = os.getenv("GOOGLE_CREDS_BASE64")

if not encoded_creds:
    raise RuntimeError("GOOGLE_CREDS_BASE64 environment variable not set.")

# Decode and parse the credentials
creds_json = base64.b64decode(encoded_creds).decode("utf-8")
creds_dict = json.loads(creds_json)

# Use the credentials
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Open your Google Sheet
sheet = client.open("airport").sheet1  # Ensure the sheet exists

@app.route("/submit-airport-form", methods=["POST"])
def submit_form():
    data = request.get_json()

    name = data.get("name")
    employee_code = data.get("employeeCode")
    return_ticket_pnr = data.get("returnTicketPNR")
    airport_name = data.get("airportName")
    flight_timings = data.get("flightTimings")
    goodies_received = data.get("goodiesReceived")
    signature_base64 = data.get("signature")

    # Optional: Save signature image
    if signature_base64:
        try:
            os.makedirs("signatures", exist_ok=True)
            signature_data = base64.b64decode(signature_base64.split(",")[1])
            with open(f"signatures/{employee_code}_signature.png", "wb") as f:
                f.write(signature_data)
        except Exception as e:
            print("Error saving signature image:", e)

    # Append row to Google Sheet
    if employee_code not in sheet.col_values(2) :
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
    else:
        return jsonify({"message": "Data already exists for this employee code."}), 200
   

if __name__ == "__main__":
    app.run(debug=True)
