import os

from dotenv import load_dotenv
from pymongo import MongoClient

from flask import Flask, request, jsonify
from flask_cors import CORS

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


# =========================================================
# 1. Load environment variables
# =========================================================

load_dotenv()


# =========================================================
# 2. Flask application
# =========================================================

app = Flask(__name__)
CORS(app)


# =========================================================
# 3. Translation model
# =========================================================

print("Loading translation model...")

MODEL_NAME = "facebook/nllb-200-distilled-600M"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

print("Model loaded successfully!")


# =========================================================
# 4. Supported languages
# =========================================================

LANGUAGES = {
    "auto": "Detect Language",
    "en": "English",
    "fr": "French",
    "ta": "Tamil",
    "hi": "Hindi",
    "kn": "Kannada"
}


# NLLB language codes
LANG_CODES = {
    "en": "eng_Latn",
    "fr": "fra_Latn",
    "ta": "tam_Taml",
    "hi": "hin_Deva",
    "kn": "kan_Knda"
}


# =========================================================
# 5. MongoDB connection
# =========================================================

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://localhost:27017/"
)

MONGO_DB_NAME = os.getenv(
    "MONGO_DB_NAME",
    "ltm_aiml"
)


try:
    mongo_client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000
    )

    # Test MongoDB connection
    mongo_client.admin.command("ping")

    db = mongo_client[MONGO_DB_NAME]
    translations_collection = db["translations"]

    print("MongoDB connected successfully!")

except Exception as e:

    mongo_client = None
    db = None
    translations_collection = None

    print("MongoDB connection failed:", e)
    print("Translation will still work without MongoDB.")


# =========================================================
# 6. Home endpoint
# =========================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "message": "LTM AIML Translation API is running",
        "endpoints": {
            "languages": "/languages",
            "translate": "/translate"
        }
    })


# =========================================================
# 7. Languages endpoint
# =========================================================

@app.route("/languages", methods=["GET"])
def languages():

    return jsonify(LANGUAGES)


# =========================================================
# 8. Translation endpoint
# =========================================================

@app.route("/translate", methods=["POST"])
def translate():

    try:

        # Get JSON data
        data = request.get_json()

        if not data:

            return jsonify({
                "error": "JSON data is required"
            }), 400


        # Get input text
        text = data.get("text", "").strip()


        # Get source and target languages
        source_lang = data.get(
            "source_lang",
            "en"
        )

        target_lang = data.get(
            "target_lang",
            "fr"
        )


        # Check text
        if not text:

            return jsonify({
                "error": "Text cannot be empty"
            }), 400


        # Automatic language detection
        if source_lang == "auto":

            return jsonify({
                "error": "Automatic language detection is not implemented yet. Please select a source language."
            }), 400


        # Check source language
        if source_lang not in LANG_CODES:

            return jsonify({
                "error": "Unsupported source language"
            }), 400


        # Check target language
        if target_lang not in LANG_CODES:

            return jsonify({
                "error": "Unsupported target language"
            }), 400


        # Same language
        if source_lang == target_lang:

            translated_text = text

        else:

            # Get NLLB language codes
            source_code = LANG_CODES[source_lang]
            target_code = LANG_CODES[target_lang]


            # Tell NLLB the source language
            tokenizer.src_lang = source_code


            # Tokenize input
            inputs = tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            )


            # Generate translation
            translated_tokens = model.generate(
                **inputs,
                forced_bos_token_id=tokenizer.convert_tokens_to_ids(
                    target_code
                ),
                max_length=512
            )


            # Convert tokens to text
            translated_text = tokenizer.batch_decode(
                translated_tokens,
                skip_special_tokens=True
            )[0]


        # =================================================
        # Save translation in MongoDB
        # =================================================

        if translations_collection is not None:

            try:

                translations_collection.insert_one({

                    "original": text,

                    "translation": translated_text,

                    "source_language": source_lang,

                    "target_language": target_lang

                })

                print("Translation saved to MongoDB.")

            except Exception as mongo_error:

                print(
                    "MongoDB save error:",
                    mongo_error
                )


        # =================================================
        # Send response to React
        # =================================================

        return jsonify({

            "original": text,

            "translation": translated_text,

            "source_language": source_lang,

            "target_language": target_lang

        })


    except Exception as e:

        print(
            "Translation error:",
            e
        )

        return jsonify({

            "error": "Translation failed",

            "details": str(e)

        }), 500


# =========================================================
# 9. Run Flask
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )