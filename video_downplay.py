#! python

import subprocess
import os
import traceback
import sys
import threading
import errno

import time

import youtube_dl
import clipb

# def hook(status):
#     if status['status'] == 'finished':
#         if not hook.player_run:
#             hook.player_run = True
#             hook.subprocess = subprocess.Popen([args.video_player, status['filename']])
#             hook.subprocess.wait()
#     return

# hook.player_run = False
# hook.subprocess = None

def hook(status):
    if not hook.player_run:
        hook.player_run = True
        hook.subprocess = subprocess.Popen(
            [args.video_player, status['filename']])
        hook.subprocess.wait()

    return


hook.player_run = False
hook.subprocess = None


def supported_youtube_dl(url):
    """
    checks if 'url' parameter is a supported url
    returns True if supported
    """
    ies = youtube_dl.extractor.gen_extractors()
    for ie in ies:
        if ie.suitable(url) and ie.IE_NAME != 'generic':
            # Site has dedicated extractor
            if args.only_youtube and ie.IE_NAME != 'youtube':
                if args.v:
                    print('clipboard content is not from youtube', flush=True)
                return False

            print('\n>Detected ' + ie.IE_NAME + ' url:\n' + url, flush=True)
            return True

    if args.v:
        print('clipboard content is not a link', flush=True)
    return False


def play_url(url):
    videoFilename = ''

    opts = {
        # 'format': 'best', # sadly doesn't give the highest quality
        # removes "WARNING: Requested formats are incompatible for merge and will be merged into mkv." # https://askubuntu.com/questions/806258/requested-formats-are-incompatible-for-merge
        # https://stackoverflow.com/questions/31631535/youtube-dl-dash-video-and-audio-in-highest-quality-without-human-intervention
        # 'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'format': 'bestvideo[height>=1080]+bestaudio/bestvideo+bestaudio/best',
        # 'nopart': True,
        # 'progress_hooks': [hook],
        'outtmpl': args.download_dir + "/%(title)s.%(ext)s",
        'verbose': args.v,
        'noplaylist': True,
    }

    with youtube_dl.YoutubeDL(opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            videoFilename = ydl.prepare_filename(info)
            if args.v:
                print("download dir: ", args.download_dir, flush=True)
            ydl.download([url])
        except Exception as e:
            print(traceback.format_exception(*sys.exc_info()))
            print(e)
            print('----------------- failed to youtube-dl ', url, flush=True)
            pass

    # try to salvage wrong extension name
    if not os.path.isfile(videoFilename):
        videoFilename = os.path.splitext(videoFilename)[0] + '.mkv'

    if not os.path.isfile(videoFilename):
        print('video file not found ', url, ' filename: ', flush=True)
        try:
            print(videoFilename, flush=True)
        except:
            print("couldn't print filename", flush=True)
            pass
        return

    try:
        video_should_open = not args.no_autoplay
        video_should_delete = args.keep_download
        # Open video
        if video_should_open:
            command = [args.video_player, videoFilename]

            print("executing:", flush=True)
            try:
                print(command, flush=True)
            except:
                print("couldn't print command (videoFilename)", flush=True)
                pass

            try:
                import subprocess
                subprocess = subprocess.Popen(command)
                subprocess.wait()
            except Exception as e:
                print(traceback.format_exception(*sys.exc_info()))
                print(e)
                print('Failed to launch video player', flush=True)
                pass

        # Delete video
        if video_should_delete:
            try:
                print(f'deleting video: {videoFilename}')
                os.remove(videoFilename)
            except Exception as e:
                print(traceback.format_exception(*sys.exc_info()))
                print(e)
                print('did not delete ', videoFilename, flush=True)
                pass
    except SystemExit as e:
        print(f'SystemExit caught :)')
    except Exception as e:
        print(f'Exception caught {e}')


class VideoDownPlay(threading.Thread):
    def __init__(self, url, autoplay=True):
        super(VideoDownPlay, self).__init__()
        self._url = url
        self._autoplay = autoplay

    def run(self):
        play_url(self._url)


def videoDownPlayMakeThread(url):
    print('Creating thread with url: ', url, flush=True)
    thread = VideoDownPlay(url)
    thread.start()
    return thread


def ensure_dir(pathDir):
    """
    ----------
    pathDir : path to directory you want to exist
    -------
    """
    if not pathDir:
        raise ValueError("Invalid file path")
    try:
        os.makedirs(pathDir, exist_ok=True)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    return


if __name__ == "__main__":
    import argparse
    # Instantiate the parser
    parser = argparse.ArgumentParser(
        description='script description\n'
        'python ' + __file__ + ' arg1 example usage',
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='verbose')
    parser.add_argument('link', nargs='?',
                        help='video link')
    parser.add_argument('--download_dir', nargs='?', default=os.path.dirname(__file__) + '/downloads/',
                        help='video link')
    parser.add_argument('--video_player', nargs='?', default='mpc-hc64',
                        help='video link')
    parser.add_argument('-yt', '--only_youtube', action='store_true',
                        help='youtube only')
    parser.add_argument('-k', '--keep_download', action='store_true',
                        help='keep files after closing')
    parser.add_argument('-nap', '--no_autoplay', action='store_true',
                        help='no autoplay after downloading')

    # Parse arguments
    args = parser.parse_args()

    # ensure existence of output directory
    if args.verbose:
        print(
            f"ensure existence of output directory {args.download_dir}", flush=True)
    ensure_dir(args.download_dir)
    print(f"Watching for video links on clipboard.", flush=True)
    print(
        f"Will download them on the directory: {args.download_dir}", flush=True)
    print(f"Keys:", flush=True)
    print(f"\t'q': Quit", flush=True)
    print(f"\t'p': Pause", flush=True)
    print(f"\t'u': Unpause", flush=True)
    print(f"\t'k': Toggle keep video after watching", flush=True)
    print(f"\t'o': Toggle open video after downloading", flush=True)

    if args.link:
        play_url(args.link)
    else:
        # wait for links in clipboard

        watcher = clipb.ClipboardWatcher(
            supported_youtube_dl, videoDownPlayMakeThread, 0.25)

        watcher.start()

        while True:
            try:
                inp = input("...")
                inp = inp.lower()
                # # Keybindings
                # Pause
                if inp == "p":
                    watcher.pause()
                # Unpause
                if inp == "u":
                    watcher.unpause()
                # Quit / Break out
                if inp == "q":
                    break
                # Toggle keep video after watching
                if inp == "k":
                    args.keep_download = not args.keep_download
                    print(f"Keep video file after watching {args.keep_download}.")
                # Toggle open video after downloading
                if inp == "o":
                    args.no_autoplay = not args.no_autoplay
                    print(f"Open video after downloading {args.no_autoplay}.")

                # #
            except KeyboardInterrupt:
                print("Clipboard watcher interrupted.")
                break
            except Exception as e:
                print(f"Caught exception while waitning for user input")
                print(e)
                pass

        watcher.stop()
        watcher.join()
