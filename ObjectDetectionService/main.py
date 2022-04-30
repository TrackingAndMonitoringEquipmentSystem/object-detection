import rglob
import copy
from tkinter import W
from flask import json
import base64
import os
import numpy as np
import cv2 as cv
from dotenv import load_dotenv
import matplotlib.pyplot as plt
load_dotenv()


class ObjectDetectionService:
    def __init__(self):
        self.camerasMap = os.getenv('DETECT_CAMARAS').split(',')
        for index in range(len(self.camerasMap)):
            self.camerasMap[index] = int(self.camerasMap[index])
            cap = cv.VideoCapture(self.camerasMap[index])
            cap.read()
            cap.read()
            cap.read()
            cap.release()

    def detect(self, uuid):
        detectedResults = []
        for camNum in self.camerasMap:
            print('canNum:', camNum)
            camara = cv.VideoCapture(camNum)
            camara.read()
            camara.read()
            camara.read()
            camara.read()
            _, image = camara.read()
            cv.imwrite('cam{}_original.jpg'.format(camNum), image)
            grayImage = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
            _, thresh = cv.threshold(grayImage, 130, 255, cv.THRESH_BINARY_INV)
            kernel = np.ones((5, 5), np.uint8)
            opening = cv.morphologyEx(
                thresh, cv.MORPH_OPEN, kernel, iterations=2)
            cv.imwrite('cam{}_removed_noise.jpg'.format(camNum), opening)
            contours, hierarchy = cv.findContours(
                opening, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            imageNumber = 0
            detectedObjects = []
            for c in contours:
                x, y, w, h = cv.boundingRect(c)
                if w > 100 and h > 100:
                    detectedObjects.append({'x': x, 'y': y, 'w': w, 'h': h})
                    ROI = image[y:y+h, x:x+w]
                    cv.imwrite("cam{}_ROI_{}.jpg".format(
                        camNum, imageNumber), ROI)
                    cv.drawContours(image, contours, -1, (0, 255, 0), 3)
                    cv.imwrite("cam{}_detected_{}.jpg".format(
                        camNum, imageNumber), image)
                    imageNumber += 1

            detectedResults.append(
                {'image': image, 'detectedObjects': detectedObjects})
            camara.release()
        saveDetectedResults = copy.deepcopy(detectedResults)
        for saveDetectedResult in saveDetectedResults:
            _, buffer = cv.imencode('.jpg', saveDetectedResult['image'])
            base64image = base64.b64encode(buffer)
            saveDetectedResult['image'] = base64image.decode('utf-8')
        with open("temp-files/{}.json".format(uuid), "w") as file:
            file.write(json.dumps(saveDetectedResults))
        for detectedResult in detectedResults:
            encode_param = [int(cv.IMWRITE_JPEG_QUALITY), 20]
            _, buffer = cv.imencode(
                '.jpg',  detectedResult['image'], encode_param)
            base64image = base64.b64encode(buffer).decode('utf-8')
            detectedResult['image'] = base64image
        return detectedResults

    def saveDetect(self, uuid, macAddresse):
        with open('temp-files/{}.json'.format(uuid)) as file:
            loadedResults = json.load(file)
            cnt = 0
            for loadedResult in loadedResults:
                imageBase64 = loadedResult['image']
                buffer = base64.b64decode(imageBase64)
                npBuf = np.asarray(bytearray(buffer), dtype="uint8")
                image = cv.imdecode(npBuf, cv.IMREAD_COLOR)
                for index in range(len(loadedResult['detectedObjects'])):
                    x = loadedResult['detectedObjects'][index]['x']
                    w = loadedResult['detectedObjects'][index]['w']
                    y = loadedResult['detectedObjects'][index]['y']
                    h = loadedResult['detectedObjects'][index]['h']
                    cv.imwrite(
                        'object-pictures/{}.jpg'.format(macAddresse[cnt]), image[y:y+h, x:x+w])
                    cnt += 1
        return {'isSuccess': True}

    def recognition(self):
        detectedMacAddresse = []
        detectedImages = []
        for camNum in self.camerasMap:
            camara = cv.VideoCapture(camNum)
            camara.read()
            camara.read()
            camara.read()
            camara.read()
            _, image = camara.read()
            cv.imwrite('cam{}_original.jpg'.format(camNum), image)
            grayImage = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
            _, thresh = cv.threshold(grayImage, 130, 255, cv.THRESH_BINARY_INV)
            kernel = np.ones((5, 5), np.uint8)
            opening = cv.morphologyEx(
                thresh, cv.MORPH_OPEN, kernel, iterations=2)
            cv.imwrite('cam{}_removed_noise.jpg'.format(camNum), opening)
            contours, hierarchy = cv.findContours(
                opening, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            imageNumber = 0
            for c in contours:
                x, y, w, h = cv.boundingRect(c)
                if w > 100 and h > 100:
                    ROI = grayImage[y:y+h, x:x+w]
                    cv.imwrite("cam{}_ROI_{}.jpg".format(
                        camNum, imageNumber), ROI)
                    detectedImages.append(ROI)
                    imageNumber += 1
            camara.release()
        fileList = rglob.rglob("object-pictures/", "*")
        sift = cv.SIFT_create()
        cnt = 0
        for detectedImage in detectedImages:
            for file in fileList:
                dbObject = cv.imread(file, 0)
                kp1, des1 = sift.detectAndCompute(detectedImage, None)
                kp2, des2 = sift.detectAndCompute(dbObject, None)
                # print("des1: descriptors=", des1.shape)
                # print("des2: descriptors=", des2.shape)
                # FLANN parameters
                FLANN_INDEX_KDTREE = 1
                index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
                search_params = dict(checks=50)   # or pass empty dictionary
                flann = cv.FlannBasedMatcher(index_params, search_params)
                matches = flann.knnMatch(des1, des2, k=2)

                matchesMask = [[0, 0] for i in range(len(matches))]
                # ratio test as per Lowe's paper
                matchesCount = 0
                for i, (m, n) in enumerate(matches):
                    if m.distance < 0.7*n.distance:
                        matchesCount += 1
                        matchesMask[i] = [1, 0]
                draw_params = dict(matchColor=(0, 255, 0),
                                   singlePointColor=(255, 0, 0),
                                   matchesMask=matchesMask,
                                   flags=cv.DrawMatchesFlags_DEFAULT)
                print('matchesCount:', matchesCount)
                if matchesCount > 50:
                    print('file:', file)
                    detectedMacAddresse.append(
                        file.split('/')[1].split('.')[0])
                drawMatch = cv.drawMatchesKnn(
                    detectedImage, kp1, dbObject, kp2, matches, None, **draw_params)
                # plt.imshow(drawMatch)
                # plt.show()
                cv.imwrite('detected{}_{}.jpg'.format(cnt, file), drawMatch)
            cnt += 1
        return list(set(detectedMacAddresse))


def main():
    objectDetectionService = ObjectDetectionService()
    objectDetectionService.detect()


if __name__ == '__main__':
    main()
