import os
import re
import csv 

def clean_and_organize_scripts(file_path, output_dir):
    # Create base output directory if it doesn't exist
                
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Read the full script file
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    season_data = {}
    current_season = None
    current_episode = None
    current_episode_lines = []
    
    # Regular expression pattern to match "SxEy - num OUT OF 180"
    episode_pattern = re.compile(r'S(\d+)E(\d+)\s*-\s*(\d+)\s*OUT OF 180')

    for line in lines:
        # Skip empty lines and lines with only "=" symbols
        if line.strip() == '' or line.strip() == '===========================================================================':
            continue

        # Check if the line matches the "SxEy - num OUT OF 180" pattern
        match = episode_pattern.match(line)
        if match:
            # If there's data from the previous episode, store it
            if current_season and current_episode_lines:
                season_data[current_season].append(('Episode_' + current_episode, ''.join(current_episode_lines)))
                current_episode_lines = []

            # Extract season and episode information
            # it can be 01 or 1 so we need to convert it to 01
            season = match.group(1)  # Season number (e.g., '1' for S1)
            episode = match.group(2)  # Episode number (e.g., '1' for E1)
            season = season.zfill(2)
            episode = episode.zfill(2)
            current_season = f"Season_{season}"
            current_episode = episode

            # Initialize the season folder if not already present
            if current_season not in season_data:
                season_data[current_season] = []

            # Start recording the new episode
            current_episode_lines.append(line)

        else:
            # Add lines to the current episode
            current_episode_lines.append(line)

        # Detect the end of the episode with '[End]'
        if '[End]' in line:
            season_data[current_season].append(('Episode_' + current_episode, ''.join(current_episode_lines)))
            current_episode_lines = []

    # Write each season's episodes into separate folders
    for season, episodes in season_data.items():
        season_folder = os.path.join(output_dir, season)
        if not os.path.exists(season_folder):
            os.makedirs(season_folder)

        for episode_name, episode_content in episodes:
            episode_file = os.path.join(season_folder, f'{episode_name}.txt')
            with open(episode_file, 'w', encoding='utf-8') as ep_file:
                ep_file.write(episode_content)
            print('Episode:', episode_name, 'written to:', episode_file)

    print(f"Scripts have been cleaned and organized into {output_dir}.")


def read_episode_info(csv_file):
    """Reads episode information from CSV and returns a dictionary keyed by SEID (SxEy)."""
    episode_info = {}
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Get SEID (e.g., S01E01)
            seid = row['SEID']
            # Store episode information in a dictionary
            episode_info[seid] = {
                'title': row['Title'],
                'air_date': row['Air Date'],
                'writers': row['Writers'],
                'director': row['Director']
            }
    return episode_info

def prepend_episode_info(episode_file, episode_data):
    """Prepends the episode information to the episode file."""
    # Read the existing content of the episode file
    with open(episode_file, 'r', encoding='utf-8') as file:
        episode_content = file.read()

    # Create the info to prepend
    episode_info_text = (
        f"Title: {episode_data['title']}\n"
        f"Air Date: {episode_data['air_date']}\n"
        f"Writers: {episode_data['writers']}\n"
        f"Director: {episode_data['director']}\n\n"
    )

    # Write the episode info followed by the episode content back to the file
    with open(episode_file, 'w', encoding='utf-8') as file:
        file.write(episode_info_text + episode_content)

def update_episode_files_with_info(episode_info, base_directory):
    """Updates all episode files in the season folders with episode info from CSV."""
    # Iterate through each season folder in the base directory
    for season_folder in os.listdir(base_directory):
        season_path = os.path.join(base_directory, season_folder)

        if os.path.isdir(season_path):
            # Iterate through each episode file in the season folder
            for episode_file in os.listdir(season_path):
                if episode_file.endswith('.txt'):
                    # Extract SEID from the filename (assuming format Episode_x.txt)
                    episode_number = episode_file.split('_')[1].split('.')[0]
                    seid = f"S{season_folder.split('_')[1].zfill(2)}E{episode_number.zfill(2)}"

                    # If episode info exists for this SEID, prepend it
                    if seid in episode_info:
                        episode_file_path = os.path.join(season_path, episode_file)
                        prepend_episode_info(episode_file_path, episode_info[seid])

    print(f"Episode files have been updated with information from {csv_file}.")

# File and directory setup
input_file = '/Users/michaelbest/Desktop/deep-learning-workshop/full_scripsts_sharon.txt'
output_directory = 'organized_scripts'

#clean_and_organize_scripts(input_file, output_directory)

# File paths
csv_file = 'episode_info.csv'
base_directory = 'organized_scripts'  # Folder containing season directories

# Read the episode info from the CSV
#episode_info = read_episode_info(csv_file)

# Update the episode files with the episode info
#update_episode_files_with_info(episode_info, base_directory)

#clean episode 04 in season 01 , remove empty lines 
def clean_episode(file_path):
    # Read the episode file
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    for line in lines:
        if line.strip() == '':
            lines.remove(line)
    # Write the cleaned content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(''.join(lines))
    print(f"Episode 03 in Season 02 has been cleaned.")

clean_episode('organized_scripts/Season_02/Episode_03.txt')
    



    
    
    
