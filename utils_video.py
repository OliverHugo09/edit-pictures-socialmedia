import os
import random
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, ColorClip # type: ignore


def resize_and_center_video(video_path, output_path, target_resolution):
    video = VideoFileClip(video_path)
    original_ratio = video.w / video.h
    target_ratio = target_resolution[0] / target_resolution[1]

    if original_ratio > target_ratio:
        # El video es más ancho, redimensionar por ancho
        new_width = target_resolution[0]
        new_height = int(new_width / original_ratio)
    else:
        # El video es más alto, redimensionar por alto
        new_height = target_resolution[1]
        new_width = int(new_height * original_ratio)

    resized = video.resize(newsize=(new_width, new_height))
    background = ColorClip(target_resolution, color=(0, 0, 0), duration=video.duration)
    centered = CompositeVideoClip([background.set_duration(video.duration),
                                   resized.set_position("center")])
    centered.write_videofile(output_path, codec="libx264", audio_codec="aac")
    video.close()


def combine_video_audio(video_path, audio_path, output_path, random_audio=False, audio_start=0):
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)

    if random_audio:
        if audio.duration > video.duration:
            max_start = audio.duration - video.duration
            audio_start = random.uniform(0, max_start)
        else:
            audio_start = 0

    audio = audio.subclip(audio_start, min(audio_start + video.duration, audio.duration))

    final = video.set_audio(audio)
    final.write_videofile(output_path, codec="libx264", audio_codec="aac")

    video.close()
    audio.close()


def process_video(input_path, output_folder, filename, formats, audio_path=None, random_audio=False, audio_start=0):
    base_name = os.path.splitext(filename)[0]

    resolutions = {
        'instagram': (1080, 1350),
        'tiktok': (1080, 1920),
        'x': (1080, 1350),
        'youtube': (1080, 1920)
    }

    for fmt in formats:
        if fmt not in resolutions:
            continue

        target_resolution = resolutions[fmt]
        temp_video = os.path.join(output_folder, f"{base_name}_{fmt}_temp.mp4")
        final_video = os.path.join(output_folder, f"{base_name}_{fmt}.mp4")

        resize_and_center_video(input_path, temp_video, target_resolution)

        if audio_path:
            combine_video_audio(temp_video, audio_path, final_video, random_audio, audio_start)
            os.remove(temp_video)
        else:
            os.rename(temp_video, final_video)