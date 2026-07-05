import ffmpeg


def video_to_audio(input_path: str, output_path: str):
    """Video se audio (MP3) nikaalta hai."""
    (
        ffmpeg
        .input(input_path)
        .output(output_path, format="mp3", acodec="libmp3lame", audio_bitrate="128k")
        .overwrite_output()
        .run(quiet=True)
    )
    return output_path


def compress_video(input_path: str, output_path: str, crf: int = 32):
    """
    Video ka size chhota karta hai.
    crf jitna zyada, utna zyada compression (quality kam) - range 18(best)-35(smallest).
    """
    (
        ffmpeg
        .input(input_path)
        .output(output_path, vcodec="libx264", crf=crf, preset="veryfast",
                acodec="aac", audio_bitrate="96k")
        .overwrite_output()
        .run(quiet=True)
    )
    return output_path


def convert_audio_format(input_path: str, output_path: str, target_format: str):
    """MP3/WAV/OGG jaise audio formats ke beech convert karta hai."""
    (
        ffmpeg
        .input(input_path)
        .output(output_path, format=target_format)
        .overwrite_output()
        .run(quiet=True)
    )
    return output_path
