import os, fnmatch, json, jsonschema, copy
import subprocess, time, shlex, threading
from functools import cached_property
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.events import EVENT_TYPE_CLOSED, EVENT_TYPE_OPENED


class CONSTANTS:
    __slots__ = ()
    SCRIPT_PATH = os.path.realpath(__file__)
    SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)
    WATCH_JSON_PATH = os.path.join(SCRIPT_DIR, "watch.json")
    WATCH_JSON_DIR = SCRIPT_DIR
    P_SPAWN_DELAY = 2  # s
    EVENT_IDLE_TIME = (
        2  # s Time after the last event, after which we can spawn a new process
    )


os.chdir(CONSTANTS.SCRIPT_DIR)

SCHEMA = {
    "type": "object",
    "properties": {
        "ignore": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Folders to ignore",
        },
        "watch": {"type": "string", "description": "Folder to watch for changes"},
        "recursive": {
            "type": "boolean",
            "description": "True if we should recursively watch the folder provided",
        },
        "command": {
            "type": "string",
            "description": "Command to execute on a file change",
        },
    },
    "required": [
        "ignore",
        "watch",
        "command",
    ],
}


class WatchConfig:
    __WATCHER_SETTINGS = {}

    def __init__(self) -> None:
        if not self.load_watch_settings():
            raise Exception("Watcher Settings Failed to load")

    @cached_property
    def ignore_patterns(self):
        return list(
            map(
                lambda pattern: self._resolve_path(pattern),
                self.__WATCHER_SETTINGS.get("ignore", [])[::],
            )
        )

    @cached_property
    def watched_folder(self):
        return self._resolve_path(
            self.__WATCHER_SETTINGS.get("watch", "./")
        )  # Watch the `watch.py` folder by default

    @cached_property
    def watch_pattern(self):
        folder_path = self.watched_folder
        if self.is_recursive:
            return os.path.join(folder_path, "**")
        else:
            return folder_path

    @cached_property
    def is_recursive(self):
        return self.__WATCHER_SETTINGS.get("recursive", True)

    @cached_property
    def command(self):
        return self.__WATCHER_SETTINGS.get("command", "")

    def is_path_ignored(self, path):
        # type: (str) -> bool
        match = fnmatch.fnmatch
        return any(match(path, pattern) for pattern in self.ignore_patterns)

    def is_path_watched(self, path):
        # type: (str, str) -> bool
        match = fnmatch.fnmatch
        if self.is_recursive:
            return match(path, self.watch_pattern)
        return match(path, self.watched_folder)

    def get_settings(self):
        # type: () -> dict
        return copy.deepcopy(self.__WATCHER_SETTINGS)

    def load_watch_settings(self):
        # type: () -> bool
        # Returns True if the settings were successfully loaded
        if os.path.exists(CONSTANTS.WATCH_JSON_PATH):
            settings = {}
            try:
                with open(CONSTANTS.WATCH_JSON_PATH, "r") as fp:
                    settings.update(json.loads(fp.read()))
            except:
                return False

            if settings:
                try:
                    jsonschema.validate(settings, SCHEMA)
                except jsonschema.ValidationError:
                    raise ValueError("watch.json doesn't match schema")

                self.__WATCHER_SETTINGS.update(settings)
                return True
        else:
            return False

    def _resolve_path(self, path):
        # type: (str) -> str | None
        # Convert path in watcher settings to absolute form by appending path of
        # `watch.json` to this `path`
        if not os.path.isabs(path):
            path = os.path.normpath(os.path.join(CONSTANTS.WATCH_JSON_DIR, path))
            return path

        return path

    def _print_settings(self):
        _special = ("ignore", "watch")

        print("Printing Watcher Settings...")
        for key in self.__WATCHER_SETTINGS:
            print(key, ":")

            if key not in _special:
                print("\t", self.__WATCHER_SETTINGS.get(key, ""))

            elif key == "ignore":
                for p in self.__WATCHER_SETTINGS.get(key, []):
                    print("\t", self._resolve_path(p))

            else:  # key == "watch"
                p = self.__WATCHER_SETTINGS.get(key, "")
                print("\t", self._resolve_path(p))


class CustomEventHandler(FileSystemEventHandler):
    _WATCH_SETTINGS = {}

    def __init__(self):
        super().__init__()

        self._config = WatchConfig()
        if not self._config.load_watch_settings():
            raise Exception("Could not load Watcher Settings")
        self._config._print_settings()
        self._curr_process: subprocess.Popen | None = None

        self._idle_lock = threading.Lock()
        self._e_idle_time = -1
        self._idle_watch_start = True  # Should we watch for idle?
        self._idle_watch_disable = False  # Use this to stop the _idle_watch_thread
        self._idle_watch_thread = threading.Thread(
            target=self._wait_for_idle, daemon=False
        )
        self._offending_event = None

    def start_idle_detection_thread(self):
        print("---- _wait_for_idle enabled")
        self._idle_watch_disable = False
        self._idle_watch_thread.start()

    def stop_idle_detection_thread(self):
        self._idle_watch_disable = True

    def _wait_for_idle(self):
        while not self._idle_watch_disable:
            self._idle_lock.acquire()
            if self._idle_watch_start:
                

                # Watching for Idle. Has the idle threshold been reached? Can we spawn a new process?
                if (
                    self._curr_process is None
                    or self._curr_process.poll() is not None # Current process has stopped (abruptly)
                    or time.time() - self._e_idle_time > CONSTANTS.EVENT_IDLE_TIME
                ):
                    self._idle_watch_start = False
                    event = self._offending_event
                    if event is not None:
                        print(
                            f"EVENT_TYPE: {event.event_type}, src: {event.src_path}",
                        )
                    print("🔃 PyWatch Restarting")
                    self._spawn_process()
                    self._e_idle_time = time.time()
                else:
                    # print("Idle timeout not exceeded")
                    pass
                

            self._idle_lock.release()

        print("---- _wait_for_idle disabled")

    def on_any_event(self, event: FileSystemEvent):
        if event.event_type not in (EVENT_TYPE_OPENED, EVENT_TYPE_CLOSED):

            if self._config.is_path_ignored(event.src_path):
                # print("State: Ignored")
                pass
            else:
                # print("State: Not Ignored")
                self._idle_lock.acquire()
                self._e_idle_time = time.time()
                self._idle_watch_start = True
                self._offending_event = event
                self._idle_lock.release()

    def _spawn_process(self):
        # Kill previous child process and spawn a new child

        if self._curr_process is not None:
            self._curr_process.terminate()

        args = shlex.split(self._config.command)
        self._curr_process = subprocess.Popen(args)


def main():
    handler = CustomEventHandler()
    observer = Observer()
    observer.schedule(
        handler, handler._config.watched_folder, recursive=handler._config.is_recursive
    )

    observer.start()

    print("🚧 PyWatch Started")
    handler.start_idle_detection_thread()
    try:
        while True:
            pass
    except:
        observer.stop()
        handler.stop_idle_detection_thread()
        print("🛑 PyWatch Stopped")

    observer.join()


if __name__ == "__main__":
    main()
