import pandas as pd
import cv2, os
import argparse
from ultralytics import YOLO
import supervision as sv
import numpy as np
import time, csv, json
import datetime, requests

def initial_setup()-> None :
    if not os.path.exists('data') :
        os.makedirs('data')
    if not os.path.exists("data/density.csv") : 
        fp = open('data/density.csv', 'x')
        fp.close()  
    if not os.path.exists('data/signal.json'):
        fp = open('data/signal.json', 'x')
        fp.close() 
        data = {"Flag" : 1, 'initiate' : 1}
        with open("data/signal.json", "w") as outfile:
            json.dump(data, outfile)
            outfile.close()
    state = checkStart()
    if state == 1:
        download_model()
        doneSetup()
    main()

def download_model():
    if not os.path.exists('model'):
        os.makedirs('model')

    if not os.path.exists('model/model.pt'):
        file_id = "1UaSfz8VMUI3N4CP_mvs_n1qfipr8g0vM"
        url = f'https://drive.google.com/uc?id={file_id}'

        r = requests.get(url)
        open('model/model.pt', 'wb').write(r.content)
        r.close()

        print("Initial Setup Completed! 🪄")

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Crowd detection')
    parser.add_argument(
        '--webcam-resolution',
        default=[1280,720],
        nargs=2,
        type=int
    )
    args = parser.parse_args()
    return args


def main():
    global args, model, frame_count, startSeconds, firstFrame, \
        videoFPS, videoHeight, videoWidth, fps_set
    args = parse_arguments()
    model = YOLO(model='model/model.pt', conf=0.4)
    frame_count = 0
    startSeconds = datetime.datetime.strptime('00:00:00', '%H:%M:%S')
    firstFrame = True
    videoFPS = 0
    videoWidth = 0
    videoHeight = 0
    fps_set = set()
    


def process_frame(frame : np.ndarray, _) -> np.ndarray: 
    ZONE_SIDES = np.array([
    [0,0],
    [videoWidth, 0],
    [videoWidth, videoHeight],
    [0,videoHeight]
    ])
    
    zone = sv.PolygonZone(polygon=ZONE_SIDES, frame_resolution_wh=tuple(args.webcam_resolution))
    
    start_time = time.time()
    results = model(frame, imgsz=1280)[0]
    detections = sv.Detections.from_yolov8(results)
    detections = detections[detections.class_id == 0]
    zone.trigger(detections=detections)
    
    box_annotator = sv.BoxAnnotator(thickness=2, text_thickness=1, text_scale=0.5, text_padding = 2)
    zone_annotator = sv.PolygonZoneAnnotator(zone=zone, color=sv.Color.white())
    
    labels = [
        f"{model.model.names[class_id]} {confidence :0.2f}"
        for _, confidence, class_id,_ 
        in detections
    ]
    frame = box_annotator.annotate(scene=frame, detections=detections, labels=labels)
    frame = zone_annotator.annotate(scene=frame)
    
    end_time = time.time()
    fps = 1 / (end_time - start_time)
    global fps_set
    fps_set.add(fps)
    cv2.putText(frame, "FPS: " + str(int(fps)), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    global frame_count
    global startSeconds
    global firstFrame
    frame_count = frame_count + 1
    
    if firstFrame :
        writeCSV(startSeconds.strftime('%M:%S'), len(labels))
        firstFrame = False
    my_time = videoFPS * int(max(list(fps_set)))
    if frame_count == my_time:
        startSeconds += datetime.timedelta(seconds=2)
        writeCSV(startSeconds.strftime('%M:%S'), len(labels))
        frame_count = 0
    return frame

def writeCSV(startSeconds, count):
    with open('data/density.csv', mode='a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([startSeconds, count])

def detect(imgPath, confidence = 0.4) -> int:
    args = parse_arguments()
    frame_width, frame_height = args.webcam_resolution
    model = YOLO(model='model/model.pt', conf=confidence)
    frame = cv2.imread(imgPath)
    
    box_annotator = sv.BoxAnnotator(
        thickness = 1,
        text_thickness = 1,
        text_scale = 0.5,
        text_padding = 2
    )
    
    height, width, channels = frame.shape
    
    IMG_SIDES = np.array([
    [0,0],
    [width, 0],
    [width, height],
    [0,height]
    ])
    zone = sv.PolygonZone(polygon=IMG_SIDES, frame_resolution_wh=tuple(args.webcam_resolution))
    zone_annotator = sv.PolygonZoneAnnotator(zone=zone, color=sv.Color.white())
    
    result = model(frame)[0]
    detection = sv.Detections.from_yolov8(result)
    
    labels = [
        f"{model.model.names[class_id]} {confidence :0.2f}"
        for _, confidence, class_id,_ 
        in detection
    ]
    
    print(f"The count of people in the image is {len(labels)}")

    frame = box_annotator.annotate(scene = frame, detections = detection, labels = labels)
    
    zone.trigger(detections=detection)
    frame = zone_annotator.annotate(scene=frame)
    cv2.imwrite('data/result.jpg', frame)
    return len(labels)

def detectVideo(videoPath, confidence=0.4) :
    video_info = sv.VideoInfo.from_video_path(videoPath)
    global videoFPS, videoWidth, videoHeight
    videoFPS = video_info.fps
    videoHeight = video_info.height
    videoWidth = video_info.width
    
    with open('data/density.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Time', 'Count'])
    
    sv.process_video(source_path=videoPath, target_path="data/output.mp4", callback=process_frame)
    
def getDataframe():
    df = pd.read_csv('data/density.csv')
    return df

def checkStart() :
    f = open('data/signal.json','r')
    data = json.load(f)
    f.close()
    return data['initiate']

def doneSetup():
    f = open('data/signal.json','r')
    data = json.load(f)
    f.close()
    data['initiate'] = 0
    with open("data/signal.json", "w") as outfile:
        json.dump(data, outfile)
        outfile.close()

def getProcessCount():
    f = open('data/signal.json','r')
    data = json.load(f)
    f.close()
    return data['Flag']

def setProcessCount():
    f = open('data/signal.json','r')
    data = json.load(f)
    f.close()
    data['Flag'] = 0
    with open("data/signal.json", "w") as outfile:
        json.dump(data, outfile)
        outfile.close()

def resetProcessCount():
    f = open('data/signal.json','r')
    data = json.load(f)
    f.close()
    data['Flag'] = 1
    with open("data/signal.json", "w") as outfile:
        json.dump(data, outfile)
        outfile.close()
