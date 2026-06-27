from flask import Flask, render_template, request
import csv
from difflib import get_close_matches

app = Flask(__name__)

# ---------------- HEALTH TIP SYSTEM ----------------
def get_tip(ingredient):
    ingredient = ingredient.lower()

    if "paracetamol" in ingredient:
        return "⚠️ Paracetamol: Do not exceed 3–4g per day. Overdose may damage liver."

    elif "azithromycin" in ingredient:
        return "💊 Azithromycin: Always complete full antibiotic course even if symptoms improve."

    elif "pantoprazole" in ingredient:
        return "🍽️ Pantoprazole: Take before food for better acid control."

    elif "fexofenadine" in ingredient:
        return "🤧 Fexofenadine: Non-drowsy antihistamine used for allergies."

    elif "montelukast" in ingredient:
        return "🌿 Montelukast: Used for asthma/allergy prevention. Take regularly."

    elif "omeprazole" in ingredient:
        return "🧪 Omeprazole: Long-term use only under doctor supervision."

    elif "calcium" in ingredient or "vitamin" in ingredient:
        return "💪 Calcium/Vitamin D: Supports bone health. Do not overdose."

    elif "antacid" in ingredient:
        return "🧴 Antacid: Used for quick relief from acidity."

    else:
        return "💡 Always consult a doctor before using medicines regularly."


@app.route("/", methods=["GET", "POST"])
def home():

    result = None
    monthly_data = None

    if request.method == "POST":

        brand = request.form["medicine"].strip().lower()

        ingredient = ""
        alternatives = []
        cheapest_brand = ""
        cheapest_price = 0
        saving = 0
        price = 0

        rows = []
        medicine_names = []

        with open("medicines.csv", "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)

            for row in reader:
                rows.append(row)
                medicine_names.append(row[1].lower())

        match = get_close_matches(brand, medicine_names, n=1, cutoff=0.5)

        if match:
            matched_brand = match[0]

            for row in rows:
                if row[1].lower() == matched_brand:
                    ingredient = row[2]
                    price = float(row[3])
                    brand = row[1]
                    availability = row[4] if len(row) > 4 else "unknown"
                    break

            for row in rows:
                if row[2] == ingredient:
                    alternatives.append(row)

            if alternatives:

                cheapest_row = min(alternatives, key=lambda x: float(x[3]))
                cheapest_brand = cheapest_row[1]
                cheapest_price = float(cheapest_row[3])

                saving = price - cheapest_price

                saving_percent = round((saving / price) * 100, 1) if price > 0 else 0

                # ✅ HEALTH TIP ADDED HERE
                tip = get_tip(ingredient)

                result = {
                    "brand": brand,
                    "ingredient": ingredient,
                    "price": price,
                    "alternatives": alternatives,
                    "cheapest_brand": cheapest_brand,
                    "cheapest_price": cheapest_price,
                    "saving": round(saving, 2),
                    "saving_percent": saving_percent,
                    "availability": availability,
                    "tip": tip
                }

        # MONTHLY CALCULATOR
        if request.form.get("strips") and price and cheapest_price:

            strips = int(request.form["strips"])

            current_total = price * strips
            alt_total = cheapest_price * strips

            monthly_saving = current_total - alt_total
            yearly_saving = monthly_saving * 12

            monthly_data = {
                "strips": strips,
                "current_total": round(current_total, 2),
                "alt_total": round(alt_total, 2),
                "monthly_saving": round(monthly_saving, 2),
                "yearly_saving": round(yearly_saving, 2)
            }

    return render_template("index.html", result=result, monthly_data=monthly_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)