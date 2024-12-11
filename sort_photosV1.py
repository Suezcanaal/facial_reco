import os
import face_recognition
import shutil

# Paths
base_folder = os.getcwd()  # Get the current working directory
photos_folder = os.path.join(base_folder, "Photos")  # Folder containing all photos
reference_folder = r"C:\Users\micro\OneDrive\Desktop\Image Reconize and seperate ML Models\Reference"  # Reference images folder
output_folder = os.path.join(base_folder, "output")  # Output folder to store sorted photos

# Ensure folders exist
if not os.path.exists(photos_folder):
    raise FileNotFoundError(f"Photos folder not found: {photos_folder}")
if not os.path.exists(reference_folder):
    raise FileNotFoundError(f"Reference folder not found: {reference_folder}")

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Load reference encodings
reference_encodings = {}
for person_name in os.listdir(reference_folder):
    person_path = os.path.join(reference_folder, person_name)
    if os.path.isdir(person_path):
        print(f"Loading reference images for {person_name}...")
        for image_file in os.listdir(person_path):
            image_path = os.path.join(person_path, image_file)
            print(f"Loading image: {image_path}")
            try:
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    if person_name not in reference_encodings:
                        reference_encodings[person_name] = []
                    reference_encodings[person_name].extend(encodings)
                    print(f"Loaded {len(encodings)} encodings for {person_name}")
            except Exception as e:
                print(f"Error processing {image_path}: {e}")

# Function to find the best match
def find_best_match(face_encoding, reference_encodings):
    best_match = None
    best_distance = float('inf')
    
    for person_name, encodings in reference_encodings.items():
        for encoding in encodings:
            distance = face_recognition.face_distance([encoding], face_encoding)[0]
            if distance < best_distance:
                best_distance = distance
                best_match = person_name
    
    return best_match

# Process photos in the "Photos" folder
for photo_file in os.listdir(photos_folder):
    photo_path = os.path.join(photos_folder, photo_file)
    if photo_file.lower().endswith((".jpg", ".jpeg", ".png")):  # Allow multiple image formats
        print(f"Processing photo: {photo_file}")
        try:
            image = face_recognition.load_image_file(photo_path)
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)

            print(f"Detected {len(face_locations)} face(s) in {photo_file}")
            
            for face_encoding in face_encodings:
                matched_person = find_best_match(face_encoding, reference_encodings)
                
                if matched_person:
                    person_folder = os.path.join(output_folder, matched_person)
                    os.makedirs(person_folder, exist_ok=True)

                    new_photo_name = f"{matched_person}_{photo_file}"
                    new_photo_path = os.path.join(person_folder, new_photo_name)

                    shutil.copy(photo_path, new_photo_path)
                    print(f"Moved: {photo_file} -> {new_photo_name}")
                    break
                else:
                    print(f"No match found for {photo_file}")
        except Exception as e:
            print(f"Error processing {photo_file}: {e}")

print("Photos sorted and renamed successfully!")
