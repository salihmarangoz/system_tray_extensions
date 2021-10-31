
"""
Downscales video to (18,6). If you want to use FFmpeg make sure using an interpolation identical to cv2.INTER_AREA
Usage: python3 video_play.py input.mp4 output.mp4
"""

import cv2
from tqdm import tqdm
import sys

target_dim = (18, 6)
cap_in = cv2.VideoCapture(sys.argv[1])
total_frames = int(cap_in.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap_in.get(cv2.CAP_PROP_FPS)
cap_out = cv2.VideoWriter(sys.argv[2],cv2.VideoWriter_fourcc(*'MPNG'), fps, target_dim)

print("You can press Ctrl+C whenever you want...")
try:
    for i in tqdm(range(total_frames)):
        if not cap_in.isOpened():
            break
        ret, frame = cap_in.read()
        if not ret:
            break

        img = cv2.resize(frame, target_dim, interpolation = cv2.INTER_AREA)
        cap_out.write(img)
except:
    cap_out.release()