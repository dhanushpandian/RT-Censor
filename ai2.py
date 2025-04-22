from keras.models import load_model  # TensorFlow is required for Keras to work
from PIL import Image, ImageOps  # Install pillow instead of PIL
import numpy as np
import openai

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the Keras model
model = load_model(r"Web-vid\converted_keras\keras_model.h5", compile=False)

# Load the labels (assuming labels.txt is in the same directory)
class_names = open(r"Web-vid\converted_keras\labels.txt", "r").readlines()

# Create the array of the right shape to feed into the keras model
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

# Function to analyze a single frame for explicit content using Keras model
def analyze_frame_for_nsfw(image_path):
    # Load the image
    image = Image.open(image_path).convert("RGB")
    
    # Resize and crop image to fit 224x224 size
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    
    # Convert image to numpy array
    image_array = np.asarray(image)
    
    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    
    # Load the image into the model input array
    data[0] = normalized_image_array

    # Predict using the model
    prediction = model.predict(data)
    index = np.argmax(prediction)
    class_name = class_names[index].strip()  # Assuming the labels file has one class name per line
    confidence_score = prediction[0][index]
    
    print("Class:", class_name, "Confidence Score:", confidence_score)
    
    return class_name, confidence_score

# Example usage for a frame (replace with actual frame extraction code)
image_path = r"Web-vid\potos\body.jpg"
class_name, confidence_score = analyze_frame_for_nsfw(image_path)

# If you want to use OpenAI for explicit content, you can also integrate this method with your existing system
# For example, calling OpenAI's API after frame analysis for further processing (if needed).
