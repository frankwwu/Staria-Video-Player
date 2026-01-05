# Staria Video Player

A feature-rich desktop video player built with Python, supporting frame-by-frame navigation, variable playback speeds, and frame capture capabilities.

## Features

### Playback Controls
- **Play/Pause**: Standard video playback control
- **Frame-by-Frame Navigation**: Step forward (►►) or backward (◄◄) one frame at a time
- **Skip Controls**: Jump forward or backward by 10 seconds
- **Progress Bar**: Seek to any position by dragging the progress bar
- **Time Display**: Shows current time and total duration

### Speed Control
- **Variable Playback Speed**: 0.25x, 0.5x, 0.75x, 1.0x, 1.25x, 1.5x, 2.0x
- **Audio Speed Matching**: Audio automatically adjusts to match playback speed
- **Smooth Speed Transitions**: Change speed during playback without interruption

### Additional Features
- **Frame Capture**: Save any frame as an image (PNG, JPEG, or BMP)
- **Auto-Resize**: Video automatically scales to fit window size
- **Responsive GUI**: All controls remain responsive during playback
- **Multi-Format Support**: MP4, AVI, MOV, MKV, WMV, FLV, WebM

## Installation

### Prerequisites
Python 3.8 or newer is required.

### Step 1: Install Python
1. Download Python from [python.org/downloads](https://python.org/downloads/)
2. Run the installer
3. **Important**: Check "Add Python to PATH" during installation

### Step 2: Install Required Libraries
Open a terminal/command prompt and run:

```bash
pip install opencv-python pillow moviepy sounddevice scipy
```

Or install them one by one if you encounter issues:

```bash
pip install opencv-python
pip install pillow
pip install moviepy
pip install sounddevice
pip install scipy
```

### Step 3: Download the Application
Save the `staria_video_player.py` file to your computer.

## Usage

### Starting the Application
1. Open a terminal/command prompt
2. Navigate to the folder containing `staria_video_player.py`
3. Run:
   ```bash
   python staria_video_player.py
   ```

### Opening a Video
1. Click the **📁 Open Video File** button
2. Select your video file
3. The video will load and display the first frame

### Playback Controls

| Control | Action |
|---------|--------|
| **▶ Play / ⏸ Pause** | Start or pause video playback |
| **◄◄** | Go back one frame |
| **►►** | Go forward one frame |
| **⏮ -10s** | Skip backward 10 seconds |
| **+10s ⏭** | Skip forward 10 seconds |
| **Progress Bar** | Click or drag to seek to any position |

### Changing Playback Speed
Click any speed button (0.25x to 2.0x) to change playback speed. Audio will automatically adjust to match.

### Capturing Frames
1. Navigate to the frame you want to capture
2. Click the **📷 Capture** button
3. Choose location and format (PNG, JPEG, or BMP)
4. The frame will be saved at original video quality

### Window Resizing
- Simply maximize or resize the window
- Video will automatically scale to fit
- Aspect ratio is preserved (no stretching)

## Keyboard Shortcuts
Currently, the application uses mouse controls only. Keyboard shortcuts may be added in future versions.

## Troubleshooting

### No Audio
**Issue**: "No audio track or audio format not supported"
- **Solution**: The video may not have an audio track, or the format is unsupported. Video playback will continue normally without audio.

### moviepy Import Error
**Issue**: `ModuleNotFoundError: No module named 'moviepy.editor'`
- **Solution**: 
  ```bash
  pip uninstall moviepy
  pip install moviepy==1.0.3
  pip install imageio-ffmpeg
  ```

### Audio Extraction Fails
**Issue**: "Audio extraction failed"
- **Solution**: Try installing FFmpeg separately:
  - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
  - **Mac**: `brew install ffmpeg`
  - **Linux**: `sudo apt install ffmpeg`

### Video Flickering
- Ensure you have the latest version of opencv-python
- Try: `pip install --upgrade opencv-python`

### Slow Performance
- Close other applications to free up system resources
- Try playing lower resolution videos
- Reduce playback speed if using frame-by-frame navigation

### sounddevice Issues
**Issue**: Audio playback errors
- **Windows**: Install Visual C++ Redistributable
- **Mac/Linux**: Install PortAudio: `sudo apt install portaudio19-dev` (Linux) or `brew install portaudio` (Mac)

## Technical Details

### Libraries Used
- **OpenCV (cv2)**: Video reading and frame extraction
- **Pillow (PIL)**: Image processing and display
- **MoviePy**: Audio extraction from video files
- **sounddevice**: Audio playback with speed control
- **scipy**: Audio resampling for speed changes
- **tkinter**: GUI framework (included with Python)

### Audio Synchronization
- **1.0x Speed**: Continuous audio playback for smooth sound
- **Other Speeds**: Chunked playback with real-time resampling and sync adjustment

### Performance Notes
- Videos are read frame-by-frame for precise control
- Audio is loaded into memory for speed adjustment
- Large video files play smoothly, but audio extraction may take a few seconds

## Limitations

- Audio quality may vary slightly at extreme speeds (0.25x or 2.0x) due to resampling
- Very large video files (>2GB) may take longer to load audio
- Frame-by-frame navigation assumes 30 FPS (adjusts automatically per video)

## System Requirements

### Minimum
- **OS**: Windows 11+, macOS 10.12+, or Linux
- **RAM**: 4GB
- **Python**: 3.8 or newer

### Recommended
- **OS**: Windows 11+, macOS 11+, or recent Linux
- **RAM**: 8GB or more
- **Python**: 3.9 or newer
- **Display**: 1920x1080 or higher

## Future Enhancements

Potential features for future versions:
- Keyboard shortcuts
- Playlist support
- Subtitle support
- Video filters and effects
- Trimming and basic editing
- Export video segments
- Bookmarks/markers

## License

This is a free and open-source application. Feel free to modify and distribute.

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Ensure all libraries are correctly installed
3. Verify your Python version is 3.8 or newer

## Credits

Built using Python and open-source libraries:
- OpenCV for video processing
- MoviePy for multimedia handling
- sounddevice for audio playback
- scipy for signal processing
