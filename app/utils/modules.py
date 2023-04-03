import pandas as pd
import cv2, os
import argparse, subprocess
import supervision as sv
import numpy as np
import time, csv, json
import datetime, requests

def initial_setup()-> None :
    """
        Initializes the data folder, csv file 
        and signal json files.
    """
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
        try :
            download_model()
        except :
            print("⛔️ 1.Unable to download the model.")
        try :
            download_script()
        except :
            print("Warning ! ")
            print("❕ 2.Unable to implement the algorithm.")
            print("Kindly ignore if you are excuting the application inside the provided container.")
        doneSetup()
    main()


def download_script():
    """
        Downloads the customized algorithm to modify 
        the ultralytics package installed.
    """
    working_directory = '..'
    os.chdir(working_directory)
    result = subprocess.run(['python', '-m', 'setup'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(result.stdout.decode('utf-8'))
    os.chdir(os.path.join(os.getcwd() + '/app'))

def download_model():
    """
        Downloads the trained yolov8 model 🚀
        to detect person class.
    """
    if not os.path.exists('model'):
        os.makedirs('model')

    if not os.path.exists('model/model.pt'):
        file_id = "1UaSfz8VMUI3N4CP_mvs_n1qfipr8g0vM"
        url = f'https://drive.google.com/uc?id={file_id}'

        r = requests.get(url)
        open('model/model.pt', 'wb').write(r.content)
        r.close()

        print("Model is ready to do magic! 🪄 - Downloaded succssfully")

def parse_arguments() -> argparse.Namespace:
    """
        Initializes the commandline argument parser.
    """
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
    """
        Initializes the global variables to use in other methods.
    """
    from ultralytics import YOLO
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
    """
        Processes the frame and return the processed frame
        with bounding boxex and labels from 'frame'
    """
    ZONE_SIDES = np.array([
    [0,0],
    [videoWidth, 0],
    [videoWidth, videoHeight],
    [0,videoHeight]
    ])
    
    zone = sv.PolygonZone(polygon=ZONE_SIDES, frame_resolution_wh=tuple(args.webcam_resolution))
    
    start_time = time.time()
    
    from ultralytics import YOLO
    model = YOLO(model='model/model.pt', conf=thresh)
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
    """
        Writes the counts into a csv file 
        using 'Time' and 'Counts'.
    """
    with open('data/density.csv', mode='a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([startSeconds, count])

def detect(imgPath, confidence = 0.4) -> int:
    """
        Detects the person in a image using
        'Image path' and 'Threshold confidence'
    """
    from ultralytics import YOLO
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
    """
        Detects the person in a Video using
        'Video path' and 'Threshold confidence'
    """
    video_info = sv.VideoInfo.from_video_path(videoPath)
    global videoFPS, videoWidth, videoHeight, thresh
    thresh = confidence
    videoFPS = video_info.fps
    videoHeight = video_info.height
    videoWidth = video_info.width
    
    with open('data/density.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Time', 'Count'])
    
    sv.process_video(source_path=videoPath, target_path="data/output.mp4", callback=process_frame)
    
def getDataframe():
    """
        Reads and returns the dataframe from csv file
    """
    df = pd.read_csv('data/density.csv')
    return df

def checkStart() :
    """
        Reads and return the flag status 
        from signal file.
    """
    f = open('data/signal.json','r')
    data = json.load(f)
    f.close()
    return data['initiate']

def doneSetup():
    """
        Reads and Turn the Flag to off,
        to indicate that initial setup is done
    """
    f = open('data/signal.json','r')
    data = json.load(f)
    f.close()
    data['initiate'] = 0
    with open("data/signal.json", "w") as outfile:
        json.dump(data, outfile)
        outfile.close()

def getFlag():
    """
        Reads and return the flag value,
    """
    f = open('data/signal.json','r')
    data = json.load(f)
    f.close()
    return data['Flag']

def setFlag():
    """
        Reads and Sets the Flag to Off,
        To restrict processing the video.
    """
    f = open('data/signal.json','r')
    data = json.load(f)
    f.close()
    data['Flag'] = 0
    with open("data/signal.json", "w") as outfile:
        json.dump(data, outfile)
        outfile.close()

def resetFlag():
    """
        Reads and Sets the Flag to On,
        To allow processing the video.
    """
    f = open('data/signal.json','r')
    data = json.load(f)
    f.close()
    data['Flag'] = 1
    with open("data/signal.json", "w") as outfile:
        json.dump(data, outfile)
        outfile.close()
