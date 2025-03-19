import cv2
import numpy as np
import serial
import time

# Set up serial communication with ESP32
ser = serial.Serial('COM6', 115200, timeout=1)  # Change 'COMX' to your ESP32 port
time.sleep(2)  # Allow time for ESP32 to initialize

# Open the camera
cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to grayscale and apply threshold
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 95, 255, cv2.THRESH_BINARY_INV)

    # Get frame dimensions
    h, w = thresh.shape
    box_width = w // 7.5
    box_height = h // 7.5
    x_center = w // 2
    y_pos = h // 2
    spacing = box_width // 2  # Space between boxes

    # Define 3 small sensor regions & convert to int
    left_x = int(x_center - box_width * 1.5 - spacing)
    center_x = int(x_center - box_width // 2.0)
    right_x = int(x_center + box_width // 2.0 + spacing)
    y_pos = int(y_pos)
    box_width = int(box_width)
    box_height = int(box_height)

    # Extract regions from thresholded image
    left_region = thresh[y_pos:y_pos+box_height, left_x:left_x+box_width]
    center_region = thresh[y_pos:y_pos+box_height, center_x:center_x+box_width]
    right_region = thresh[y_pos:y_pos+box_height, right_x:right_x+box_width]

    # Check for black pixels in each small box
    left_detected = np.any(left_region == 255)
    center_detected = np.any(center_region == 255)
    right_detected = np.any(right_region == 255)

    # Determine movement command
    if center_detected:
        command = "backward"
        center_color = (0, 0, 255)  # Red
    else:
        center_color = (255, 255, 255)  # White
    
    if left_detected:
        command = "CCW"  # Turn left
        left_color = (0, 0, 255)  # Red
    else:
        left_color = (255, 255, 255)  # White
    
    if right_detected:
        command = "CW"  # Turn right
        right_color = (0, 0, 255)  # Red
    else:
        right_color = (255, 255, 255)  # White
    
    if not (center_detected or left_detected or right_detected):
        command = "stop"
    
    # Send command to ESP32
    ser.write((command + "\n").encode())

    # Display detection results
    detected_text = f"Detected: {command}"
    cv2.putText(frame, detected_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Draw sensor boxes
    cv2.rectangle(frame, (left_x, y_pos), (left_x + box_width, y_pos + box_height), left_color, 2)
    cv2.rectangle(frame, (center_x, y_pos), (center_x + box_width, y_pos + box_height), center_color, 2)
    cv2.rectangle(frame, (right_x, y_pos), (right_x + box_width, y_pos + box_height), right_color, 2)

    # Show the result
    cv2.imshow("Line Following Detection", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
ser.close()
cv2.destroyAllWindows()
