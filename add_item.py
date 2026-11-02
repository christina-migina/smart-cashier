from time import sleep
from ultralytics import YOLO
import torch
import json
import cv2
import config
import numpy as np
from utils.picamera_utils import is_raspberry_camera, get_picamera
from utils.db_utils import init_db, add_item_to_db

IS_RASPI_CAMERA = is_raspberry_camera()
print(f"Using Raspberry Pi Camera: {IS_RASPI_CAMERA}")

model = YOLO(config.MODEL_PATH)
print("Model loaded successfully.")

#name = int(input("Enter the name of the item: "))
#price = float(input("Enter the price of the item: "))

#new_item_data = {
#    "name": name,
#    "price": price
#}

if __name__ == "__main__":
    try:
        if IS_RASPI_CAMERA:
            cap = get_picamera(config.IMAGE_WIDTH, config.IMAGE_HEIGHT)
            cap.start()
        else:
            cap = cv2.VideoCapture(config.CAMERA_DEVICE_ID)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.IMAGE_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.IMAGE_HEIGHT)
    
        while True:
            if IS_RASPI_CAMERA:
                print("Capturing frame from Raspberry Pi Camera...")
                frame = cap.capture_array()
                if frame.shape[2] == 4:
                    frame = frame[:, :, :3]
            else:
                ret, frame = cap.read()
                if not ret: 
                    print("Failed to capture frame from webcam.")
                    break

            results = model.predict(frame, conf=0.92, stream=True)

            for r in results:
                r.plot()
                new_frame = r.plot()

            cv2.imshow("E", new_frame)

            if cv2.waitKey(1) == 27:
                break
    
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        # Release resources
        cv2.destroyAllWindows()
        if 'cap' in locals():
            cap.close() if IS_RASPI_CAMERA else cap.release()