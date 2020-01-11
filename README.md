# Organize It

Python script to automate organization and copying of TV Shows and  movies to
their permanent storage position.

## How to use
### Configuration
There are a few configuration variables at the top of the script
* `ORGANIZE_DIR` The Directory that contains all of the media you wish to organize. It will walk through the directory 
and find all media files.
* `EXCLUDE_DIRS` A list of directories that you wish to exclude from being parsed
* `TV_DIR` The directory to move the TV Shows in to
* `MOVIES_DIR` The directory to move the movies in to
* `VIDEO_FILE_EXTENSIONS` The extensions of files to consider videos

### Running

```console
./organizeit
```

It will look at all video files in `ORGANIZE_DIR` that match `VIDEO_FILE_EXTENSIONS` and are not in `EXCLUDE_DIRS`. 
Using the file name determine whether it is a TV Show or Movie and move it appropriately. It expects
the name of the movie / show to be in the file name and if it is a TV Show the season and episode number.

* If it is a TV Show it will move the file to `TV_DIR/<Show Name>/Season ##/`. It will title case the show name when 
creating the directory.
* If it is a movie it will move the file to `MOVIES_DIR`

