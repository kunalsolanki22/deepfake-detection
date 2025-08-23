import os
import cv2
import pandas as pd
from mtcnn import MTCNN
import shutil
import multiprocessing

# MTCNN face detector setup
detector = MTCNN()

def process_single_video(video_data):
    """
    Processes a single video by extracting, cropping, and saving faces.
    This function is designed to be run in parallel by a multiprocessing pool.
    
    Args:
        video_data (tuple): A tuple containing the video's path and its label.
    """
    video_path, label = video_data
    
    # Extract a unique video ID from the filename
    video_id = os.path.basename(video_path).split('.')[0]
    
    # Define the output directory based on the video's label and ID
    output_base_dir = r'D:\minor project\dataset\processed_faces'
    label_dir = 'real' if label == 0 else 'fake'
    output_dir = os.path.join(output_base_dir, label_dir, video_id)
    
    try:
        # Create the output directory for this specific video
        os.makedirs(output_dir, exist_ok=True)
        
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        
        while cap.isOpened() and frame_count < 30: # Process up to 30 frames
            ret, frame = cap.read()
            if not ret:
                break
            
            # --- MTCNN Face Detection ---
            # It's better to use the RGB frame for MTCNN
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = detector.detect_faces(rgb_frame)
            
            if len(faces) > 0:
                face = faces[0]['box'] # Get the bounding box of the first face
                x, y, width, height = face
                
                # Convert MTCNN's [x, y, width, height] format to the required [x1, y1, x2, y2]
                x1, y1, x2, y2 = x, y, x + width, y + height

                # Add a margin to the bounding box
                margin = 50
                x1 = max(0, x1 - margin)
                y1 = max(0, y1 - margin)
                x2 = min(frame.shape[1], x2 + margin)
                y2 = min(frame.shape[0], y2 + margin)
                
                cropped_face = frame[y1:y2, x1:x2]
                
                # Resize to target size (256x256)
                resized_face = cv2.resize(cropped_face, (256, 256))
                
                # Save the image
                output_path = os.path.join(output_dir, f'frame_{frame_count:03d}.jpg')
                cv2.imwrite(output_path, resized_face)
                frame_count += 1
        
        cap.release()
        print(f"Processed {frame_count} frames from {video_id}")
        
    except Exception as e:
        print(f"Error processing video {video_id}: {e}")
        # Clean up the directory if there was an error to avoid corrupted output
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

def main():
    """
    The main function to orchestrate the multiprocessing.
    """
    # Define paths
    MASTER_CSV_PATH = r'D:\minor project\dataset\master_data.csv'
    OUTPUT_IMAGES_DIR = r'D:\minor project\dataset\processed_faces'
    
    # Clean up the output directory from any previous runs
    if os.path.exists(OUTPUT_IMAGES_DIR):
        shutil.rmtree(OUTPUT_IMAGES_DIR)
    
    # Create the main output subfolders
    os.makedirs(os.path.join(OUTPUT_IMAGES_DIR, 'real'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_IMAGES_DIR, 'fake'), exist_ok=True)
    
    # Read the metadata CSV
    df = pd.read_csv(MASTER_CSV_PATH)
    
    # Prepare the list of videos for the multiprocessing pool
    video_list = list(zip(df['video_path'], df['label']))
    
    # Use all available CPU cores for parallel processing
    num_cores = multiprocessing.cpu_count()
    print(f"Starting parallel processing on {num_cores} cores.")
    
    with multiprocessing.Pool(processes=num_cores) as pool:
        # Use 'pool.map' to apply the 'process_single_video' function to each video
        pool.map(process_single_video, video_list)
        
    print("\nAll video preprocessing complete.")

if __name__ == "__main__":
    main()