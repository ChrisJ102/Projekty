import cv2
import math
import time

# Zmienne globalne
_last_frame_time = time.time()
_distance_values = []
_initial_distance = None

# Cache dla detektora
_detector_cache = {
    "min_area": None,
    "max_area": None,
    "detector": None
}

def calculate_deformation(current_distance, initial_distance):
    if initial_distance > 0 and current_distance > 0:
        return math.log(current_distance / initial_distance)
    return None

def calculate_distance(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def adjust_brightness_contrast(image, brightness=0, contrast=0):
    brightness = float(brightness)
    contrast = float(contrast)

    image = cv2.addWeighted(image, contrast, image, 0, brightness)


    return image

def create_blob_detector(min_area, max_area):
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = min_area
    params.maxArea = max_area
    params.minThreshold = 1
    params.maxThreshold = 2000
    params.filterByCircularity = True

    params.minCircularity = 0.3
    params.minInertiaRatio = 0.5

    params.filterByConvexity = True
    params.minConvexity = 0.2
    params.filterByInertia = True

    params.thresholdStep = 10
    params.minRepeatability = 2
    params.filterByInertia = True
    params.minInertiaRatio = 0.5

    return cv2.SimpleBlobDetector_create(params)

def extract_roi_region(frame, center_x, center_y, size):
    h, w = frame.shape[:2]
    half = size // 2
    x1 = max(0, center_x - half)
    y1 = max(0, center_y - half)
    x2 = min(w, center_x + half)
    y2 = min(h, center_y + half)
    return frame[y1:y2, x1:x2]


def get_cached_blob_detector(min_area, max_area):
    if (_detector_cache["min_area"] != min_area or
        _detector_cache["max_area"] != max_area or
        _detector_cache["detector"] is None):

        _detector_cache["min_area"] = min_area
        _detector_cache["max_area"] = max_area
        _detector_cache["detector"] = create_blob_detector(min_area, max_area)

    return _detector_cache["detector"]

def extract_settings(entries, grayscale_var, negative_var):
    try:
        return {
            "brightness": float(entries["brightness"].get()),
            "contrast": float(entries["contrast"].get()),
            "roi_width": int(entries["roi_width"].get()),
            "roi_height": int(entries["roi_height"].get()),
            "min_area": float(entries["minArea"].get()),
            "max_area": float(entries["maxArea"].get()),
            "grayscale": grayscale_var.get(),
            "negative": negative_var.get()
        }
    except ValueError:
        return {
            "brightness": 0.0, "contrast": 0.0, "roi_width": 200, "roi_height": 200,
            "min_area": 50, "max_area": 5000, "grayscale": False, "negative": False
        }

def apply_filters(frame, settings):
    frame = adjust_brightness_contrast(frame, settings["brightness"], settings["contrast"])
    if settings["grayscale"]:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if settings["negative"]:
        frame = cv2.bitwise_not(frame)

    frame = cv2.GaussianBlur(frame, (3, 3), 0)
    return frame

def get_roi(frame, roi_width, roi_height):
    h, w = frame.shape[:2]
    x = max(0, (w - roi_width) // 2)
    y = max(0, (h - roi_height) // 2)
    return frame[y:y+roi_height, x:x+roi_width], (x, y, roi_width, roi_height)
