import cv2
import numpy as np
from PIL import Image
from io import BytesIO

def t_coloring_split(img, output_prefix, parts=10):
    # Convert Django InMemoryUploadedFile to a NumPy array
    img_bytes = img.read()  # Read image file into bytes
    nparr = np.frombuffer(img_bytes, np.uint8)  # Convert to NumPy array
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # Decode image as OpenCV format

    if img_cv is None:
        raise ValueError("Invalid image format. Unable to process.")

    # Convert to grayscale
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # Compute histogram
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])

    # Find threshold values for 10 equal-intensity segments
    thresholds = np.linspace(0, 255, parts + 1).astype(int)  # Convert to integers

    output_files = []
    for i in range(parts):
        lower, upper = int(thresholds[i]), int(thresholds[i + 1])

        # Create a mask for pixels in the intensity range
        mask = cv2.inRange(gray, lower, upper)

        # Apply the mask to get the segmented image
        segmented = cv2.bitwise_and(img_cv, img_cv, mask=mask)

        # Convert to PIL Image and save
        segmented_pil = Image.fromarray(cv2.cvtColor(segmented, cv2.COLOR_BGR2RGB))
        output_filename = f"{output_prefix}_part_{i + 1}.png"
        segmented_pil.save(output_filename)
        output_files.append(output_filename)

    return output_files  # Return list of file paths
