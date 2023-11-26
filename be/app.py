from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
import io
from infer_sd import run_inpaint
from infer_owl import run_owl

app = Flask(__name__)
CORS(app)
port = 5100


@app.route('/owl', methods=['POST'])
def owl():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image= request.files['image'].read()
    img = Image.open(io.BytesIO(image.read()))

    image_original, mask, bboxes = run_owl(img, "")

    file_object = io.BytesIO()
    bboxes.save(file_object, 'PNG')  
    file_object.seek(0)

    return send_file(file_object, mimetype='image/PNG')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port)
