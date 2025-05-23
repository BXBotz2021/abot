import os
import yt_dlp

def download_video(url, quality='best'):
    """Download a YouTube video and return the file path"""
    video_info = {}
    
    ydl_opts = {
        'format': f'{quality}',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
        'progress_hooks': [lambda d: download_hook(d, video_info)],
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return video_info.get('filepath')
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

def download_hook(d, video_info):
    """Hook to get information about the download"""
    if d['status'] == 'finished':
        video_info['filepath'] = d['filename']
