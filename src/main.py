import cv2
import mediapipe as mp
import numpy as np
from pythonosc import udp_client
import argparse

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def send_osc_message(client, address, *args):
    client.send_message(address, args)

def send_hand_landmarks(client, hand_index, hand_landmarks, frame_shape):
    height, width = frame_shape[:2]
    coordinates = [hand_index]  # Prepend the hand index to the coordinates list
    for landmark in hand_landmarks.landmark:
        x, y = int(landmark.x * width), int(landmark.y * height)
        # Normalize the coordinates
        normalized_x = x / width
        normalized_y = y / height
        coordinates.extend([normalized_x, normalized_y])
    send_osc_message(client, "/hands", *coordinates)

def send_marker_data(client, marker_ids, marker_corners, frame_shape):
    if marker_ids is not None:
        height, width = frame_shape[:2]
        for idx, marker_id in enumerate(marker_ids):
            address = "/aruco/marker"
            marker_id = int(marker_id[0])
            
            # Normalize the coordinates
            coordinates = marker_corners[idx][0].ravel()
            coordinates[::2] = coordinates[::2] / width  # Normalizing x
            coordinates[1::2] = coordinates[1::2] / height # Normalizing y
            
            msg_args = [marker_id] + coordinates.tolist()
            send_osc_message(client, address, *msg_args)


def detect_and_process(camera_index, show_display, ip, port, inverted):
    cap = cv2.VideoCapture(camera_index)
    client = udp_client.SimpleUDPClient(ip, port)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250) 
    # dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_ARUCO_ORIGINAL) 
    
    parameters = cv2.aruco.DetectorParameters()

    markers_position = {}

    with mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        while True:
            _, frame = cap.read()
            if frame is None:
                print("Error: Could not read frame from webcam.")
                break
            
            # Hand detection with MediaPipe
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_image)

            # Send and draw hand landmarks
            if results.multi_hand_landmarks:
                for hand_index, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    send_hand_landmarks(client, hand_index, hand_landmarks, frame.shape)
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            
            # ArUco marker detection
            if inverted:
                frame = cv2.bitwise_not(frame)

            marker_corners, marker_ids, _ = cv2.aruco.detectMarkers(frame, dictionary, parameters=parameters)
            cv2.aruco.drawDetectedMarkers(frame, marker_corners, marker_ids)

            send_marker_data(client, marker_ids, marker_corners, frame.shape)

            # Update stored marker positions
            if marker_ids is not None:
                for i, marker_id in enumerate(marker_ids):
                    markers_position[int(marker_id[0])] = marker_corners[i][0]
            
            # Check if fingertip is above any stored marker
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    fingertip = [hand_landmarks.landmark[8].x * frame.shape[1], hand_landmarks.landmark[8].y * frame.shape[0]]
                    fingertip_normalized = [fingertip[0]/frame.shape[1], fingertip[1]/frame.shape[0]]
                    
                    for marker_id, corners in markers_position.items():
                        corners = np.array(corners, dtype=np.float32)
                        fingertip_np = np.array(fingertip_normalized, dtype=np.float32)
                        
                        if cv2.pointPolygonTest(corners, tuple(fingertip_np), False) > 0:
                            send_osc_message(client, "/hand_detected", marker_id)

            
            if show_display:
                cv2.imshow('MediaPipe Hands + ArUco Markers', frame)
                if cv2.waitKey(1) == 27:  # Esc key
                    break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hand and ArUco markers detection")
    parser.add_argument("--input", default=0, type=int, help="Camera input index")
    parser.add_argument("--show", default=0, type=int, help="Display the CV2 window (default is 0)")
    parser.add_argument("--ip", default="127.0.0.1", type=str)
    parser.add_argument("--port", default=8000, type=int)
    parser.add_argument("--inverted", default=False, action='store_true', help="Detect inverted markers")    

    args = parser.parse_args()
    detect_and_process(args.input, bool(args.show), args.ip, args.port, args.inverted)
