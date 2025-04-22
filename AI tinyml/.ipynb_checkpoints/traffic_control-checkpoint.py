from pathlib import Path
import pandas as pd
import time
from tqdm import tqdm
from termcolor import colored
from yolo_model import process_images  # Import the function to process images from the model file
import os

# Define the path to the CSV file
csv_file_path = 'C:\\Users\\saksh\\Desktop\\project\\outputs\\vehicle_counts.csv'

# Check if the CSV file exists
if not os.path.exists(csv_file_path):
    # Create a DataFrame with default content if the file doesn't exist
    data = {
        'Image': [],         # Image names or file names
        'Signal': [],        # Signal names (e.g., Redlight 1, Redlight 2)
        'Car': [],           # Vehicle count for cars
        'Motorcycle': [],    # Vehicle count for motorcycles
        'Bus': [],           # Vehicle count for buses
        'Truck': []          # Vehicle count for trucks
    }
    
    # Create an empty DataFrame with the default content
    df = pd.DataFrame(data)
    
    # Save the empty DataFrame to the CSV file
    df.to_csv(csv_file_path, index=False)
    print(f"CSV file created at {csv_file_path} with default content.")
else:
    # Load the CSV file if it already exists
    df = pd.read_csv(csv_file_path)
    print(f"CSV file loaded from {csv_file_path}.")

# Function to calculate green light duration
def calculate_green_time(row):
    return 1 * row['Car'] + 1 * row['Motorcycle'] + 1 * row['Bus'] + 1 * row['Truck']

# Function to display countdown with tqdm
def countdown_timer(seconds, light_color, signal_name):
    for remaining in tqdm(range(seconds, 0, -1), desc=f"{colored(signal_name, 'cyan')} ({colored(light_color, 'green' if light_color == 'GREEN' else 'yellow')})", ncols=75):
        time.sleep(1)

# Simulate traffic lights
def simulate_traffic_lights(df):
    rounds = df['Image'].unique()  # Get unique rounds (e.g., 1.jpg, 2.jpg)
    redlights = df['Signal'].unique()  # Get unique signals (e.g., Redlight 1, Redlight 2)
    
    for round_ in rounds:
        print(f"\n{colored(f'Starting Round: {round_}', 'blue', attrs=['bold'])}\n")
        for redlight in redlights:
            # Filter the data for the current round and redlight
            row = df[(df['Image'] == round_) & (df['Signal'] == redlight)].iloc[0]
            green_time = calculate_green_time(row)
            
            # Simulate green light
            print(f"{colored(redlight, 'cyan')} is {colored('GREEN', 'green')} for {green_time} seconds.")
            countdown_timer(green_time, "GREEN", redlight)
            
            # Simulate yellow light
            print(f"{colored(redlight, 'cyan')} is {colored('YELLOW', 'yellow')} for 5 seconds.")
            countdown_timer(5, "YELLOW", redlight)
            
        print(f"{colored(f'Round {round_} completed.', 'blue', attrs=['bold'])}\n")

# Define the folders containing the images
folders = [
    Path('C:\\Users\\saksh\\Desktop\\project\\Inputs\\Redlight 1\\'),
    Path('C:\\Users\\saksh\\Desktop\\project\\Inputs\\Redlight 2\\'),
    Path('C:\\Users\\saksh\\Desktop\\project\\Inputs\\Redlight 3\\'),
    Path('C:\\Users\\saksh\\Desktop\\project\\Inputs\\Redlight 4\\')
]

# Ensure each folder exists
folders = [Path(folder) for folder in folders]
for folder in folders:
    assert folder.exists(), f"Folder {folder} does not exist."

# Define the base output directory
base_output_dir = Path("C:\\Users\\saksh\\Desktop\\project\\outputs\\")

# Call the function to process images and get the CSV file with vehicle counts
process_images(folders, base_output_dir)

# Load the processed CSV
df = pd.read_csv(base_output_dir / 'vehicle_counts.csv')

# Run the simulation
simulate_traffic_lights(df)
