# README: rgb_kb_custom



## Modifying Presets

If you want to modify presets without breaking update function add a `.gitignore` file with only `*` inside into this folder (rgb_kb_custom).



## Preprocessing Videos

If you use a video directly CPU usage may be high because the RGB keyboard module will try to downscale it while animating. So, I recommend preprocessing the video before using daily.

```bash
# If you are using youtube-dl
youtube-dl -f 22 <video_url> # Just make sure you downloaded MP4
python video_play.py download.mp4 # test video on the keyboard

# If the video looks good, apply these steps to preprocess and lower CPU usage while animating:

# Use first 10 minutes and reduce fps to 20. These limits can be increased or removed, but may increase CPU usage
ffmpeg -i download.mp4 -t 600 -filter:v fps=20 reduced_fps.mp4

# Downscale image to (18,6). If you want to use FFmpeg make sure to use an interpolation same to the OpenCV INTER_AREA interpolation
python video_compress.py reduced_fps.mp4 final_video.mp4 
```



Credit goes to [Ambiefix](https://www.youtube.com/channel/UCnwLT9GEwbzfjPusVKtxacA) Youtube Channel for preset videos:

- `Aurora.mp4` -> https://www.youtube.com/watch?v=X6PLRiil2F4
- `Rainbow.mp4` -> https://www.youtube.com/watch?v=sTsO_NMjb3o
- `Spaghetti.mp4` -> https://www.youtube.com/watch?v=Nw9vgfbPf90

