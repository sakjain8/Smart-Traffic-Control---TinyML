import pandas as pd
import time
from tqdm import tqdm
from termcolor import colored

# Load the CSV file
df = pd.read_csv('C:\\Users\\saksh\\Desktop\\project\\outputs\\vehicle_counts.csv')

# Function to calculate green light duration
def calculate_green_time(row):
    return 1 * row['Car'] + 1 * row['Motorcycle'] + 2 * row['Bus'] + 2 * row['Truck']

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

# Run the simulation
simulate_traffic_lights(df)
