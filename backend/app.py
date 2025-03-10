from flask import Flask, request, jsonify, send_from_directory
import os
from chat import add_documents_to_vstore
from audio import get_audio
from fetch import get_doc_content
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

project_root = os.path.abspath(os.path.dirname(__file__))

@app.route('/')
def home():
    return "/"

@app.route('/update_db', methods=['POST'])
def update_vetor_db():
    try:
        form_data = request.form
        keywords = form_data["keywords"]
        doc_dict = get_doc_content(keywords)
        is_success = add_documents_to_vstore(doc_dict)

        if is_success:
            return jsonify({"message": "Documents added successfully!"}), 200
        else:
            return jsonify({"message": "Failed to add documents."}), 500

    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

    
@app.route('/query_db', methods=['POST'])
def query_db():
    try:
        form_data = request.get_json()
        print(form_data)
        keywords = form_data["query"]
        print(keywords)
        
        result = get_audio(keywords)
        
        if result:
            return jsonify({"message": result}), 200
        else:
            return jsonify({"message": "No results found for your query."}), 404

    except Exception as e:
        return jsonify({"message": "I'm sorry, there was an issue processing your request. Please try again later."}), 500
    
@app.route('/audios/<filename>')
def serve_audio(filename):
    audios_folder = os.path.join(app.root_path, 'audios')
    return send_from_directory(audios_folder, filename)

if __name__ == "__main__":
    app.run(debug=True)


