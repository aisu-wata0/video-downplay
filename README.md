
# Video Downplay

Downloads and opens videos from links copied on your clipboard!

When you copy a video link supported by youtube_dl it automatically downloads it and opens with the chosen video player.

By default videos are downloaded to the script location/downloads/

The 'video player' is the command line for opening the player, for example `mpc-hc64` opens Media Player Classic (the default is `mpc-hc64`) [1].

This command downloads and plays videos in links copied in the clipboard with the chosen video player (mpc-hc64 is the default, you can ommit the `--video_player` argument):

`video_downplay.py --video_player mpc-hc64`

Use this to see more options:

`video_downplay.py --help`

This command downloads and plays the video in the link:

`video_downplay.py https://www.youtube.com/watch?v=eI1GCXAUxAA`

This command downloads just downloads the video in the link:

`video_downplay.py https://www.youtube.com/watch?v=eI1GCXAUxAA -nap -k`

Example of use in a console:

```bash
$ video_downplay.py 
Watching for video links on clipboard.
Will download them on the directory: C:/Users/bruno/scripts/video-downplay/downloads/
Keys:
        'q': Quit
        'p': Pause
        'u': Unpause
        'd': Toggle delete video after watching
        'o': Toggle open video after downloading
...q
stopping...
```

In this case I input 'q' and pressed enter to choose the action "'q': Quit", any other could be chosen.


* 'p': Pause
 
  Pauses watcher, copied links while paused are ignored

* 'u': Unpause

	Continues normal execution

* 'd': Toggle delete video after watching

	Continues normal execution

* 'o': Toggle open video after downloading

## Extra info

[1] The video player call is actually just implemented as a subprocess  [video_player, filepath]; so if you pass `--video_player echo` it would just print the filepath after downloading.
