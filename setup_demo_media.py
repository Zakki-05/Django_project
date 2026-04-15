import os
import shutil

# Create media directory structure
media_dir = r"d:\Django_project\media\staff_images"
os.makedirs(media_dir, exist_ok=True)

# Path to the generated image
generated_image = r"C:\Users\ELCOT\.gemini\antigravity\brain\8fd06d44-9006-4d77-bb16-2fde36ef89a0\professional_doctor_profile_1776242939435.png"

# Target path
target_path = os.path.join(media_dir, "doctor_demo.png")

# Copy the image
try:
    shutil.copy(generated_image, target_path)
    print(f"Copied image to {target_path}")
except Exception as e:
    print(f"Error copying image: {e}")
