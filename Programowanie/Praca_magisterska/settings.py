import json

SETTINGS_FILE = "settings.json"


def load_settings():
    """Load brightness, contrast, ROI, and checkbox settings from a JSON file."""
    try:
        with open(SETTINGS_FILE, "r") as f:
            settings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        settings = {}

    # Ustaw domyślne wartości, jeśli nie istnieją
    settings.setdefault("camera_mode", 2)
    settings.setdefault("camera_width", 1920)
    settings.setdefault("camera_height", 1080)
    settings.setdefault("brightness", 0.0)
    settings.setdefault("contrast", 0.0)
    settings.setdefault("grayscale", False)
    settings.setdefault("negative", False)
    settings.setdefault("minArea", 50)
    settings.setdefault("maxArea", 150)
    settings.setdefault("roi_width", 300)
    settings.setdefault("roi_height", 100)
    settings.setdefault("small_roi_size", 50)

    return settings

def save_settings(camera_mode, camera_width, camera_height,
                  brightness, contrast, grayscale, negative,
                  min_area, max_area, roi_width, roi_height,
                  small_roi_size):

    """Save brightness, contrast, ROI, and checkbox settings to a JSON file."""
    settings = {
        "camera_mode": camera_mode,
        "camera_width": camera_width,
        "camera_height": camera_height,
        "brightness": brightness,
        "contrast": contrast,
        "grayscale": grayscale,
        "negative": negative,
        "minArea": min_area,
        "maxArea": max_area,
        "roi_width": roi_width,
        "roi_height": roi_height,
        "small_roi_size": small_roi_size
    }
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

