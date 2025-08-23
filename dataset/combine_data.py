import os
import pandas as pd

def create_master_csv(faceforensics_path, celebd_df_path, output_path):
    """
    Unifies metadata from FaceForensics++ and Celeb-DF into a single CSV.

    Args:
        faceforensics_path (str): Path to the FaceForensics++ main folder.
        celebd_df_path (str): Path to the Celeb-DF main folder.
        output_path (str): Path to save the master CSV.
    """
    all_videos = []

    # Process FaceForensics++
    print("Processing FaceForensics++ data...")
    ff_subfolders = ['DeepFakeDetection', 'Deepfakes', 'Face2Face', 'FaceShifter', 'FaceSwap', 'NeuralTextures', 'original']
    for folder in ff_subfolders:
        label = 0 if folder == 'original' else 1
        video_dir = os.path.join(faceforensics_path, folder)
        
        if not os.path.exists(video_dir):
            print(f"Warning: Folder not found at {video_dir}. Skipping.")
            continue

        for filename in os.listdir(video_dir):
            if filename.endswith('.mp4'):
                video_path = os.path.join(video_dir, filename)
                all_videos.append({'video_path': video_path, 'label': label})

    # Process Celeb-DF
    print("Processing Celeb-DF data...")
    celebd_df_txt_path = os.path.join(celebd_df_path, 'new_celebd_df_list.txt')
    
    if os.path.exists(celebd_df_txt_path):
        with open(celebd_df_txt_path, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            parts = line.strip().split()
            label = int(parts[0])
            video_relative_path = parts[1] 

            video_path = os.path.join(celebd_df_path, video_relative_path)
            all_videos.append({'video_path': video_path, 'label': label})
    else:
        print(f"Warning: List_of_testing_videos.txt not found at {celebd_df_txt_path}. Skipping Celeb-DF.")

    # Create and save the master DataFrame
    master_df = pd.DataFrame(all_videos)
    master_df.to_csv(output_path, index=False)
    print(f"Master metadata created with {len(master_df)} videos and saved to {output_path}")

# Example Usage:
# Update these paths to match your directory structure

FACEFORENSICS_DIR = r'D:\minor project\dataset\FaceForensics++_C23'
CELEBDF_DIR = r'D:\minor project\dataset\Celeb-DF-v2'
MASTER_CSV_PATH = r'D:\minor project\dataset\master_data.csv'

create_master_csv(FACEFORENSICS_DIR, CELEBDF_DIR, MASTER_CSV_PATH)