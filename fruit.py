import random
import cv2
import os

class Fruit:
    def __init__(self, width):
        self.x = random.randint(50, width - 50)
        self.y = 0
        self.speed = random.randint(5, 8)
        self.radius = 30

        # 🔥 Less bombs (important fix)
        self.type = random.choices(
            ["apple", "banana", "watermelon", "bomb"],
            weights=[4, 4, 4, 1]   # bomb is rare
        )[0]

        self.image = self.load_image()

    def load_image(self):
        try:
            if self.type == "bomb":
                path = "assets/bomb.png"
            else:
                path = f"assets/fruits/{self.type}.png"

            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            return img
        except:
            return None

    def move(self):
        self.y += self.speed

    def draw(self, frame):
        h, w, _ = frame.shape

        if self.image is not None:
            img = cv2.resize(self.image, (60, 60))
            x1 = self.x - 30
            y1 = self.y - 30

            if 0 <= x1 < w-60 and 0 <= y1 < h-60:

                # 🔥 Proper transparency fix
                if img.shape[2] == 4:
                    alpha = img[:, :, 3] / 255.0
                    for c in range(3):
                        frame[y1:y1+60, x1:x1+60, c] = (
                            alpha * img[:, :, c] +
                            (1 - alpha) * frame[y1:y1+60, x1:x1+60, c]
                        )
                else:
                    frame[y1:y1+60, x1:x1+60] = img[:, :, :3]

        else:
            # fallback
            cv2.circle(frame, (self.x, self.y), self.radius, (0, 255, 0), -1)