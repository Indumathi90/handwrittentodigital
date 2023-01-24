import os
import time

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from flask import Flask, render_template, request, make_response
from msrest.authentication import CognitiveServicesCredentials
from fpdf import FPDF, HTMLMixin

app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates')

computer_vision_key = os.environ['COMPUTER_VISION_KEY']
computer_vision_name = os.environ['COMPUTER_VISION_NAME']
computer_vision_endpoint = f"https://{computer_vision_name}.cognitiveservices.azure.com/"
computer_vision_client = ComputerVisionClient(computer_vision_endpoint,
                                              CognitiveServicesCredentials(computer_vision_key))


class MyFPDF(FPDF, HTMLMixin):
    pass


@app.route("/")
def home():
    return render_template('home.html')


@app.route("/convert_from_url", methods=['POST'])
def convert_from_url():
    image_url = request.form['image_url']
    try:
        read_response = computer_vision_client.read(image_url, raw=True, language='en')
        operation_id = get_operation_id_from_read_response(read_response)
        digital_text = convert(operation_id)
        return render_template('converted_text.html', digital_text=digital_text, failure=False,
                               operation_id=operation_id)
    except Exception as e:
        print(e)
        return render_template('converted_text.html', digital_text="", failure=True, operation_id="")


@app.route("/convert_from_local", methods=['POST'])
def convert_from_local():
    uploaded_image = request.files['image']
    try:
        read_response = computer_vision_client.read_in_stream(uploaded_image, raw=True, language='en')
        operation_id = get_operation_id_from_read_response(read_response)
        digital_text = convert(operation_id)
        return render_template('converted_text.html', digital_text=digital_text, failure=False,
                               operation_id=operation_id)
    except Exception as e:
        print(e)
        return render_template('converted_text.html', digital_text="", failure=True, operation_id="")


@app.route("/download_as_text_file", methods=['GET'])
def download_as_text_file():
    operation_id = request.args.get("operation_id")
    digital_text = convert(operation_id)
    response = app.response_class(response=digital_text, status=200, mimetype='application/txt',
                                  headers={'Content-disposition': 'attachment; filename=converted_file.txt'})
    return response


@app.route("/download_as_pdf_file", methods=['GET'])
def download_as_pdf_file():
    operation_id = request.args.get("operation_id")
    digital_text = convert(operation_id)
    pdf = MyFPDF()
    pdf.add_page()
    pdf.write_html(digital_text)
    response = make_response(pdf.output(dest='S'))
    response.headers.set('Content-Disposition', 'attachment', filename='converted_file.pdf')
    response.headers.set('Content-Type', 'application/pdf')
    return response


def get_operation_id_from_read_response(read_response):
    read_operation_location = read_response.headers["Operation-Location"]
    return read_operation_location.split("/")[-1]


def convert(operation_id):
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


if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)
