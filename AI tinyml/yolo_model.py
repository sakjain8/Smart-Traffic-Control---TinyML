import torch
import cv2
import pandas as pd
from pathlib import Path

import warnings
warnings.filterwarnings("ignore", category=FutureWarning, message=".*torch.cuda.amp.autocast.*")

# Load YOLOv5 model (pre-trained on COCO dataset)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# Define the vehicle classes to detect
vehicle_classes = ['car', 'motorcycle', 'bus', 'truck']

def detect_and_classify(image_path, save_dir, confidence_threshold=0.37):
    # Load the image
    img = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB for visualization

    # Perform object detection
    results = model(img)

    # Filter results for vehicle classes
    detections = results.pandas().xyxy[0]  # Get results as pandas DataFrame
    vehicle_detections = detections[detections['name'].isin(vehicle_classes)]

    # List to store bounding boxes and their confidence scores
    boxes_with_confidence = []

    # Dictionary to count vehicle classes
    vehicle_counts = {cls: 0 for cls in vehicle_classes}

    # Process and filter detections based on confidence threshold
    for _, row in vehicle_detections.iterrows():
        conf, cls = row['confidence'], row['name']
        if conf > confidence_threshold:
            x1, y1, x2, y2 = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
            label = f"{cls} {conf:.2f}"
            color = (0, 255, 0)  # Green for bounding boxes

            # Append bounding box and confidence to the list
            boxes_with_confidence.append({
                'class': cls,
                'confidence': conf,
                'bbox': [x1, y1, x2, y2]
            })

            # Count the detected class
            vehicle_counts[cls] += 1

            # Draw rectangle and label
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Save and display the result
    output_path = Path(save_dir) / Path(image_path).name
    cv2.imwrite(str(output_path), img)

    # Return the list of bounding boxes with confidence scores and vehicle counts
    return boxes_with_confidence, vehicle_counts

def process_images(folders, base_output_dir):
    # Collect and sort image paths by filename (ensure they are processed in order: 1.jpg, 2.jpg, etc.)
    images_in_folders = [sorted(folder.glob("*.jpg"), key=lambda x: int(x.stem)) for folder in folders]

    # Create output directories for each folder under the base output directory
    output_dirs = [base_output_dir / folder.name for folder in folders]

    for output_dir in output_dirs:
        output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize an index to track which image to process from each folder
    current_index = 0
    max_images = min(len(images) for images in images_in_folders)  # Ensure all folders have the same number of images

    # Create a DataFrame to store vehicle counts for each signal
    vehicle_counts_df = pd.DataFrame(columns=['Signal', 'Image', 'Car', 'Motorcycle', 'Bus', 'Truck'])

    # Process images interactively
    while current_index < max_images:
        for i, (folder_images, output_dir) in enumerate(zip(images_in_folders, output_dirs)):
            image_path = folder_images[current_index]
            _, vehicle_counts = detect_and_classify(str(image_path), str(output_dir))
            
            # Create a new row as a DataFrame
            new_row = pd.DataFrame({
                'Signal': [f'Redlight {i + 1}'],
                'Image': [image_path.name],
                'Car': [vehicle_counts['car']],
                'Motorcycle': [vehicle_counts['motorcycle']],
                'Bus': [vehicle_counts['bus']],
                'Truck': [vehicle_counts['truck']]
            })
            
            # Concatenate the new row with existing DataFrame
            vehicle_counts_df = pd.concat([vehicle_counts_df, new_row], ignore_index=True)
        
        current_index += 1

    # Save the counts to a CSV file
    output_csv = base_output_dir / 'vehicle_counts.csv'
    vehicle_counts_df.to_csv(output_csv, index=False)
    print(f"Vehicle counts saved to {output_csv}")
