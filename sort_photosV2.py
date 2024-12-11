import os
import face_recognition
import shutil
import dlib

# Paths
base_folder = os.getcwd()  # Get the current working directory
photos_folder = os.path.join(base_folder, "Photos")  # All your photos
reference_folder = r'C:\Users\micro\OneDrive\Desktop\test ing my programs files\Reference'  # Your reference images path
output_folder = os.path.join(base_folder, "output")  # Output folder to store sorted photos

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Load reference encodings with all faces
reference_encodings = {}
for person_name in os.listdir(reference_folder):
    person_path = os.path.join(reference_folder, person_name)
    if os.path.isdir(person_path):
        print(f"Loading reference images for {person_name}...")
        for image_file in os.listdir(person_path):
            image_path = os.path.join(person_path, image_file)
            print(f"Loading image: {image_path}")
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                if person_name not in reference_encodings:
                    reference_encodings[person_name] = []
                reference_encodings[person_name].extend(encodings)  # Add all encodings for the person
                print(f"Loaded {len(encodings)} encodings for {person_name}")

# Function to find best match from multiple encodings
def find_best_match(face_encoding, reference_encodings):
    best_match = None
    best_distance = float('inf')
    
    # Compare with each reference person
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
    
    # Only process .jpg images
    if photo_file.endswith(".jpg"):
        print(f"Processing photo: {photo_file}")
        image = face_recognition.load_image_file(photo_path)
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)

        print(f"Detected {len(face_locations)} face(s) in {photo_file}")
        
        # For each detected face, compare it with reference encodings
        for face_encoding in face_encodings:
            matched_person = find_best_match(face_encoding, reference_encodings)
            
            if matched_person:  # If a match is found
                # Create a folder for the matched person in the output folder
                person_folder = os.path.join(output_folder, matched_person)
                os.makedirs(person_folder, exist_ok=True)

                # Create the new photo name with the matched person's name
                new_photo_name = f"{matched_person}_{photo_file}"
                new_photo_path = os.path.join(person_folder, new_photo_name)

                # Rename and move the photo to the respective folder
                shutil.copy(photo_path, new_photo_path)
                print(f"Renamed and moved: {photo_file} -> {new_photo_name}")
                break  # Move on to the next photo after a match is found
            else:
                print(f"No match found for {photo_file}")

print("Photos sorted and renamed successfully!")

# Ask user to review and move files to the reference folders
user_input = input("Do you want to move the sorted photos to the reference folders? (yes/no): ").strip().lower()

if user_input == 'yes':
    # Move the files back to the reference folders
    for person_name in os.listdir(output_folder):
        person_folder = os.path.join(output_folder, person_name)
        if os.path.isdir(person_folder):
            # Move files to the respective reference folder
            for photo_file in os.listdir(person_folder):
                photo_path = os.path.join(person_folder, photo_file)
                reference_person_folder = os.path.join(reference_folder, person_name)
                os.makedirs(reference_person_folder, exist_ok=True)
                shutil.move(photo_path, os.path.join(reference_person_folder, photo_file))

            # Optionally, you can remove the empty person folder from output
            os.rmdir(person_folder)

    print("Files have been moved to the reference folders.")
else:
    print("You chose not to move the files to the reference folders. The output files remain in the output folder.")