import os
import cv2
import numpy as np
import joblib
from skimage.feature import hog
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# Load dataset
def load_chess_pieces_data(data_folder):
    X = []
    y = []
    piece_labels = ["Bishop", "empty", "King", "Knight", "Pawn", "Queen", "Rook"]
    
    for label in piece_labels:
        folder_path = os.path.join(data_folder, label)
        if not os.path.exists(folder_path):
            print(f"Warning: Folder {folder_path} does not exist. Skipping.")
            continue
        
        for filename in os.listdir(folder_path):
            img_path = os.path.join(folder_path, filename)
            img = cv2.imread(img_path)
            if img is not None:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            if img is not None:
                img_resized = cv2.resize(img, (64, 64))
                features = hog(img_resized, orientations=9, pixels_per_cell=(8, 8), cells_per_block=(2, 2), block_norm='L2-Hys')
                X.append(features)
                y.append(label)
    
    return np.array(X), np.array(y)

# Train SVM model
def train_svm_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training SVM model...")
    svm = SVC(kernel='linear', probability=True)
    svm.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = svm.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    return svm

# Save trained model
def save_model(model, model_path):
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    data_folder = r"C:\GitHubRepos\MyPythonScripts\ChessOpener\templates"
    model_path = r"C:\GitHubRepos\MyPythonScripts\ChessOpener\chess_piece_svm_model.pkl"

    # Load data
    X, y = load_chess_pieces_data(data_folder)
    if len(X) == 0 or len(y) == 0:
        print("No data found. Please make sure the dataset is available.")
    else:
        # Train model
        svm_model = train_svm_model(X, y)
        
        # Save model
        save_model(svm_model, model_path)
