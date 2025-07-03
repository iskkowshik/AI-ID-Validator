import cv2
import numpy as np

def crop_id_card(input_path, output_path="cropped_id.jpg"):
    # Read the image
    image = cv2.imread(input_path)
    if image is None:
        print("❌ Could not read the image.")
        return

    # Resize for better handling
    ratio = 800.0 / image.shape[1]
    dim = (800, int(image.shape[0] * ratio))
    resized = cv2.resize(image, dim)

    # Convert to grayscale
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    # Blur to remove noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Edge detection
    edged = cv2.Canny(blurred, 50, 200)

    # Find contours
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours by area (largest first)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Loop through contours to find a 4-cornered shape (likely ID card)
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            cropped = resized[y:y+h, x:x+w]
            cv2.imwrite(output_path, cropped)
            print(f"✅ Cropped ID card saved as '{output_path}'")
            return

    print("❌ Could not find a rectangular ID card in the image.")

# === Usage ===
input_image_path = "20250528_130415.jpg"  # Replace with your image path
crop_id_card(input_image_path)
