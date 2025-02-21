import cv2
import os
from gestures.gesture_detector import GestureDetector
from gestures.gesture_mapper import GestureMapper
# from utils.palm_integration import PalmIntegration
from utils.computer_control import ComputerControl

def main():
    # Initialize components
    gesture_detector = GestureDetector()
    gesture_mapper = GestureMapper()
    # palm_api_key = os.getenv("PALM_API_KEY")
    # if not palm_api_key:
        # raise ValueError("Palm API key not found. Please set the PALM_API_KEY environment variable.")

    # palm_integration = PalmIntegration(api_key=palm_api_key)
    computer_control = ComputerControl()

    # Start video capture
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            frame = cv2.resize(frame, (640, 480))  # Resize for performance
            gesture = gesture_detector.detect_gesture(frame)

            if gesture != "no_hand":
                print("Detected Gesture:", gesture)

                action = gesture_mapper.get_action(gesture)
                print("Mapped Action:", action)

                try:
                    computer_control.execute_command(action)
                except Exception as e:
                    print(f"Error executing command: {e}")

            cv2.imshow('Hand Gesture Control', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # Release resources
        cap.release()
        cv2.destroyAllWindows()
        print("Resources released. Exiting application.")

if __name__ == "_main_":
    main()