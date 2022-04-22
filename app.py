from ObjectDetectionService.main import ObjectDetectionService
from flask import Flask, json, request
from dotenv import load_dotenv
import numpy as np
load_dotenv()
app = Flask(__name__)

objectDetectionService = ObjectDetectionService()


@app.route('/')
def hello():
    return 'Python Backend For Object Detection'


@app.route('/detect-object', methods=['POST'])
def detectObject():
    body = request.get_json(force=True)
    result = objectDetectionService.detect(body['uuid'])
    response = app.response_class(
        response=json.dumps(result),
        status=200,
        mimetype='application/json',
    )
    return response


@app.route('/save-detect', methods=['PATCH'])
def saveDetect():
    body = request.get_json(force=True)
    result = objectDetectionService.saveDetect(
        body['uuid'], body['macAddresse'])
    response = app.response_class(
        response=json.dumps(result),
        status=200,
        mimetype='application/json',
    )
    return response


@app.route('/recognition', methods=['GET'])
def recognition():
    result = objectDetectionService.recognition()
    response = app.response_class(
        response=json.dumps(result),
        status=200,
        mimetype='application/json',
    )
    return response
