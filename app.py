from ObjectDetectionService.main import ObjectDetectionService
from ScanTagService.main import ScanTagService
from flask import Flask, json, request
from dotenv import load_dotenv
import numpy as np
load_dotenv()
app = Flask(__name__)

objectDetectionService = ObjectDetectionService()
scanTagService = ScanTagService()


@app.route('/')
def hello():
    return 'Python Backend For Object Detection'


@app.route('/detect-object', methods=['POST'])
def detectObject():
    body = request.get_json(force=True)
    detectResults = objectDetectionService.detect(body['uuid'])
    scanResult = scanTagService.scan()
    objectDetectedCount = 0
    for detctResult in detectResults:
        objectDetectedCount += len(detctResult['detectedObjects'])
    macAddresses = []
    if scanResult['isSucceed']:
        macAddresses = scanResult['data']
    print('objectDetectedCount:', objectDetectedCount)
    print('macAddresses:', macAddresses)
    if (len(macAddresses) != objectDetectedCount) or len(macAddresses) == 0 or objectDetectedCount == 0:
        response = app.response_class(
            response=json.dumps({'message': 'invalid tag'}),
            status=400,
            mimetype='application/json',)
        return response

    response = app.response_class(
        response=json.dumps(
            {'objects': detectResults, 'macAddresses': macAddresses}),
        status=200,
        mimetype='application/json',
    )
    return response


@app.route('/save-detect', methods=['PATCH'])
def saveDetect():
    body = request.get_json(force=True)
    result = objectDetectionService.saveDetect(
        body['uuid'], body['macAddresses'])
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
