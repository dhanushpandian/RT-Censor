import cv2
import json
import numpy as np
from keras.models import load_model
from PIL import Image, ImageOps

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the Keras model
# model = load_model("converted_keras/keras_model.h5", compile=False)
model = load_model(r"C:\Users\91638\OneDrive\Desktop\Folder\Web-vid\converted_keras\keras_model.h5", compile=False)


# Load the labels (assuming labels.txt is in the same directory)
class_names = open(r"C:\Users\91638\OneDrive\Desktop\Folder\Web-vid\converted_keras\labels.txt", "r").readlines()

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
    
    return class_name, confidence_score

# Function to analyze the video and return timestamps with explicit content
def analyze_video_for_explicit_content(video_path):
    # Open video file
    cap = cv2.VideoCapture(video_path)
    
    # Store the timestamps of explicit content
    skip_times = []
    frame_rate = cap.get(cv2.CAP_PROP_FPS)  # Get frames per second
    frame_interval = int(frame_rate)  # Process 1 frame per second
    
    while cap.isOpened():
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Convert frame to image
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        # Analyze the frame for explicit content
        class_name, confidence_score = analyze_frame_for_nsfw(image)
        
        if class_name.lower() == "explicit" and confidence_score > 0.7:  # Threshold for explicit content
            timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000  # Convert milliseconds to seconds
            skip_times.append(timestamp)
        
        # Skip frames based on the frame_interval
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(cap.get(cv2.CAP_PROP_POS_FRAMES)) + frame_interval)
    
    cap.release()
    return skip_times
