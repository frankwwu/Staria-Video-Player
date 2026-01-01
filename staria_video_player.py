import tkinter as tk
from tkinter import filedialog, ttk
import cv2
from PIL import Image, ImageTk
import threading
import time
import os
import tempfile
from moviepy.editor import VideoFileClip
import numpy as np
import sounddevice as sd
from scipy import signal
import wave

class VideoPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Video Player")
        self.root.geometry("900x750")
        self.root.configure(bg='#2b2b2b')
        
        # Video variables
        self.video = None
        self.is_playing = False
        self.current_frame = 0
        self.total_frames = 0
        self.fps = 30
        self.playback_speed = 1.0
        self.video_thread = None
        self.audio_thread = None
        self.stop_thread = False
        self.video_path = None
        self.photo = None
        self.temp_audio_file = None
        
        # Audio variables
        self.has_audio = False
        self.audio_data = None
        self.audio_sample_rate = 44100
        self.audio_stream = None
        self.audio_position = 0
        
        # Seeking flag
        self.seeking = False
        
        # Create GUI
        self.create_widgets()
        
        # Bind window resize event
        self.root.bind('<Configure>', self.on_window_resize)
        self.last_resize_time = 0
        
    def create_widgets(self):
        # Video display canvas
        self.canvas = tk.Canvas(self.root, bg='black', height=450)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control frame
        control_frame = tk.Frame(self.root, bg='#2b2b2b')
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Progress bar
        progress_frame = tk.Frame(control_frame, bg='#2b2b2b')
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Scale(
            progress_frame, 
            from_=0, 
            to=100, 
            orient=tk.HORIZONTAL,
            variable=self.progress_var,
            command=self.on_progress_change
        )
        self.progress_bar.pack(fill=tk.X, side=tk.LEFT, expand=True)
        self.progress_bar.bind("<ButtonPress-1>", self.on_progress_press)
        self.progress_bar.bind("<ButtonRelease-1>", self.on_progress_release)
        
        # Time labels
        time_frame = tk.Frame(control_frame, bg='#2b2b2b')
        time_frame.pack(fill=tk.X, pady=2)
        
        self.time_label = tk.Label(
            time_frame, 
            text="0:00 / 0:00", 
            fg='white', 
            bg='#2b2b2b',
            font=('Arial', 10)
        )
        self.time_label.pack()
        
        # Button frame
        button_frame = tk.Frame(control_frame, bg='#2b2b2b')
        button_frame.pack(pady=10)
        
        # Playback buttons
        btn_style = {'bg': '#404040', 'fg': 'white', 'padx': 10, 'pady': 5, 'relief': tk.RAISED}
        
        self.btn_prev_frame = tk.Button(button_frame, text="◄◄", command=self.prev_frame, **btn_style)
        self.btn_prev_frame.pack(side=tk.LEFT, padx=2)
        
        self.btn_skip_back = tk.Button(button_frame, text="⏮ -10s", command=lambda: self.skip(-10), **btn_style)
        self.btn_skip_back.pack(side=tk.LEFT, padx=2)
        
        self.btn_play_pause = tk.Button(button_frame, text="▶ Play", command=self.toggle_play, **btn_style)
        self.btn_play_pause.pack(side=tk.LEFT, padx=5)
        
        self.btn_skip_forward = tk.Button(button_frame, text="+10s ⏭", command=lambda: self.skip(10), **btn_style)
        self.btn_skip_forward.pack(side=tk.LEFT, padx=2)
        
        self.btn_next_frame = tk.Button(button_frame, text="►►", command=self.next_frame, **btn_style)
        self.btn_next_frame.pack(side=tk.LEFT, padx=2)
        
        # Capture frame button
        self.btn_capture = tk.Button(button_frame, text="📷 Capture", command=self.capture_frame, bg='#4CAF50', fg='white', padx=10, pady=5)
        self.btn_capture.pack(side=tk.LEFT, padx=10)
        
        # Speed control frame
        speed_frame = tk.Frame(control_frame, bg='#2b2b2b')
        speed_frame.pack(pady=10)
        
        tk.Label(speed_frame, text="Playback Speed:", fg='white', bg='#2b2b2b', font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        speeds = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
        for speed in speeds:
            btn = tk.Button(
                speed_frame, 
                text=f"{speed}x", 
                command=lambda s=speed: self.change_speed(s),
                bg='#404040', 
                fg='white', 
                padx=8, 
                pady=3
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        self.speed_label = tk.Label(speed_frame, text="1.0x", fg='#4CAF50', bg='#2b2b2b', font=('Arial', 10, 'bold'))
        self.speed_label.pack(side=tk.LEFT, padx=10)
        
        # Audio status label
        self.audio_status = tk.Label(control_frame, text="", fg='#888', bg='#2b2b2b', font=('Arial', 9))
        self.audio_status.pack(pady=2)
        
        # File selection button
        self.btn_open = tk.Button(
            control_frame, 
            text="📁 Open Video File", 
            command=self.open_video,
            bg='#2196F3', 
            fg='white', 
            padx=20, 
            pady=8,
            font=('Arial', 10, 'bold')
        )
        self.btn_open.pack(pady=10)
        
        # File name label
        self.file_label = tk.Label(control_frame, text="No video loaded", fg='#888', bg='#2b2b2b', font=('Arial', 9))
        self.file_label.pack()
        
    def open_video(self):
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.load_video(file_path)
            
    def extract_audio(self, video_path):
        """Extract audio from video file using moviepy"""
        try:
            self.audio_status.config(text="Extracting audio...", fg='yellow')
            self.root.update()
            
            # Create a temporary file for audio
            temp_dir = tempfile.gettempdir()
            self.temp_audio_file = os.path.join(temp_dir, "temp_audio.wav")
            
            # Remove old temp file if exists
            if os.path.exists(self.temp_audio_file):
                try:
                    os.remove(self.temp_audio_file)
                except:
                    pass
            
            # Extract audio using moviepy
            video_clip = VideoFileClip(video_path)
            
            if video_clip.audio is not None:
                video_clip.audio.write_audiofile(self.temp_audio_file, verbose=False, logger=None)
                video_clip.close()
                
                # Load audio data
                self.load_audio_data(self.temp_audio_file)
                self.has_audio = True
                self.audio_status.config(text="✓ Audio loaded (supports all speeds)", fg='#4CAF50')
                return True
            else:
                video_clip.close()
                self.audio_status.config(text="No audio track in video", fg='#888')
                return False
                
        except Exception as e:
            print(f"Audio extraction error: {e}")
            self.audio_status.config(text="Audio extraction failed", fg='#ff6b6b')
            return False
    
    def load_audio_data(self, audio_file):
        """Load audio data into memory"""
        try:
            with wave.open(audio_file, 'rb') as wf:
                self.audio_sample_rate = wf.getframerate()
                frames = wf.readframes(wf.getnframes())
                self.audio_data = np.frombuffer(frames, dtype=np.int16)
                
                # Convert to float for processing
                self.audio_data = self.audio_data.astype(np.float32) / 32768.0
                
                # Handle stereo
                if wf.getnchannels() == 2:
                    self.audio_data = self.audio_data.reshape(-1, 2)
        except Exception as e:
            print(f"Error loading audio data: {e}")
            self.has_audio = False
            
    def load_video(self, path):
        # Stop current playback
        if self.is_playing:
            self.toggle_play()
        
        # Stop audio
        self.stop_audio()
        
        # Load new video
        self.video = cv2.VideoCapture(path)
        self.total_frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.video.get(cv2.CAP_PROP_FPS)
        self.current_frame = 0
        self.video_path = path
        
        # Extract and load audio
        self.has_audio = self.extract_audio(path)
        
        # Update UI
        self.file_label.config(text=os.path.basename(path), fg='white')
        self.progress_bar.config(to=self.total_frames - 1)
        
        # Display first frame
        self.show_frame()
        self.update_time_label()
        
    def show_frame(self):
        if self.video is None:
            return
        
        try:
            self.video.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            ret, frame = self.video.read()
            
            if not ret:
                return
            
            # Convert BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Resize to fit canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                h, w = frame.shape[:2]
                scale = min(canvas_width/w, canvas_height/h)
                new_w, new_h = int(w*scale), int(h*scale)
                frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
            
            # Convert to PhotoImage and keep reference
            img = Image.fromarray(frame)
            self.photo = ImageTk.PhotoImage(image=img)
            
            # Display on canvas
            self.canvas.delete("all")
            self.canvas.create_image(
                canvas_width//2, 
                canvas_height//2, 
                image=self.photo, 
                anchor=tk.CENTER
            )
        except Exception as e:
            pass
            
    def toggle_play(self):
        if self.video is None:
            return
        
        self.is_playing = not self.is_playing
        
        if self.is_playing:
            self.btn_play_pause.config(text="⏸ Pause")
            
            # Start audio playback
            if self.has_audio:
                self.start_audio()
            
            self.stop_thread = False
            self.video_thread = threading.Thread(target=self.play_video)
            self.video_thread.daemon = True
            self.video_thread.start()
        else:
            self.btn_play_pause.config(text="▶ Play")
            self.stop_thread = True
            
            # Stop audio
            self.stop_audio()
    
    def start_audio(self):
        """Start audio playback with speed adjustment"""
        if not self.has_audio or self.audio_data is None:
            return
        
        try:
            # Calculate audio position based on current frame
            current_time = self.current_frame / self.fps
            self.audio_position = int(current_time * self.audio_sample_rate)
            
            # Start audio thread (processing happens in background)
            self.stop_audio()
            self.audio_thread = threading.Thread(target=self.play_audio_thread)
            self.audio_thread.daemon = True
            self.audio_thread.start()
        except Exception as e:
            print(f"Error starting audio: {e}")
    
    def play_audio_thread(self):
        """Play audio in separate thread with speed adjustment"""
        try:
            # At 1.0x speed, play continuously without chunking for smooth audio
            if self.playback_speed == 1.0:
                # Get current video position
                current_time = self.current_frame / self.fps
                start_sample = int(current_time * self.audio_sample_rate)
                
                # Check bounds
                if start_sample >= len(self.audio_data):
                    return
                
                # Play entire remaining audio
                audio_segment = self.audio_data[start_sample:]
                sd.play(audio_segment, self.audio_sample_rate, blocking=False)
                
                # Keep monitoring for stop signal
                while self.is_playing and not self.stop_thread:
                    if not sd.get_stream().active:
                        break
                    time.sleep(0.1)
                
            else:
                # For non-1.0x speeds, use chunked playback with sync
                chunk_duration = 1.0
                last_end_sample = 0
                
                while self.is_playing and not self.stop_thread:
                    # Get current video position
                    current_time = self.current_frame / self.fps
                    start_sample = int(current_time * self.audio_sample_rate)
                    
                    # Use continuity from previous chunk
                    if last_end_sample > 0 and abs(start_sample - last_end_sample) < self.audio_sample_rate * 0.2:
                        start_sample = last_end_sample
                    
                    # Calculate chunk size
                    chunk_size = int(chunk_duration * self.audio_sample_rate)
                    end_sample = start_sample + chunk_size
                    
                    # Check bounds
                    if start_sample >= len(self.audio_data):
                        break
                    
                    if end_sample > len(self.audio_data):
                        end_sample = len(self.audio_data)
                    
                    audio_chunk = self.audio_data[start_sample:end_sample]
                    
                    if len(audio_chunk) == 0:
                        break
                    
                    # Apply speed change
                    audio_chunk = self.resample_audio_segment(audio_chunk, self.playback_speed)
                    
                    # Play chunk
                    sd.play(audio_chunk, self.audio_sample_rate, blocking=False)
                    
                    last_end_sample = end_sample
                    
                    # Wait for most of chunk to play
                    chunk_play_time = len(audio_chunk) / self.audio_sample_rate
                    wait_time = chunk_play_time * 0.9
                    sleep_intervals = int(wait_time / 0.1)
                    for _ in range(max(1, sleep_intervals)):
                        if self.stop_thread or not self.is_playing:
                            sd.stop()
                            return
                        time.sleep(0.1)
            
        except Exception as e:
            print(f"Audio playback error: {e}")
        finally:
            try:
                sd.stop()
            except:
                pass
    
    def resample_audio_segment(self, audio_segment, speed):
        """Resample a segment of audio for speed change"""
        try:
            # Calculate new length
            new_length = int(len(audio_segment) / speed)
            
            # Handle stereo vs mono
            if len(audio_segment.shape) == 2:
                # Stereo
                resampled_left = signal.resample(audio_segment[:, 0], new_length)
                resampled_right = signal.resample(audio_segment[:, 1], new_length)
                return np.column_stack((resampled_left, resampled_right))
            else:
                # Mono
                return signal.resample(audio_segment, new_length)
        except Exception as e:
            print(f"Error resampling audio: {e}")
            return audio_segment
    
    def stop_audio(self):
        """Stop audio playback"""
        try:
            sd.stop()
            # Wait a bit for audio to fully stop
            time.sleep(0.05)
        except:
            pass
    
    def change_audio_speed(self, audio_data, speed):
        """Change audio speed using resampling - kept for compatibility"""
        if speed == 1.0:
            return audio_data
        
        try:
            # Calculate new length
            new_length = int(len(audio_data) / speed)
            
            # Handle stereo vs mono
            if len(audio_data.shape) == 2:
                # Stereo
                resampled_left = signal.resample(audio_data[:, 0], new_length)
                resampled_right = signal.resample(audio_data[:, 1], new_length)
                return np.column_stack((resampled_left, resampled_right))
            else:
                # Mono
                return signal.resample(audio_data, new_length)
        except Exception as e:
            print(f"Error changing audio speed: {e}")
            return audio_data
            
    def play_video(self):
        frame_time = 1.0 / self.fps
        
        while self.is_playing and self.current_frame < self.total_frames - 1:
            if self.stop_thread:
                break
            
            loop_start = time.time()
            
            # Update frame
            self.current_frame += 1
            
            # Schedule display update and wait for it to complete
            self.root.after_idle(self.update_display)
            
            # Calculate timing
            target_delay = frame_time / self.playback_speed
            elapsed = time.time() - loop_start
            sleep_time = max(0, target_delay - elapsed)
            
            # Use smaller sleep intervals to keep GUI responsive
            if sleep_time > 0:
                sleep_chunks = int(sleep_time / 0.01) + 1
                chunk_time = sleep_time / sleep_chunks
                for _ in range(sleep_chunks):
                    if self.stop_thread:
                        break
                    time.sleep(chunk_time)
        
        if self.current_frame >= self.total_frames - 1:
            self.is_playing = False
            self.root.after(0, lambda: self.btn_play_pause.config(text="▶ Play"))
            self.stop_audio()
    
    def update_display(self):
        """Update display in main thread to prevent flickering"""
        if not self.seeking:
            self.show_frame()
            self.progress_var.set(self.current_frame)
            self.update_time_label()
            
    def next_frame(self):
        if self.video is None:
            return
        
        was_playing = self.is_playing
        if was_playing:
            self.toggle_play()
        
        if self.current_frame < self.total_frames - 1:
            self.current_frame += 1
            self.show_frame()
            self.progress_var.set(self.current_frame)
            self.update_time_label()
            
    def prev_frame(self):
        if self.video is None:
            return
        
        was_playing = self.is_playing
        if was_playing:
            self.toggle_play()
        
        if self.current_frame > 0:
            self.current_frame -= 1
            self.show_frame()
            self.progress_var.set(self.current_frame)
            self.update_time_label()
            
    def skip(self, seconds):
        if self.video is None:
            return
        
        was_playing = self.is_playing
        if was_playing:
            self.toggle_play()
        
        frames_to_skip = int(seconds * self.fps)
        self.current_frame = max(0, min(self.current_frame + frames_to_skip, self.total_frames - 1))
        self.show_frame()
        self.progress_var.set(self.current_frame)
        self.update_time_label()
        
        if was_playing:
            self.toggle_play()
        
    def change_speed(self, speed):
        was_playing = self.is_playing
        
        # Stop first to avoid conflicts
        if was_playing:
            self.stop_thread = True
            self.stop_audio()
            
            # Wait for threads to finish
            if self.video_thread and self.video_thread.is_alive():
                self.video_thread.join(timeout=1.0)
            if self.audio_thread and self.audio_thread.is_alive():
                self.audio_thread.join(timeout=1.0)
            
            self.is_playing = False
            self.btn_play_pause.config(text="▶ Play")
        
        # Change speed
        self.playback_speed = speed
        self.speed_label.config(text=f"{speed}x")
        
        # Restart if was playing
        if was_playing:
            # Reset flags
            self.stop_thread = False
            # Small delay to ensure clean restart
            self.root.after(200, self.toggle_play)
    
    def on_progress_press(self, event):
        self.seeking = True
        if self.is_playing:
            self.stop_audio()
    
    def on_progress_release(self, event):
        self.seeking = False
        if self.video is None:
            return
        
        was_playing = self.is_playing
        if was_playing:
            self.stop_thread = True
            if self.video_thread:
                self.video_thread.join(timeout=0.5)
            self.is_playing = False
        
        self.current_frame = int(self.progress_var.get())
        self.show_frame()
        self.update_time_label()
        
        if was_playing:
            self.toggle_play()
        
    def on_progress_change(self, value):
        if self.video is None or not self.seeking:
            return
        
        self.current_frame = int(float(value))
        self.show_frame()
        self.update_time_label()
        
    def update_time_label(self):
        if self.video is None:
            return
        
        current_time = self.current_frame / self.fps
        total_time = self.total_frames / self.fps
        
        current_str = self.format_time(current_time)
        total_str = self.format_time(total_time)
        
        self.time_label.config(text=f"{current_str} / {total_str}")
        
    def format_time(self, seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}:{secs:02d}"
    
    def capture_frame(self):
        """Capture current frame and save as image"""
        if self.video is None:
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Frame As",
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png"),
                ("JPEG Image", "*.jpg"),
                ("BMP Image", "*.bmp"),
                ("All files", "*.*")
            ],
            initialfile=f"frame_{self.current_frame}.png"
        )
        
        if file_path:
            self.video.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            ret, frame = self.video.read()
            
            if ret:
                cv2.imwrite(file_path, frame)
                self.audio_status.config(text=f"✓ Frame saved: {os.path.basename(file_path)}", fg='#4CAF50')
                self.root.after(3000, lambda: self.audio_status.config(text="✓ Audio loaded (supports all speeds)" if self.has_audio else "", fg='#4CAF50' if self.has_audio else '#888'))
    
    def on_window_resize(self, event):
        """Handle window resize event"""
        if event.widget == self.root:
            current_time = time.time()
            if current_time - self.last_resize_time > 0.1:
                self.last_resize_time = current_time
                if self.video is not None:
                    self.root.after(50, self.show_frame)
    
    def __del__(self):
        # Clean up
        self.stop_audio()
        if self.temp_audio_file and os.path.exists(self.temp_audio_file):
            try:
                os.remove(self.temp_audio_file)
            except:
                pass

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoPlayer(root)
    root.mainloop()