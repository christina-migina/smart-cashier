import cv2
import config
import numpy as np
from ultralytics import YOLO
import json
from utils.picamera_utils import is_raspberry_camera, get_picamera

IS_RASPI_CAMERA = is_raspberry_camera()
print(f"Using Raspberry Pi Camera: {IS_RASPI_CAMERA}")

with open("items_data.json", "r") as f:
    items_data = json.load(f)

detector = YOLO(config.MODEL_PATH)

if __name__ == "__main__":
    try:
        if IS_RASPI_CAMERA:
            cap = get_picamera(config.IMAGE_WIDTH, config.IMAGE_HEIGHT)
            cap.start()
        else:
            cap = cv2.VideoCapture(config.CAMERA_DEVICE_ID)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.IMAGE_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.IMAGE_HEIGHT)

        total_sum = 0
        item_name = "Searching..."
        item_price = 0

        while True:
            if IS_RASPI_CAMERA:
                frame = cap.capture_array()
                if frame.shape[2] == 4:
                    frame = frame[:, :, :3]
            else:
                ret, frame = cap.read()
                if not ret: 
                    break

            frame = np.ascontiguousarray(frame, dtype=np.uint8)

            display_frame = frame.copy()

            results = detector(frame, conf=0.92, stream=True)

            for r in results:
                boxes = r.boxes
                for box in boxes:
                    cls_id = int(box.cls[0])
                    # Берем координаты
                    coords = box.xyxy[0].tolist() # Переводим тензор в обычный список
                    x1, y1, x2, y2 = map(int, coords)

                    item_info = items_data.get(str(cls_id), {"name": "Unknown", "price": 0})
                    item_name = item_info["name"]
                    item_price = item_info["price"]

                    # Рисуем на display_frame (который мы гарантированно сделали Mat-совместимым)
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), config.TEXT_COLOR, 2)
                    
            cv2.putText(display_frame, f"Item: {item_name}", (config.TEXT_X_OFFSET, config.TEXT_Y_OFFSET), 
                        cv2.FONT_HERSHEY_SIMPLEX, config.FONT_SIZE, config.TEXT_COLOR, config.FONT_THICKNESS)
            
            cv2.putText(display_frame, f"Price: {item_price} {config.CURRENCY}", (config.TEXT_X_OFFSET, config.TEXT_Y_OFFSET + 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, config.FONT_SIZE, config.TEXT_COLOR, config.FONT_THICKNESS)
            
            cv2.putText(display_frame, f"Total Sum: {total_sum} {config.CURRENCY}", (config.TEXT_X_OFFSET, config.TEXT_Y_OFFSET + 80), 
                        cv2.FONT_HERSHEY_SIMPLEX, config.FONT_SIZE, (0, 255, 0), config.FONT_THICKNESS)

            cv2.imshow("Cassier", display_frame)
            key = cv2.waitKey(1) & 0xFF

            if key == 32:
                total_sum += item_price
            elif key == 27:
                break
    
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        # Release resources
        cv2.destroyAllWindows()
        if 'cap' in locals():
            cap.close() if IS_RASPI_CAMERA else cap.release()