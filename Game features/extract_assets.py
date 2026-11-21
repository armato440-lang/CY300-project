
import zipfile
import os

# Folder containing your ZIP files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Destination folders
IMAGE_DIR = os.path.join(BASE_DIR, "assets", "images")
SOUND_DIR = os.path.join(BASE_DIR, "assets", "sounds")

# Create folders if they do not exist
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(SOUND_DIR, exist_ok=True)

# Extract image files
def extract_images(zip_name):
    zip_path = os.path.join(BASE_DIR, zip_name)

    with zipfile.ZipFile(zip_path, "r") as archive:
        for file in archive.namelist():
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                filename = os.path.basename(file)

                if filename:
                    destination = os.path.join(IMAGE_DIR, filename)

                    with archive.open(file) as source:
                        with open(destination, "wb") as target:
                            target.write(source.read())

                    print("Image extracted:", filename)


# Extract sound files
def extract_sounds(zip_name):
    zip_path = os.path.join(BASE_DIR, zip_name)

    with zipfile.ZipFile(zip_path, "r") as archive:
        for file in archive.namelist():
            if file.lower().endswith((".wav", ".ogg", ".mp3")):
                filename = os.path.basename(file)

                if filename:
                    destination = os.path.join(SOUND_DIR, filename)

                    with archive.open(file) as source:
                        with open(destination, "wb") as target:
                            target.write(source.read())

                    print("Sound extracted:", filename)


# Extract from your three Kenney packs
extract_images("kenney_platformer-characters.zip")

extract_sounds("kenney_impact-sounds.zip")
extract_sounds("kenney_voiceover-pack-fighter.zip")

print("Asset extraction complete!")
