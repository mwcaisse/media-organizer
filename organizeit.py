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


def progress_percentage(perc, width=None):

    FULL_BLOCK = "█"
    INCOMPLETE_BLOCK_GRAD = ["░", "▒", "▓"]

    assert(isinstance(perc, float))
    assert(0. <= perc <= 100.)

    if width is None:
        try:
            width = os.get_terminal_size().columns
        except OSError as e:
            width=120 # default it to 120 if this happens

    max_perc_widget = "[100.00%]"
    separator = " "
    blocks_widget_width = width - len(separator) - len(max_perc_widget)
    assert(blocks_widget_width >= 10)
    perc_per_block = 100.0/blocks_widget_width

    # sensitivity of rendering a gradient block
    epsilon = 1e-6

    full_blocks = int((perc + epsilon) / perc_per_block)
    empty_blocks = blocks_widget_width - full_blocks

    blocks_widget = ([FULL_BLOCK] * full_blocks)
    blocks_widget.extend([INCOMPLETE_BLOCK_GRAD[0]] * empty_blocks)

    remainder = perc - full_blocks * perc_per_block

    if remainder > epsilon:
        grad_index = int((len(INCOMPLETE_BLOCK_GRAD) * remainder) / perc_per_block)
        blocks_widget[full_blocks] = INCOMPLETE_BLOCK_GRAD[grad_index]

    str_perc = "%.2f" % perc
    perc_widget = "[%s%%]" % str_perc.ljust(len(max_perc_widget) - 3)

    # create the progress bar
    progress_bar = "%s%s%s" % ("".join(blocks_widget), separator, perc_widget)
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
        dest_file = os.path.join(dest_dir, filename)

        # If the file already exists, skip copying it
        if os.path.exists(dest_file):
            SKIPPED.append(src_file)
            print("{file} ALREADY EXISTS! SKIPPING!".format(file=dest_file))
            return

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        print("Copying TV Show: {filename}!".format(filename=filename))
        copy_file_with_progress(src_file, dest_file)
        os.remove(src_file)

    elif guess["type"] == "movie":
        if not os.path.exists(MOVIES_DIR):
            os.makedirs(MOVIES_DIR)

        dest_file = os.path.join(MOVIES_DIR, filename)
        # If the file already exists, skip copying it
        if os.path.exists(dest_file):
            SKIPPED.append(src_file)
            print("{file} ALREADY EXISTS! SKIPPING!".format(file=dest_file))
            return

        # copy to the movies dir
        #TODO: Might want to add a check to see if the file contains S01E01 format first, incase mistaken movie
        print("Copying Movie: {filename}!".format(filename=filename))
        copy_file_with_progress(src_file, dest_file)
        os.remove(src_file)
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
