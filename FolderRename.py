import os

def rename_folder_contents(folder_path, base_name):
    try:
        # Get a list of all files in the folder
        files = os.listdir(folder_path)
        files = [f for f in files if os.path.isfile(os.path.join(folder_path, f))]

        # Iterate through files and rename them sequentially
        for index, file_name in enumerate(files, start=1):
            # Get the file extension
            _, file_extension = os.path.splitext(file_name)

            # Create the new file name
            new_name = f"{base_name}{index}{file_extension}"

            # Rename the file
            old_path = os.path.join(folder_path, file_name)
            new_path = os.path.join(folder_path, new_name)
            os.rename(old_path, new_path)

        print(f"Renamed {len(files)} files successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Prompt for user input
folder_path = input("Enter the path to your folder: ")
base_name = input("Enter the base name for the files: ")
rename_folder_contents(folder_path, base_name)
