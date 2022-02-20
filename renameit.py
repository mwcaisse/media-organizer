#!/usr/bin/env python
from datetime import datetime
from guessit import guessit
import os
import requests
import pickle
import shutil

from utils import is_video_file, is_subtitle_file, get_subtitle_file_for_movie


def guess_name_from_file_name(filename):
    guess = guessit(filename)

    return {
        "type": guess.get("type", None),
        "year": guess.get("year", None),
        "name": guess.get("title", None)
    }


HAS_MULTI = 0


def prompt_for_multiple_choices(filename, movies):
    print("\n")
    print(f'Found multiple possible movies for "{filename}". Please chose which is correct:')
    for i, movie in enumerate(movies):
        name = movie["title"]
        try:
            year = datetime.strptime(movie["release_date"], "%Y-%m-%d").year
        except:
            year = None
        print(f"\t {i + 1}) {name} ({year})")

    while True:
        selected_index = input(f"Choice ({1} - {len(movies)}, 0 to skip, ENTER for 1): ")

        if selected_index == "":
            selected_index = 1
            break

        try:
            selected_index = int(selected_index)
        except:
            continue

        if 0 <= selected_index <= len(movies):
            break

        print("Invalid input.")
        selected_index = input(f"Choice({1} - {len(movies)}, 0 to skip):")

    if selected_index == 0:
        return None

    return movies[selected_index-1]


def get_movie_info_themoviedb(filename):
    guess = guess_name_from_file_name(filename)

    if not guess["name"]:
        return None

    query_params = {
        "api_key": "FILL_ME_IN",
        "query": guess["name"]
    }

    if guess.get("year"):
        query_params["year"] = guess["year"]

    resp = requests.get("https://api.themoviedb.org/3/search/movie", params=query_params)
    resp.raise_for_status()

    results = resp.json()["results"]

    if len(results) == 0:
        return None

    if len(results) > 1:
        global HAS_MULTI
        HAS_MULTI = HAS_MULTI + 1
        movie = prompt_for_multiple_choices(filename, results)
    else:
        movie = next(iter(results))

    if movie is None:
        return None

    release_date = datetime.strptime(movie["release_date"], "%Y-%m-%d")

    return {
        "name": movie["title"],
        "year": release_date.year,
        "tmdb_id": movie["id"]
    }


# this doesn't seem to be very good, use as fallback?
def get_movie_info_simkl(filename):
    resp = requests.post("https://api.simkl.com/search/file", json={
        "file": filename
    })
    resp.raise_for_status()

    res = resp.json()

    if type(res) is list and len(res) == 0:
        return None
    elif type(res) is list:
        print("List returned multiple values, using the first for now")
        res = next(res)

    print(res)
    print(type(res) is list)

    if res.get("type") and res["type"] == "movie":
        movie = res["movie"]

        return {
            "name": movie["title"],
            "year": movie["year"],
            "imdb_id": movie.get("ids", {}).get("imdb")
        }

    return None


MOVIE_CACHE_FILE = ".movie_requests_cache.pkl"

if os.path.isfile(MOVIE_CACHE_FILE):
    with open(MOVIE_CACHE_FILE, "rb") as cache_file:
        MOVIE_CACHE = pickle.load(cache_file)
else:
    MOVIE_CACHE = {}


def get_movie_info_cached(filename):
    if filename in MOVIE_CACHE:
        return MOVIE_CACHE[filename]

    movie = get_movie_info_themoviedb(filename)

    MOVIE_CACHE[filename] = movie
    return movie


def get_folder_for_movie(movie):
    name = movie["name"]
    year = movie.get("year")

    if year:
        return f"{name} ({year})"
    else:
        return f"{name}"


def main():
    print("Welcome to RenameIt (TM)")

    # We want to rename our Movie files and move them into folders, where the folder is the name of the movie
    # -- we could do Movie Name (Year)

    # lets just walk through all of the video files and do some categorization / stats on em

    movie_dir = "/media/arch-data/media/Videos/Movies"

    root, dirs, files = next(os.walk(movie_dir))

    results = {
        "unknown": [],
        "subtitles": [],
        "found": [],
        "non_movies": []
    }

    files.sort()

    for filename in files:

        if is_subtitle_file(filename):
            results["subtitles"].append(filename)
            continue

        if not is_video_file(filename):
            results["non_movies"].append(filename)
            continue

        movie_info = get_movie_info_cached(filename)

        if movie_info:
            movie_info["filename"] = filename
            results["found"].append(movie_info)
        else:
            results["unknown"].append(filename)

    # save the cached movie requests
    with open(MOVIE_CACHE_FILE, "wb") as cache_file:
        pickle.dump(MOVIE_CACHE, cache_file)

    print("====FOUND=====")
    for guess in results["found"]:
        filename = guess["filename"]
        print(get_folder_for_movie(guess) + "/" + filename)

    print("====UNKNOWN=====")
    for filename in results["unknown"]:
        print(filename)

    print("===IGNORED / NON MOVIES =======")
    for filename in results["non_movies"]:
        print(filename)

    # Lets move all of the FOUND ones
    print("MOVING ALL OF THE FOUND MOVIES")
    input("PRESS ENTER TO CONTINUE... OR FOREVER HOLD YOUR PEACE")

    moved = 0

    for movie in results["found"]:
        if moved > 2:
            break

        filename = movie["filename"]
        movie_folder_name = get_folder_for_movie(movie)

        src = os.path.join(root, filename)
        dest = os.path.join(root, movie_folder_name)

        print(f"MOVING {src} to {dest}")
        os.makedirs(dest, exist_ok=True)
        shutil.move(src, dest)

        subtitle_files = get_subtitle_file_for_movie(movie_dir, filename)

        for subtitle_file in subtitle_files:
            subtitle_file = os.path.join(root, subtitle_file)

            print(f"MOVING SUBTITLE FILE {subtitle_file} to {dest}")
            shutil.move(subtitle_file, dest)


        #moved = moved + 1
    print("EVERYTHING IS MOVED INTO ITS FOLDERS NOW. HOPEFULLY WE DIDN'T FUCK SHIT UP")


def back_to_root():
    movie_dir = "/media/arch-data/media/Videos/Movies/"

    moved = 0

    for root, directories, files in os.walk(movie_dir):
        if root == movie_dir:
            continue

        for filename in files:
            print(f"MOVING {os.path.join(root, filename)} to {movie_dir}")
            shutil.move(os.path.join(root, filename), movie_dir)
            moved = moved + 1


if __name__ == "__main__":
    main()
