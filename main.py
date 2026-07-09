import cv2
import csv
import cvzone
from cvzone.HandTrackingModule import HandDetector

# Camera Setup
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Hand Detector
detector = HandDetector(detectionCon=0.8, maxHands=1)


class MCQ:
    def __init__(self, data):
        self.question = data[0]
        self.choice1 = data[1]
        self.choice2 = data[2]
        self.choice3 = data[3]
        self.choice4 = data[4]
        self.answer = int(data[5])
        self.userAns = None

    def update(self, cursor, bboxs):
        for i, bbox in enumerate(bboxs):
            x1, y1, x2, y2 = bbox

            if x1 < cursor[0] < x2 and y1 < cursor[1] < y2:
                self.userAns = i + 1
                return True

        return False


# ================= Load Questions =================

pathCSV = "Mcqs.csv"

with open(pathCSV, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    dataAll = list(reader)[1:]

mcqList = []

for q in dataAll:
    if len(q) >= 6:
        mcqList.append(MCQ(q))

qNo = 0
qTotal = len(mcqList)

print("Total Questions:", qTotal)

# Click Lock
clicked = False

# ================= Main Loop =================

while True:

    success, img = cap.read()

    if not success:
        continue

    img = cv2.flip(img, 1)

    hands, img = detector.findHands(img, flipType=False)

    if qNo < qTotal:

        mcq = mcqList[qNo]

        img, bboxQ = cvzone.putTextRect(img, mcq.question,
                                        [100, 100], 2, 2,
                                        offset=20, border=3)

        img, bbox1 = cvzone.putTextRect(img, mcq.choice1,
                                        [100, 250], 2, 2,
                                        offset=20, border=3)

        img, bbox2 = cvzone.putTextRect(img, mcq.choice2,
                                        [700, 250], 2, 2,
                                        offset=20, border=3)

        img, bbox3 = cvzone.putTextRect(img, mcq.choice3,
                                        [100, 450], 2, 2,
                                        offset=20, border=3)

        img, bbox4 = cvzone.putTextRect(img, mcq.choice4,
                                        [700, 450], 2, 2,
                                        offset=20, border=3)

        if hands:

            lmList = hands[0]["lmList"]

            cursor = lmList[8][:2]

            cv2.circle(img, cursor, 10, (255, 0, 255), cv2.FILLED)

            length, info, img = detector.findDistance(
                lmList[8][:2],
                lmList[12][:2],
                img
            )

            # Select answer only once per pinch
            if length < 35 and not clicked:

                if mcq.update(cursor, [bbox1, bbox2, bbox3, bbox4]):
                    clicked = True
                    qNo += 1

            # Reset after fingers separate
            if length > 45:
                clicked = False

    else:

        score = 0

        for mcq in mcqList:
            if mcq.answer == mcq.userAns:
                score += 1

        percentage = round((score / qTotal) * 100, 2)

        img, _ = cvzone.putTextRect(
            img,
            "Quiz Completed",
            [350, 250],
            3,
            3,
            offset=20,
            border=3
        )

        img, _ = cvzone.putTextRect(
            img,
            f"Your Score : {percentage}%",
            [350, 400],
            3,
            3,
            offset=20,
            border=3
        )

    # Progress Bar
    if qTotal > 0:
        barValue = 150 + int((950 / qTotal) * qNo)

        cv2.rectangle(img, (150, 650), (barValue, 700),
                      (0, 255, 0), cv2.FILLED)

        cv2.rectangle(img, (150, 650), (1100, 700),
                      (255, 0, 255), 5)

        cvzone.putTextRect(
            img,
            f'{int((qNo / qTotal) * 100)}%',
            [1130, 670],
            2,
            2,
            offset=10,
            border=2
        )

    cv2.imshow("Quiz", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()