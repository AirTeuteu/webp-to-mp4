import os
import subprocess
import shutil
from PIL import Image, ImageSequence

print("\033[92mInit...\033[0m")

# Paramètres
input_directory = os.getcwd()
output_format = "mp4"

def get_webp_fps(input_file_path):
    # Utiliser FFmpeg pour obtenir le framerate du fichier WebP
    result = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", "-of", "default=noprint_wrappers=1:nokey=1", input_file_path], capture_output=True, text=True)

    if result.returncode == 0:
        try:
            # Convertir le framerate en nombre à virgule flottante
            fps = eval(result.stdout)
            print(f"Framerate du fichier WebP ({input_file_path}): {fps} fps")
            return fps
        except (SyntaxError, TypeError):
            pass

    # En cas d'échec, retourner None pour indiquer qu'aucun FPS n'a été trouvé
    print(f"\033[91mAvertissement : Aucun FPS trouvé pour {input_file_path}.\033[0m")
    return None

def convert_webp_to_mp4(input_file_path, output_file_path):
    # Créer un répertoire temporaire pour stocker les images
    temp_image_dir = "temp_images_webp"
    os.makedirs(temp_image_dir, exist_ok=True)

    # Charger le fichier WebP et convertir en PNG avec Pillow
    img = Image.open(input_file_path)

    # Enregistrer chaque image individuellement avec le format de nommage correct
    for i, frame in enumerate(ImageSequence.Iterator(img)):
        frame.save(os.path.join(temp_image_dir, f"frame_{i + 1:05d}.png"), "PNG")

    # Obtenir le framerate du fichier WebP
    webp_fps = get_webp_fps(input_file_path)

    # Utiliser FFmpeg pour créer la vidéo à partir des images avec le framerate du fichier WebP
    if webp_fps is not None:
        subprocess.run(["ffmpeg", "-framerate", str(webp_fps), "-i", f"{temp_image_dir}/frame_%05d.png",
                        "-c:v", "libx264", "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
                        "-pix_fmt", "yuv420p", output_file_path])
    else:
        print(f"\033[91mConversion ignorée pour {input_file_path} en raison de l'absence de FPS.\033[0m")
    # Supprimer le répertoire temporaire des images
    shutil.rmtree(temp_image_dir)

for filename in os.listdir(input_directory):
    if filename.endswith(".webp"):
        input_file_path = os.path.join(input_directory, filename)
        output_file_path = os.path.join(input_directory, f"{os.path.splitext(filename)[0]}.{output_format}")
        print(f"\033[92mDébut de conversion de {filename}\033[0m")
        convert_webp_to_mp4(input_file_path, output_file_path)
        print(f"\033[92mConversion terminée pour {filename}\033[0m")

print("\033[92mToutes les conversions sont terminées.\033[0m")
