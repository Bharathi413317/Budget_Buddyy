from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

# Configure Gemini API
GOOGLE_API_KEY = "AIzaSyAMQW-OPVcgh3TCE2Po_cWiwp-zuEd_1I0" # Replace with your actual key
genai.configure(api_key=GOOGLE_API_KEY)

# Create Gemini chat session
model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat(history=[])

app = Flask(__name__, template_folder='templates', static_folder='static')

investment_data = {
    "monthly_investment": 0,
    "warning_threshold": 1000
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat_response():
    user_message = request.json.get('message', '')
    user_message_lower = user_message.lower()
    response = ""

    if "investment" in user_message_lower:
        try:
            invest_amount = int("".join(filter(str.isdigit, user_message)))
            investment_data["monthly_investment"] = invest_amount
            response = f"Your monthly investment is ${invest_amount}. I will now track this for you."
        except ValueError:
            response = "Sorry, I couldn't understand the investment amount. Please specify a number."

    elif "warning" in user_message_lower and investment_data["monthly_investment"] > 0:
        warning_threshold = investment_data["warning_threshold"]
        monthly_investment = investment_data["monthly_investment"]

        if monthly_investment < warning_threshold:
            response = (
                f"<div class='warning-message'>"
                f"⚠️ Warning: Your monthly investment of ${monthly_investment} "
                f"is below the recommended threshold of ${warning_threshold}."
                f"</div>"
            )
        else:
            response = f"✅ Your monthly investment of ${monthly_investment} is on track!"

    else:
        try:
            gemini_response = chat.send_message(user_message)
            response = gemini_response.text
        except Exception as e:
            response = f"Error: {str(e)}"

    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)