# from PIL import Image
# import os

# # Define los formatos para cada red
# TARGET_SIZES = {
#     'instagram': (1080, 1080),
#     'tiktok': (1080, 1920),
#     'facebook': (1200, 1500),
#     'twitter': (1200, 675),
# }

# def process_image(input_path, output_base_dir, filename):
#     img = Image.open(input_path).convert('RGB')

#     for platform, size in TARGET_SIZES.items():
#         target_w, target_h = size
#         img_copy = img.copy()

#         # Calcula escala proporcional
#         img_copy.thumbnail((target_w, target_h), Image.LANCZOS)
#         resized_w, resized_h = img_copy.size

#         # Crear fondo negro y pegar imagen centrada
#         background = Image.new('RGB', (target_w, target_h), (0, 0, 0))
#         offset_x = (target_w - resized_w) // 2
#         offset_y = (target_h - resized_h) // 2
#         background.paste(img_copy, (offset_x, offset_y))

#         # Crear carpeta si no existe
#         platform_dir = os.path.join(output_base_dir, platform)
#         os.makedirs(platform_dir, exist_ok=True)

#         # Guardar la imagen
#         output_path = os.path.join(platform_dir, filename)
#         background.save(output_path, format='JPEG', quality=95)

from PIL import Image
import os

# Resoluciones por red social
SOCIAL_SIZES = {
    'instagram': (1080, 1080),
    'tiktok': (1080, 1920),
    'facebook': (1080, 1350),
    'x': (1200, 1500)  # Se adapta mejor al feed si es vertical
}

def process_image(input_path, output_folder, filename, networks):
    from PIL import Image, ImageOps

    image = Image.open(input_path)
    image = image.convert("RGB")

    formats = {
        "instagram": (1080, 1350),
        "tiktok": (1080, 1920),
        "facebook": (1200, 630),
        "x": (1600, 900),
    }

    for network in networks:
        if network in formats:
            target_size = formats[network]
            # Centrar la imagen sin deformar y con fondo negro
            img_with_bg = Image.new("RGB", target_size, (0, 0, 0))
            img_resized = ImageOps.contain(image, target_size)
            offset = ((target_size[0] - img_resized.width) // 2, (target_size[1] - img_resized.height) // 2)
            img_with_bg.paste(img_resized, offset)

            output_dir = os.path.join(output_folder, network)
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, filename)
            img_with_bg.save(output_path, format="JPEG", quality=95)
