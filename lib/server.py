from flask import Flask, request, jsonify, send_file
from PIL import Image
from image_processing import slic
import io
import os

app = Flask(__name__)

# Define your image processing function here
def process_image(file):
    # Load the image file
    img = Image.open(file)

    # Call the slic() function from image_processing.py to perform SLIC on the image
    processed_img = slic(img, 186, 11)

    # Save the processed image to a BytesIO object
    processed_io = io.BytesIO()
    processed_img.save(processed_io, format='JPEG')
    processed_io.seek(0)

    # Return the processed image as a BytesIO object
    return processed_io

@app.route('/process-image', methods=['POST'])
def process_image_route():
    # Check if an image file was uploaded
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']

    # Check if the file has a valid extension
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file extension'}), 400

    # Process the image file
    processed_io = process_image(file)

    # Return the processed image as a downloadable file
    return send_file(processed_io, mimetype='image/jpeg', attachment_filename='processed_image.jpg', as_attachment=True)

# Helper function to check if file has a valid extension
def allowed_file(filename):
    return True

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
