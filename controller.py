import os
import time

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from flask import Flask, render_template, request
from msrest.authentication import CognitiveServicesCredentials

app = Flask(__name__)

computer_vision_key = os.environ['COMPUTER_VISION_KEY']
computer_vision_name = os.environ['COMPUTER_VISION_NAME']
computer_vision_endpoint = f"https://{computer_vision_name}.cognitiveservices.azure.com/"
computer_vision_client = ComputerVisionClient(computer_vision_endpoint,
                                              CognitiveServicesCredentials(computer_vision_key))


@app.route("/")
def home():
    return render_template('home.html')


@app.route("/convert_from_url", methods=['POST'])
def convert_from_url():
    image_url = request.form['image_url']
    digital_text = convert_text_from_image_url(image_url)
    return render_template('converted_text.html', digital_text=digital_text)


@app.route("/convert_from_local", methods=['POST'])
def convert_from_local():
    uploaded_image = request.files['image']
    digital_text = convert_text_from_uploaded_image(uploaded_image)
    return render_template('converted_text.html', digital_text=digital_text)


def convert_text_from_uploaded_image(image_stream):
    return convert(computer_vision_client.read_in_stream(image_stream, raw=True, language='en'))


def convert_text_from_image_url(image_url):
    return convert(computer_vision_client.read(image_url, raw=True, language='en'))


def convert(read_response):
    read_operation_location = read_response.headers["Operation-Location"]
    operation_id = read_operation_location.split("/")[-1]
    while True:
        read_result = computer_vision_client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    digital_text = ""
    # Print the detected text, line by line
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            for line in text_result.lines:
                digital_text = digital_text + '\n' + line.text

    return digital_text
