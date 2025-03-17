import os
import psutil

def list_files(startpath):
    files_list = []
    for root, dirs, files in os.walk(startpath):
        for file in files:
            file_path = os.path.join(root, file)
            files_list.append(file_path)
            print(len(files_list), file_path)
    return files_list

def get_drive_options():
    drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
    available_drives = []
    for drive in drives:
        usage = psutil.disk_usage(drive)
        if usage.used <= 10 * 1024 * 1024:  # 10MB in bytes
            available_drives.append(drive)
    return available_drives
1
if __name__ == "__main__":
    available_drives = get_drive_options()
    if not available_drives:
        print("No drives with less than 10MB used space found.")
    else:
        print("Available drives:")
        for i, drive in enumerate(available_drives):
            print(f"{i + 1}. {drive}")
        choice = int(input("Select a drive by number: ")) - 1
        if 0 <= choice < len(available_drives):
            files = list_files(available_drives[choice])
            to_delete = input("Enter the numbers of the files to delete, separated by commas: ")
            to_delete_indices = [int(x.strip()) - 1 for x in to_delete.split(",") if x.strip().isdigit()]
            for index in to_delete_indices:
                if 0 <= index < len(files):
                    os.remove(files[index])
                    print(f"Deleted: {files[index]}")
                else:
                    print(f"Invalid file number: {index + 1}")
        else:
            print("Invalid choice.")
