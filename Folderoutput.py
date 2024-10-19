import os

def list_files_in_folder(folder_path):
    try:
        filenames = os.listdir(folder_path)
        for filename in filenames:
            print(filename)
    except FileNotFoundError:
        print(f"Error: The folder '{folder_path}' does not exist.")
    except PermissionError:
        print(f"Error: Permission denied to access '{folder_path}'.")

if __name__ == "__main__":
    folder_path = input("Enter the path to the folder: ")
    list_files_in_folder(folder_path)
