import cv2
import random
from hand_tracking import HandTracker
from fruit import Fruit

# 🎥 Camera
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

tracker = HandTracker()

# 🎨 Load backgrounds ONCE
bg_images = {
    1: cv2.imread("assets/bg1.jpg"),
    2: cv2.imread("assets/bg2.jpg"),
    3: cv2.imread("assets/bg3.jpg")
}

# 🔁 Reset
def reset_game():
    return [], [], 0, 1, False, [], 3

fruits, splashes, score, level, game_over, finger_trail, lives = reset_game()

# ✂️ Slice detection
def check_slice(fruit, trail):
    if len(trail) < 2:
        return False

    x1, y1 = trail[-2]
    x2, y2 = trail[-1]

    speed = abs(x2 - x1) + abs(y2 - y1)

    if speed < 6:
        return False

    if (abs(fruit.x - x2) < fruit.radius or abs(fruit.x - x1) < fruit.radius):
        if (abs(fruit.y - y2) < fruit.radius or abs(fruit.y - y1) < fruit.radius):
            return True

    return False


while True:
    ret, cam = cap.read()
    if not ret:
        break

    cam = cv2.flip(cam, 1)
    h, w, _ = cam.shape

    # 🎨 FIXED BACKGROUND LOGIC
    bg = bg_images.get(level)

    if bg is None:
        print(f"⚠️ Missing bg{level}.jpg — using bg1")
        bg = bg_images.get(1)

    frame = cv2.resize(bg, (w, h))

    if not game_over:

        # ✋ Finger tracking
        finger_pos = tracker.get_finger_position(cam)

        if finger_pos:
            finger_trail.append(finger_pos)
            if len(finger_trail) > 5:
                finger_trail.pop(0)

        # 🌍 Level system
        if score > 800:
            level = 3
        elif score > 400:
            level = 2
        else:
            level = 1

        # 🎯 Spawn fruits
        if random.randint(1, 20) == 1:
            fruits.append(Fruit(w))

        # 🍉 Update fruits
        for fruit in fruits[:]:
            fruit.move()
            fruit.draw(frame)

            if check_slice(fruit, finger_trail):

                # 💣 Bomb explosion
                if fruit.type == "bomb":
                    lives -= 1

                    for _ in range(25):
                        splashes.append([
                            fruit.x,
                            fruit.y,
                            random.randint(-10, 10),
                            random.randint(-10, 10),
                            random.randint(10, 20),
                            (0, 100 + random.randint(0, 155), 255)
                        ])

                    fruits.remove(fruit)

                    if lives <= 0:
                        game_over = True

                    continue

                # 🎨 Fruit colors
                if fruit.type == "apple":
                    color = (0, 0, 255)
                elif fruit.type == "banana":
                    color = (0, 255, 255)
                elif fruit.type == "watermelon":
                    color = (0, 200, 0)
                else:
                    color = (255, 255, 255)

                fruits.remove(fruit)

                # 💥 Splash
                for _ in range(10):
                    splashes.append([
                        fruit.x,
                        fruit.y,
                        random.randint(-5, 5),
                        random.randint(-5, 5),
                        random.randint(5, 10),
                        color
                    ])

                score += 10

            elif fruit.y > h:
                fruits.remove(fruit)

        # 💥 Splash animation
        for splash in splashes[:]:
            x, y, vx, vy, size, color = splash

            x += vx
            y += vy
            size -= 1

            splash[0] = x
            splash[1] = y
            splash[4] = size

            if size > 0:
                cv2.circle(frame, (int(x), int(y)), size, color, -1)
            else:
                splashes.remove(splash)

        # 🔵 Finger dot
        if finger_pos:
            cv2.circle(frame, finger_pos, 8, (255, 0, 0), -1)

        # 🎯 UI
        cv2.putText(frame, f"Score: {score}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.putText(frame, f"Level: {level}", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        cv2.putText(frame, f"Lives: {lives}", (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    else:
        cv2.putText(frame, "GAME OVER 💣", (120, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)

        cv2.putText(frame, "Press R to Restart", (120, 260),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("AirSlice Game", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == 27 or key == ord('q'):
        break

    if key == ord('r'):
        fruits, splashes, score, level, game_over, finger_trail, lives = reset_game()

cap.release()
cv2.destroyAllWindows()