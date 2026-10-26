from PIL import Image
import os

os.makedirs("static/icons", exist_ok=True)
sizes = [72, 96, 128, 144, 152, 192, 384, 512]

img = Image.open("static/icon.png") # your main logo

for size in sizes:
    resized = img.resize((size, size))
    resized.save(f"static/icons/launcher-icon-{size}x{size}.png")
    print(f"Created {size}x{size}")

print("Done!")
