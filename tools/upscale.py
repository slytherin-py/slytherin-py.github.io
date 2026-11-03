"""Upscales a photo 4x with OpenCV's EDSR super-resolution model, then exports web sizes.

    pip install opencv-contrib-python
    python tools/upscale.py <input.jpg> <EDSR_x4.pb> <output-name>

EDSR_x4.pb: https://github.com/Saafke/EDSR_Tensorflow (the model OpenCV's dnn_superres docs use).
Writes assets/<output-name>.webp (1200px) and assets/<output-name>.jpg (fallback).
"""
import os, sys
import cv2
from PIL import Image, ImageEnhance, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src, model, name = sys.argv[1:4]

sr = cv2.dnn_superres.DnnSuperResImpl_create()
sr.readModel(model)
sr.setModel("edsr", 4)
img = cv2.imread(src)
up = sr.upsample(img)
up = cv2.fastNlMeansDenoisingColored(up, None, 3, 3, 7, 21)  # soften JPEG noise the upscale exaggerates

im = Image.fromarray(cv2.cvtColor(up, cv2.COLOR_BGR2RGB))
im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=3))
im = ImageEnhance.Contrast(im).enhance(1.04)
print("upscaled", img.shape[1::-1], "->", im.size)

w = 1200
if im.width > w:
    im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
im.save(os.path.join(ROOT, "assets", name + ".webp"), quality=86)
im.save(os.path.join(ROOT, "assets", name + ".jpg"), quality=86, optimize=True, progressive=True)
print("wrote", name, im.size)
