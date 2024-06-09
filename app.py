from flask import Flask, request, jsonify 
import json

app = Flask(__name__)

# Load menu structure from JSON file
with open('menu_structure.json', 'r', encoding="utf-8") as file:
    menu_structure = json.load(file)

MENU_STATE = 'menu'
# Initialize current state
current_state = "menu"

@app.route('/')
def home():
    return "Welcome to the Chatbot API! Use the /chatbot endpoint to interact with the bot."

@app.route('/chatbot', methods=['POST'])
def chatbot():
    global current_state
    user_choice = request.json.get('choice', '').strip()

    if user_choice.lower() == 'back to main menu':
        # Reset to main menu
        current_state = MENU_STATE
    elif user_choice.lower() == MENU_STATE:
        pass
    elif user_choice in menu_structure.get(current_state, []):
        current_state = user_choice
    else:
        return jsonify({"error": "Invalid choice. Please type menu to get the faq."})

    # Get the current state data
    state_data = menu_structure[current_state]

    if isinstance(state_data, list):
        response = {
            "question": f"Please choose an option from {current_state}",
            "options": state_data
        }
    else:
        response = {
            "answer": state_data,
            "options": ["Back to Main Menu"]
        }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
