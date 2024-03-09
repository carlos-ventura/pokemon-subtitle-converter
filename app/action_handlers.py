from __future__ import annotations

import glob
import mimetypes
import os
import subprocess
from typing import TYPE_CHECKING

from constants import *

if TYPE_CHECKING:
    from translator import Translator


def convert_str_to_dict(entries: str):
    all_dicts = {}
    for entry in entries.split('|'):
        key, value = entry.split(':')
        all_dicts[key.strip()] = value.strip()
    return all_dicts


def translate_subs(translator: Translator, videos_folder: str):
    subs_filenames = _get_filenames(videos_folder, video=False)
    for file in subs_filenames:
        print(f"[+] {file}")
        translator.run(path=file)


def generate_subs(videos_folder: str, track_number: int):
    video_filenames = _get_filenames(videos_folder)
    for file in video_filenames:
        file_list = file.split(".")
        file_list[-1] = "ass"
        sub_file = ".".join(file_list)
        _generate_subs(file, sub_file, track_number)


def _get_filenames(videos_folder: str, video: bool = True):
    filenames = glob.glob(os.path.join(videos_folder, "*.*"))
    video_filenames = []
    sub_filenames = []
    for file in filenames:
        mime = mimetypes.guess_type(file)
        if mime[0] is None:
            continue
        if "video" in mime[0]:
            video_filenames.append(file)
        else:
            sub_filenames.append(file)
    return video_filenames if video else sub_filenames


def _generate_subs(file: str, sub_file: str, track_number: int):
    command_string = f'mkvextract "{file}" tracks {track_number}:"{sub_file}"'
    subprocess.Popen(command_string, stdout=subprocess.PIPE, shell=True)
