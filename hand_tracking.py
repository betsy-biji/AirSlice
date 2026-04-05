import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )

        self.prev = None  # for smoothing

    def get_finger_position(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        h, w, _ = frame.shape
        finger_pos = None

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # index fingertip = landmark 8
                x = int(hand_landmarks.landmark[8].x * w)
                y = int(hand_landmarks.landmark[8].y * h)
                finger_pos = (x, y)

        # 🔥 SMOOTHING (after detection)
        if finger_pos:
            if self.prev is not None:
                px, py = self.prev
                x = int((px + finger_pos[0]) / 2)
                y = int((py + finger_pos[1]) / 2)
                finger_pos = (x, y)

            self.prev = finger_pos

        return finger_pos