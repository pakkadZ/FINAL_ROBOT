import cv2
import numpy as np
import serial
import time

# Set up serial communication with ESP32
ser = serial.Serial('COM6', 115200, timeout=1)  # Change 'COMX' to your ESP32 port
time.sleep(2)  # Allow time for ESP32 to initialize

cap = cv2.VideoCapture(1)


center_width = 400  
center_height = 200  


offset_y = 100  

while True:
    ret, frame = cap.read()

    height, width = frame.shape[:2]
    

    start_x = int((width - center_width) / 2)
    start_y = int((height - center_height) / 2) + offset_y  
    end_x = start_x + center_width
    end_y = start_y + center_height


    center_area = frame[start_y:end_y, start_x:end_x]

   
    gray_image = cv2.cvtColor(center_area, cv2.COLOR_BGR2GRAY)
    
   
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

    
    edges = cv2.Canny(blurred_image, threshold1=90, threshold2=255)

  
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=50, maxLineGap=10)

   
    if lines is not None:
        best_angle = None
        best_line = None
        min_angle_diff = float('inf')  

    
        for line in lines:
            x1, y1, x2, y2 = line[0]
          
            delta_y = y2 - y1
            delta_x = x2 - x1
            angle = np.arctan2(delta_y, delta_x) * 180 / np.pi 

          
            angle_diff = abs(angle)

           
            if angle_diff < min_angle_diff:
                min_angle_diff = angle_diff
                best_angle = angle
                best_line = line

   
        if best_line is not None:
            x1, y1, x2, y2 = best_line[0]
           
            cv2.line(center_area, (x1, y1), (x2, y2), (0, 0, 0), 5)  

   
            print(f"Best Angle: {best_angle:.2f} degrees")

           
            if best_angle > 0: 
                cv2.putText(frame, 'Turn Left', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            elif best_angle < 0:  
                cv2.putText(frame, 'Turn Right', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            else:  
                cv2.putText(frame, 'Move Forward', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)


    cv2.imshow('Robot Line Following', frame)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
