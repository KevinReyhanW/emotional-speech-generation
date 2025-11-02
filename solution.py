#!/usr/bin/env python3
"""Small TTS CLI using gTTS with simple style simulation."""
import sys
import argparse
import os
from gtts import gTTS
import tempfile
import soundfile as sf
import numpy as np


def modify_audio_file(in_path: str, out_path: str, speed_factor: float):
    """Resample audio to change playback speed."""
    data, sr = sf.read(in_path, dtype="float32")
    if data.ndim == 1:
        n_samples = data.shape[0]
        new_length = int(n_samples / speed_factor)
        old_indices = np.linspace(0, n_samples - 1, num=n_samples)
        new_indices = np.linspace(0, n_samples - 1, num=new_length)
        new_data = np.interp(new_indices, old_indices, data).astype(np.float32)
    else:
        n_samples = data.shape[0]
        new_length = int(n_samples / speed_factor)
        old_indices = np.linspace(0, n_samples - 1, num=n_samples)
        new_indices = np.linspace(0, n_samples - 1, num=new_length)
        channels = [np.interp(new_indices, old_indices, data[:, ch]) for ch in range(data.shape[1])]
        new_data = np.stack(channels, axis=1).astype(np.float32)
    sf.write(out_path, new_data, sr)


def synthesize(text: str, out_path: str, style: str = "neutral"):
    if not text or text.strip() == "":
        raise ValueError("Text is empty. Please provide non-empty text.")
    out_dir = os.path.dirname(os.path.abspath(out_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        temp_path = temp_file.name

    tts = gTTS(text=text, lang='en', slow=False)
    tts.save(temp_path)

    if style == "happy":
        modify_audio_file(temp_path, out_path, speed_factor=1.2)
    elif style == "sad":
        modify_audio_file(temp_path, out_path, speed_factor=0.8)
    else:
        data, sr = sf.read(temp_path, dtype="float32")
        sf.write(out_path, data, sr)

    try:
        os.unlink(temp_path)
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description="TTS CLI with simple styles")
    parser.add_argument('text', type=str)
    parser.add_argument('out', type=str)
    parser.add_argument('--style', type=str, default='neutral', choices=['neutral', 'happy', 'sad'])
    args = parser.parse_args()
    try:
        synthesize(args.text, args.out, args.style)
        print(f"Saved synthesized speech to: {args.out}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
