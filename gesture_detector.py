import mediapipe as mp
import numpy as np
import cv2
from collections import deque

class GestureDetector:
    def _init_(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.prev_positions = deque(maxlen=5)  # Store last 5 positions for smoothing
        self.gesture_history = deque(maxlen=3)  # Store last 3 gestures for stability
        
        # Thresholds for gesture detection
        self.FINGER_BENT_THRESHOLD = 0.1
        self.PINCH_THRESHOLD = 0.04
        self.FINGER_SPREAD_THRESHOLD = 0.08

    def detect_gesture(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        
        if results.multi_hand_landmarks:
            landmarks = results.multi_hand_landmarks[0]
            self.mp_draw.draw_landmarks(frame, landmarks, self.mp_hands.HAND_CONNECTIONS)
            gesture = self._classify_gesture(landmarks)
            
            # Add gesture to history and return most common gesture
            self.gesture_history.append(gesture)
            if len(self.gesture_history) == 3:
                return max(set(self.gesture_history), key=self.gesture_history.count)
            return gesture
        return "no_hand"

    def _classify_gesture(self, landmarks):
        points = np.array([[lm.x, lm.y, lm.z] for lm in landmarks.landmark])
        
        # Get finger states and measurements
        fingers_extended = self._get_fingers_state(points)
        thumb_index_distance = self._get_distance(points[4], points[8])
        finger_spread = self._get_finger_spread(points)
        
        # Store index finger position for cursor control
        self.prev_positions.append(points[8][:2])  # Store only x,y coordinates

        # 1. Cursor Movement (Open Palm)
        if all(fingers_extended) and finger_spread > self.FINGER_SPREAD_THRESHOLD:
            return "cursor_movement"
        
        # 2. Click Action (Pinch gesture)
        if fingers_extended[1] and thumb_index_distance < self.PINCH_THRESHOLD:
            return "click_action"
        
        # 3. Volume Control (Thumb-Index pinch with varying distance)
        if fingers_extended[1] and not any(fingers_extended[2:]) and self.PINCH_THRESHOLD < thumb_index_distance < 0.15:
            return "volume_control"
        
        # 4. Minimize Window (V sign)
        if fingers_extended[1] and fingers_extended[2] and not any(fingers_extended[3:]):
            return "minimize_window"
        
        # 5. Maximize Window (Open palm with spread fingers)
        if all(fingers_extended) and finger_spread > self.FINGER_SPREAD_THRESHOLD * 1.5:
            return "maximize_window"
        
        # 6. Close Window (Closed fist)
        if not any(fingers_extended) and self._is_fist(points):
            return "close_window"

        return "no_gesture"

    def _get_fingers_state(self, points):
        """Returns array of booleans indicating if each finger is extended"""
        fingers_state = []
        
        # Thumb (special case)
        thumb_tip = points[4]
        thumb_ip = points[3]
        thumb_mcp = points[2]
        fingers_state.append(self._is_thumb_extended(thumb_tip, thumb_ip, thumb_mcp))
        
        # Other fingers
        for tip_idx, pip_idx in zip([8, 12, 16, 20], [6, 10, 14, 18]):
            fingers_state.append(points[tip_idx][1] < points[pip_idx][1] - self.FINGER_BENT_THRESHOLD)
        
        return fingers_state

    def _is_thumb_extended(self, tip, ip, mcp):
        """Check if thumb is extended based on angles"""
        angle = self._get_angle(mcp, ip, tip)
        return angle > 30  # degrees

    def _get_finger_spread(self, points):
        """Calculate average distance between adjacent fingertips"""
        fingertips = [points[i] for i in [4, 8, 12, 16, 20]]
        distances = []
        for i in range(len(fingertips)-1):
            distances.append(self._get_distance(fingertips[i], fingertips[i+1]))
        return np.mean(distances)

    def _is_fist(self, points):
        """Check if hand is in fist position"""
        # Check if all fingertips are below their MCPs
        fingertips = [8, 12, 16, 20]
        mcps = [5, 9, 13, 17]
        return all(points[tip][1] > points[mcp][1] for tip, mcp in zip(fingertips, mcps))

    def _get_angle(self, p1, p2, p3):
        """Calculate angle between three points in degrees"""
        v1 = p1 - p2
        v2 = p3 - p2
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        return np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))

    def _get_distance(self, p1, p2):
        return np.sqrt(np.sum((p1 - p2) ** 2))

    def _get_vertical_movement(self, points):
        if len(self.prev_positions) < 2:
            return 0
        return self.prev_positions[-1][1] - self.prev_positions[-2][1]

    def _is_cursor_tracking(self, fingers_state):
        return fingers_state[1] and not any(fingers_state[2:])

    def _is_click_gesture(self, fingers_state, vertical_movement):
        return fingers_state[1] and fingers_state[2] and not any(fingers_state[3:]) and vertical_movement > 0.02

    def _is_right_click_gesture(self, fingers_state, vertical_movement):
        return all(fingers_state[1:4]) and not fingers_state[4] and vertical_movement > 0.02

    def _is_scroll_gesture(self, fingers_state, vertical_movement):
        return all(fingers_state[1:]) and abs(vertical_movement) > 0.015

    def get_cursor_position(self):
        if len(self.prev_positions) > 0:
            return self.prev_positions[-1]
        return None