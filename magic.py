import argparse
import os

import cv2
import numpy as np


# Parse command-line arguments
parser = argparse.ArgumentParser(
    description='Progressively overlays an image on a video captured with TikTok\'s verzerrer filter.')
parser.add_argument(
    'video', help='The source video file, captured using verzerrer filter.')
parser.add_argument('image', help='The image to overlay on the video.')
parser.add_argument(
    '--save', help='The output location. Default is current directory.', default='./')
args = parser.parse_args()

# Open input video stream
vidcap = cv2.VideoCapture(args.video)
success, image = vidcap.read()
height, width, _ = image.shape

if not os.path.exists(args.save):
    os.makedirs(args.save)

# Create output video stream of same resolution
outfile = f'{os.path.splitext(args.video)[0]}.mp4'
outfile = os.path.join(args.save, os.path.split(outfile)[-1])
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter(outfile, fourcc, 25, (width, height))

# Open overlay image
overlay = cv2.imread(args.image)
overlay = cv2.resize(overlay, (width, height))

# Apply overlay on each frame
while success:
    try:
        # Using blue channel, binarize the image
        _, _, b = cv2.split(image)
        _, mask = cv2.threshold(
            b, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY_INV)
        mask[:, 10:] = 0

        # Find out the first pixel of the blue line
        # and apply overlay above that line
        y = np.array(np.where(mask == 255))[0, 0]
        image[:y, :] = overlay[:y, :]
        out = image

        # Save result to video output stream
        video.write(out)

        # Read next frame
        success, image = vidcap.read()
    except Exception as ex:
        for _ in range(125):
            video.write(out)
        break

cv2.destroyAllWindows()
video.release()
