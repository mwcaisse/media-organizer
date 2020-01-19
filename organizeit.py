#!/usr/bin/env python


from guessit import guessit

import os
import shutil

ORGANIZE_DIR = "/media/data/Downloads/"

EXCLUDE_DIRS = {
    "/media/data/Downloads/New folder"
}

TV_DIR = "/media/arch-data/media/Videos/TV Shows/"
MOVIES_DIR = "/media/arch-data/media/Videos/Movies/"
VIDEO_FILE_EXTENSIONS = {
    "mp4",
    "mkv",
    "avi",
}


#Progress bar constants
PB_FULL_BLOCK = "█"
PB_INCOMPLETE_BLOCK_GRAD = ["░", "▒", "▓"]
PB_SEPARATOR = " "
PB_EPSILON = 1e-6
PB_MAX_PERC_WIDGET = "[100.00%]"


def progress_percentage(perc, width=None):
    assert(isinstance(perc, float))
    assert(0. <= perc <= 100.)

    if width is None:
        try:
            width = os.get_terminal_size().columns
        except OSError as e:
            width = 120  # default it to 120 if this happens

    blocks_widget_width = width - len(PB_SEPARATOR) - len(PB_MAX_PERC_WIDGET)
    assert(blocks_widget_width >= 10)
    perc_per_block = 100.0/blocks_widget_width

    full_blocks = int((perc + PB_EPSILON) / perc_per_block)
    empty_blocks = blocks_widget_width - full_blocks

    blocks_widget = ([PB_FULL_BLOCK] * full_blocks)
    blocks_widget.extend([PB_INCOMPLETE_BLOCK_GRAD[0]] * empty_blocks)

    remainder = perc - full_blocks * perc_per_block

    if remainder > PB_EPSILON:
        grad_index = int((len(PB_INCOMPLETE_BLOCK_GRAD) * remainder) / perc_per_block)
        blocks_widget[full_blocks] = PB_INCOMPLETE_BLOCK_GRAD[grad_index]

    str_perc = "%.2f" % perc
    perc_widget = "[%s%%]" % str_perc.ljust(len(PB_MAX_PERC_WIDGET) - 3)

    # create the progress bar
    progress_bar = "%s%s%s" % ("".join(blocks_widget), PB_SEPARATOR, perc_widget)
    return "".join(progress_bar)


def copy_process(copied, total):
    print("\r" + progress_percentage(100 * copied/total), end="")


def copy_file_obj(src, dst, callback, buffer_size=16*1024):
    with open(src, "rb") as srcf:
        with open(dst, "wb") as dstf:
            copied = 0
            while True:
                buf = srcf.read(buffer_size)
                if not buf:
                    break
                dstf.write(buf)
                copied += len(buf)
                callback(copied)


def copy_file_with_progress(src, dst, buffer_size=16*1024):
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))

    total = os.stat(src).st_size
    copy_file_obj(src, dst, lambda copied : copy_process(copied, total), buffer_size)
    shutil.copymode(src, dst)
    print("")


def is_video_file(filename):
    if "." in filename:
        parts = filename.split(".")
        return parts[-1] in VIDEO_FILE_EXTENSIONS

    return False


SKIPPED = []


def copy_video_file(src_file, dest_dir, dest_filename, type="TV Show"):
    dest_file = os.path.join(dest_dir, dest_filename)

    # If the file already exists, skip copying it
    if os.path.exists(dest_file):
        SKIPPED.append(src_file)
        print("{file} ALREADY EXISTS! SKIPPING!".format(file=dest_file))
        return

    # If the destination directory doesn't already exist, create it
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    print("Copying {type}: {filename}!".format(type=type, filename=dest_filename))
    copy_file_with_progress(src_file, dest_file)
    os.remove(src_file)


def organize_video(directory, filename):
    guess = guessit(filename)

    src_file = os.path.join(directory, filename)

    # Skip a sample file
    if "sample" in src_file.lower():
        SKIPPED.append(src_file)
        print("Skipping Sample: " + src_file)
        return

    if guess["type"] == "episode":
        # create the destination path TV_DIR/Show Name/Season ##/filename
        season_dir = "Season {num}".format(num=str(guess["season"]).zfill(2))
        dest_dir = os.path.join(TV_DIR, str(guess["title"]).title(), season_dir)

        copy_video_file(src_file, dest_dir, filename)

    elif guess["type"] == "movie":
        copy_video_file(src_file, MOVIES_DIR, filename, "Movie")
    else:
        print("Unknown video file! {directory}/{filename}",
              directory=directory,
              filename=filename)


def main():

    for root, directories, files in os.walk(ORGANIZE_DIR):
        if any([root.startswith(excluded_dir) for excluded_dir in EXCLUDE_DIRS]):
            continue

        for filename in files:
            if is_video_file(filename):
                organize_video(root, filename)

    if SKIPPED:
        print("Skipped the following files: ")
        for skipped in SKIPPED:
            print("\t {skipped}".format(skipped=skipped))


if __name__ == "__main__":
    main()
