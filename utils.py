import os


VIDEO_FILE_EXTENSIONS = [
    "avi",
    "mkv",
    "mp4"
]

SUBTITLE_FILE_EXTENSIONS = [
    "sub",
    "srt",
    "idx"
]


def file_has_one_of_extensions(filename, extensions):
    if "." in filename:
        parts = filename.split(".")
        return parts[-1] in extensions

    return False


def is_video_file(filename):
    return file_has_one_of_extensions(filename, VIDEO_FILE_EXTENSIONS)


def is_subtitle_file(filename):
    return file_has_one_of_extensions(filename, SUBTITLE_FILE_EXTENSIONS)

# finds any subtitle files for a movie, and returns them if they exist
def get_subtitle_file_for_movie(dir, filename):
    if "." not in filename:
        return []

    last_dot = filename.rfind(".")

    filename_without_extension = filename[0:last_dot]

    subtitle_files = []
    for extension in SUBTITLE_FILE_EXTENSIONS:
        subtitle_file = os.path.join(dir, filename_without_extension + "." + extension)
        if os.path.isfile(subtitle_file):
            subtitle_files.append(subtitle_file)

    return subtitle_files

