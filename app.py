from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
import markdown2

app = Flask(__name__, static_folder='static')
CORS(app)

# Configure API key and set up model
genai.configure(api_key="AIzaSyBHVZRyf45wOCAFu7-EwpA142eJ0u433d4")

# Adjust the generation configuration for longer, detailed responses
generation_config = {
    "temperature": 0.7,  # Lowered temperature for more factual responses
    "top_p": 0.9,
    "top_k": 50,
    "max_output_tokens": 2000,  # Higher token count to ensure more content
    "response_mime_type": "text/plain",
}

# Reinforce instruction with a minimum word length and specific format for legal context
instructions = [
    "You are a detailed and knowledgeable assistant for the Department of Justice in India. Always provide answers in simple language but with detailed information, ensuring responses are at least 120 words long.",
    "When asked about punishments for crimes, respond with information on relevant punishments according to the Indian Penal Code (IPC) and Nyaya Sahita. Provide appropriate IPC sections and details where possible.",
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=instructions
)

# Start chat session with the model
chat_session = model.start_chat(enable_automatic_function_calling=True)

def chat_with_llm(user_input):
    try:
        # Check if the input is related to punishment to provide focused answers
        if "punishment" in user_input.lower() or "sentence" in user_input.lower():
            user_input += " Provide the relevant IPC sections and detailed legal implications."

        # Send message to the chat session and retrieve response
        response = chat_session.send_message(user_input)
        return response.text if response.text else "Sorry, no response could be generated."
    except Exception as e:
        print(f"Error in generating response: {e}")  # Debugging print
        return "Sorry, I could not generate a response at this time."

@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        data = request.get_json()
        user_input = data.get('message')
        if not user_input:
            return jsonify({'response': "Please provide a valid message."}), 400

        # Get the response and convert it to HTML format
        response = chat_with_llm(user_input)
        html_response = markdown_to_html(response)
        return jsonify({'response': html_response})
    except Exception as e:
        print(f"Error in chatbot route: {e}")  # Debugging print
        return jsonify({'response': "Sorry, an error occurred while processing your request."}), 500

def markdown_to_html(markdown_text):
    markdowner = markdown2.Markdown()
    return markdowner.convert(markdown_text)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
