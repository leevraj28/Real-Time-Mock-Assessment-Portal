import base64
import logging

import cv2
import numpy as np

logger = logging.getLogger(__name__)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

# A usable face should cover at least this share of the frame.
MIN_FACE_AREA_RATIO = 0.035


def detect_faces(base64_image: str, strict: bool = False) -> dict:
    """Check one camera frame for a clear face and a visible phone."""
    try:
        if "," in base64_image:
            base64_image = base64_image.split(",")[1]

        img_data = base64.b64decode(base64_image)
        img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            return {"status": "error", "message": "Failed to decode image"}

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        frame_h, frame_w = gray.shape[:2]
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
        face_count = len(faces)
        phone_seen = _phone_visible(gray, faces)

        violation_type = None
        message = "Face verification successful."
        is_violation = False

        if phone_seen:
            violation_type = "PHONE_DETECTED"
            message = "A mobile phone is visible on the camera. Put it away and show only your face."
            is_violation = True
        elif face_count == 0:
            violation_type = "NO_FACE_DETECTED"
            message = "Your face is not visible. Look straight at the camera."
            is_violation = True
        elif face_count > 1:
            violation_type = "MULTIPLE_FACES_DETECTED"
            message = f"More than one face is in view ({face_count}). Only you should be on camera."
            is_violation = True
        else:
            x, y, fw, fh = faces[0]
            face_ratio = (fw * fh) / float(frame_w * frame_h)
            center_x = (x + fw / 2) / float(frame_w)
            center_y = (y + fh / 2) / float(frame_h)
            eyes_visible = _eyes_visible(gray, x, y, fw, fh)
            if face_ratio < MIN_FACE_AREA_RATIO:
                violation_type = "FACE_TOO_SMALL"
                message = "Move closer. Your face needs to be clearly visible in the camera."
                is_violation = True
            elif strict and (center_x < 0.18 or center_x > 0.82 or center_y < 0.15 or center_y > 0.9):
                violation_type = "FACE_NOT_CLEAR"
                message = "Center your face in the camera so it is fully visible."
                is_violation = True
            elif strict and not eyes_visible and face_ratio < 0.08:
                violation_type = "FACE_NOT_CLEAR"
                message = "Your face is not clear. Face the camera with nothing covering it."
                is_violation = True

        return {
            "status": "success",
            "face_count": face_count,
            "is_violation": is_violation,
            "violation_type": violation_type,
            "message": message,
        }
    except Exception as e:
        logger.error(f"Face detection error: {str(e)}")
        return {"status": "error", "message": str(e)}


def _eyes_visible(gray, x, y, fw, fh) -> bool:
    roi = gray[y:y + fh, x:x + fw]
    if roi.size == 0:
        return False
    eyes = eye_cascade.detectMultiScale(roi, scaleFactor=1.1, minNeighbors=4, minSize=(12, 12))
    return len(eyes) >= 1


def _phone_visible(gray, faces) -> bool:
    """A phone is a tall or wide rectangle that is not the face itself."""
    frame_h, frame_w = gray.shape[:2]
    frame_area = frame_h * frame_w
    edges = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 60, 160)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < frame_area * 0.03 or area > frame_area * 0.28:
            continue
        approx = cv2.approxPolyDP(contour, 0.04 * cv2.arcLength(contour, True), True)
        if len(approx) != 4:
            continue
        x, y, rw, rh = cv2.boundingRect(approx)
        short_side = min(rw, rh)
        if short_side < 50:
            continue
        ratio = max(rw, rh) / float(short_side)
        # Handset screens are close to 16:9 or 19.5:9.
        if ratio < 1.7 or ratio > 2.35:
            continue
        if area / float(rw * rh) < 0.62:
            continue
        if _covers_face(x, y, rw, rh, faces):
            continue
        return True
    return False


def _covers_face(x, y, rw, rh, faces) -> bool:
    box_right, box_bottom = x + rw, y + rh
    for fx, fy, fw, fh in faces:
        cx = fx + fw / 2
        cy = fy + fh / 2
        if x <= cx <= box_right and y <= cy <= box_bottom:
            return True
    return False
