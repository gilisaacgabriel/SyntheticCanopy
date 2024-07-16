import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

MAX_WORKERS = 16  # Adjust based on your system's capabilities
BATCH_SIZE = 1000  # Number of files to process in each batch, adjust based on file size and memory usage

def move_files_batch(files_batch):
    for source, destination in files_batch:
        try:
            if not os.path.exists(os.path.dirname(destination)):
                os.makedirs(os.path.dirname(destination))
            shutil.move(source, destination)
            print(f"Moved {source} to {destination}")
        except Exception as e:
            print(f"Error moving {source} to {destination}: {e}")

def move_contents(source_directory, destination_directory):
    files_to_move = []
    for root, _, files in os.walk(source_directory):
        for file in files:
            source_file = os.path.join(root, file)
            relative_path = os.path.relpath(source_file, source_directory)
            dest_file = os.path.join(destination_directory, relative_path)
            files_to_move.append((source_file, dest_file))

    total_files = len(files_to_move)
    print(f"Total files to move: {total_files}")

    batches = [files_to_move[i:i + BATCH_SIZE] for i in range(0, total_files, BATCH_SIZE)]

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_batch = {executor.submit(move_files_batch, batch): batch for batch in batches}

        for future in as_completed(future_to_batch):
            try:
                future.result()
            except Exception as e:
                print(f"Batch failed with exception: {e}")

if __name__ == "__main__":
    source_directory = r"C:\Landsat-OneTenthDegSqs"
    destination_directory = r"I:\Landsat-OneTenthDegSqs"
    move_contents(source_directory, destination_directory)
