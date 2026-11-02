try:
    from picamera2 import Picamera2
    PiCamera_available = True
    print("PiCamera library is available.")
except ImportError:
    PiCamera_available = False
    print("PiCamera library is not available. Falling back to OpenCV.")

try:
    from ultralytics import YOLO
    YOLO_available = True
    print("YOLO library is available.")
except ImportError:
    YOLO_available = False
    print("YOLO library is not available.")

def is_raspberry_camera():
    return PiCamera_available

def get_picamera(width, height):
    if PiCamera_available:
        picam2 =  Picamera2()
        picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (width, height)}))
        return picam2
    return None