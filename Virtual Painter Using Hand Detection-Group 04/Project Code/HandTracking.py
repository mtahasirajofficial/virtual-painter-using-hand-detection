import cv2
import cv2 as cv
import mediapipe as mp
import numpy as np

class HandTracking():
    def __init__(self):
        self.draw_colour = (255, 0, 255)
        self.finger_tips = [4, 8, 12, 16, 20]
        self.mpDraw = mp.solutions.drawing_utils
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
        
    def find_hands(self, img, draw=True):
        img_rgb = cv.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.result = self.hands.process(img_rgb)
        if self.result.multi_hand_landmarks:
            for hand_landmarks in self.result.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, hand_landmarks, self.mpHands.HAND_CONNECTIONS)
        return img
    
    def get_location(self, img, hand_number=0, draw=True):
        self.landmarks = []
        if self.result.multi_hand_landmarks:
            hand = self.result.multi_hand_landmarks[hand_number]
            for hand_id, landmark in enumerate(hand.landmark):
                h, w, c = img.shape
                x, y = int(landmark.x * w), int(landmark.y * h)
                self.landmarks.append([hand_id, x, y])
                if hand_id == 8 and draw:  # draws the coloured circle at the tip of the index finger
                    cv.circle(img, (x, y), 20, self.draw_colour, cv.FILLED)
        return self.landmarks
    
    def how_many_fingers_up(self):
        fingers_up = []
        if len(self.landmarks) < 21:
            return [0, 0, 0, 0, 0]
        
        # Thumb - horizontal check
        if self.landmarks[self.finger_tips[0]][1] < self.landmarks[self.finger_tips[0] - 1][1]:
            fingers_up.append(1)
        else:
            fingers_up.append(0)
        
        # Other fingers - vertical check
        for hand_id in range(1, 5):
            if self.landmarks[self.finger_tips[hand_id]][2] < self.landmarks[self.finger_tips[hand_id] - 2][2]:
                fingers_up.append(1)
            else:
                fingers_up.append(0)
        return fingers_up
    
    def is_thumbs_up(self):
        """Improved thumbs up detection - requires clear vertical thumb with other fingers down"""
        if len(self.landmarks) < 21:
            return False
        
        fingers = self.how_many_fingers_up()
        
        # Only thumb should be up, all other fingers down
        if not (fingers[0] == 1 and fingers[1] == 0 and fingers[2] == 0 
                and fingers[3] == 0 and fingers[4] == 0):
            return False
        
        # Thumb tip should be significantly higher than thumb base
        if self.landmarks[self.finger_tips[0]][2] >= self.landmarks[self.finger_tips[0] - 1][2]:
            return False
        
        # All other fingertips should be below thumb tip
        for hand_id in range(1, 5):
            if self.landmarks[self.finger_tips[hand_id]][2] <= self.landmarks[self.finger_tips[0]][2]:
                return False
        
        # Additional vertical distance check
        if self.landmarks[6][2] - self.landmarks[self.finger_tips[0]][2] < 30:
            return False
        
        return True
    
    def is_thumbs_down(self):
        """Improved thumbs down detection"""
        if len(self.landmarks) < 21:
            return False
        
        fingers = self.how_many_fingers_up()
        
        # Only thumb should be extended downward, others closed
        if fingers[1] or fingers[2] or fingers[3] or fingers[4]:
            return False
        
        # Thumb tip should be below thumb base
        if self.landmarks[self.finger_tips[0]][2] <= self.landmarks[self.finger_tips[0] - 1][2]:
            return False
        
        # All other fingertips should be above thumb tip
        for hand_id in range(1, 5):
            if self.landmarks[self.finger_tips[hand_id]][2] >= self.landmarks[self.finger_tips[0]][2]:
                return False
        
        if self.landmarks[6][2] - self.landmarks[self.finger_tips[0]][2] > -30:
            return False
        
        return True
    
    def is_fist(self):
        """Improved fist detection"""
        fingers = self.how_many_fingers_up()
        
        # All fingers down
        if (not fingers[1] and not fingers[2] and not fingers[3] and not fingers[4]
                and not self.is_thumbs_up() and not self.is_thumbs_down() 
                and not self.drawing() and not self.selection()):
            return True
        return False
    
    def drawing(self):
        """Drawing mode - only index finger up"""
        fingers = self.how_many_fingers_up()
        
        # Only index finger up
        if (fingers[1] and not fingers[2] and not fingers[3] and not fingers[4]
                and not self.is_thumbs_up() and not self.is_thumbs_down()):
            return True
        return False
    
    def selection(self):
        """Selection mode - index and middle finger up (close together)"""
        fingers = self.how_many_fingers_up()
        
        if len(self.landmarks) < 21:
            return False
        
        # Index and middle finger up
        if not (fingers[1] and fingers[2] and not fingers[3] and not fingers[4]):
            return False
        
        if self.is_thumbs_up() or self.is_thumbs_down():
            return False
        
        # Check if fingers are close together (not spread like peace sign)
        index_tip = self.landmarks[8]
        middle_tip = self.landmarks[12]
        distance = np.sqrt((index_tip[1] - middle_tip[1])**2 + (index_tip[2] - middle_tip[2])**2)
        
        return distance < 40  # Close together for selection
    
    def is_peace_sign(self):
        """Peace sign (✌️) for clearing canvas - fingers spread apart"""
        fingers = self.how_many_fingers_up()
        
        if len(self.landmarks) < 21:
            return False
        
        # Index and middle finger up, others down
        if not (fingers[1] and fingers[2] and not fingers[3] and not fingers[4]):
            return False
        
        if self.is_thumbs_up() or self.is_thumbs_down():
            return False
        
        # Check if fingers are spread apart (peace sign, not selection)
        index_tip = self.landmarks[8]
        middle_tip = self.landmarks[12]
        distance = np.sqrt((index_tip[1] - middle_tip[1])**2 + (index_tip[2] - middle_tip[2])**2)
        
        return distance > 40  # Fingers spread apart for peace sign
    
    def is_pinching(self):
        """Check if thumb and index finger are pinching - increased threshold"""
        if len(self.landmarks) < 21:
            return False
        
        fingers = self.how_many_fingers_up()
        
        # Should not be in drawing mode or other gestures
        if self.drawing() or self.is_thumbs_up() or self.is_thumbs_down():
            return False
        
        thumb_tip = self.landmarks[4]
        index_tip = self.landmarks[8]
        distance = np.sqrt((thumb_tip[1] - index_tip[1])**2 + (thumb_tip[2] - index_tip[2])**2)
        
        # Increased threshold to avoid false positives
        return distance < 50
    
    def get_pinch_distance(self):
        """Get distance between thumb and index finger for brush size control"""
        if len(self.landmarks) < 21:
            return 50
        
        thumb_tip = self.landmarks[4]
        index_tip = self.landmarks[8]
        distance = np.sqrt((thumb_tip[1] - index_tip[1])**2 + (thumb_tip[2] - index_tip[2])**2)
        
        return distance
    
    def is_shape_mode(self):
        """Three fingers up for shape drawing mode"""
        fingers = self.how_many_fingers_up()
        
        # Index, middle, and ring finger up; pinky and thumb down
        if (fingers[1] and fingers[2] and fingers[3] and not fingers[4]
                and not self.is_thumbs_up() and not self.is_thumbs_down()):
            return True
        return False

# to try out only hand tracking
if __name__ == '__main__':
    web_cam = cv.VideoCapture(0)
    hand_tracking = HandTracking()
    while True:
        success, img = web_cam.read()
        img = hand_tracking.find_hands(img, draw=True)
        cv.imshow("Image", img)
        cv.waitKey(1)