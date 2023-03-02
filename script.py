import os
import sys
import shutil
import hashlib
import time
import argparse


import os
import sys
import shutil
import hashlib
import time
import argparse
import signal


def synchronize_folders(source_path, replica_path, log_file_path, interval):
    def signal_handler(sig, frame):
        print("\nSynchronization interrupted by user. Exiting...")
        exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    if not os.path.exists(replica_path):
        print(f"Replica folder {replica_path} does not exist. Creating...")
        os.makedirs(replica_path)

    while True:
        try:
            print("Starting synchronization...")

            # iterate through source folder
            for root, dirs, files in os.walk(source_path):
                # create directories in replica folder if they don't exist
                for directory in dirs:
                    source_dir = os.path.join(root, directory)
                    replica_dir = os.path.join(replica_path, os.path.relpath(source_dir, source_path))
                    if not os.path.exists(replica_dir):
                        print(f"Creating directory {replica_dir}")
                        os.makedirs(replica_dir)

                # copy files to replica folder
                for file in files:
                    source_file = os.path.join(root, file)
                    replica_file = os.path.join(replica_path, os.path.relpath(source_file, source_path))
                    source_checksum = hashlib.md5(open(source_file, "rb").read()).hexdigest()
                    if os.path.exists(replica_file):
                        replica_checksum = hashlib.md5(open(replica_file, "rb").read()).hexdigest()
                        if source_checksum != replica_checksum:
                            print(f"Copying modified file {source_file} to {replica_file}")
                            shutil.copy2(source_file, replica_file)
                            with open(log_file_path, "a") as log_file:
                                log_file.write(f"Copied modified file {source_file} to {replica_file}\n")
                    else:
                        print(f"Copying new file {source_file} to {replica_file}")
                        shutil.copy2(source_file, replica_file)
                        with open(log_file_path, "a") as log_file:
                            log_file.write(f"Copied new file {source_file} to {replica_file}\n")

            # remove files from replica folder if they don't exist in source folder
            for root, dirs, files in os.walk(replica_path):
                for file in files:
                    replica_file = os.path.join(root, file)
                    source_file = os.path.join(source_path, os.path.relpath(replica_file, replica_path))
                    if not os.path.exists(source_file):
                        print(f"Removing deleted file {replica_file}")
                        os.remove(replica_file)
                        with open(log_file_path, "a") as log_file:
                            log_file.write(f"Removed deleted file {replica_file}\n")

                # remove directories from replica folder if they don't exist in source folder
                for directory in dirs:
                    replica_dir = os.path.join(root, directory)
                    source_dir = os.path.join(source_path, os.path.relpath(replica_dir, replica_path))
                    if not os.path.exists(source_dir):
                        print(f"Removing deleted directory {replica_dir}")
                        shutil.rmtree(replica_dir)
                        with open(log_file_path, "a") as log_file:
                            log_file.write(f"Removed deleted directory {replica_dir}\n")

            print("Synchronization complete.")
            with open(log_file_path, "a") as log_file:
                log_file.write("Synchronization complete.\n")

            time.sleep(interval)

        except Exception as e:
            print(f"An error occurred: {e}")
            with open(log_file_path, "a") as log_file:
                current_time = time.strftime('%Y-%m-%d %H:%M:%S')
                log_file.write(f"{current_time}: An error occurred: {e}\n")
                if "replica_file" in locals():
                    log_file.write(f"{current_time}: Error occurred on file: {replica_file}\n")
                elif "source_file" in locals():
                    log_file.write(f"{current_time}: Error occurred on file: {source_file}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synchronize two folders")
    parser.add_argument("source", type=str, help="source folder path")
    parser.add_argument("replica", type=str, help="replica folder path")
    parser.add_argument("log", type=str, help="log file path")
    parser.add_argument("interval", type=int, help="synchronization interval in seconds")

    args = parser.parse_args()

    source_path = args.source
    replica_path = args.replica
    log_file_path = args.log
    interval = args.interval

    synchronize_folders(source_path, replica_path, log_file_path, interval)

   
