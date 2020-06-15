from cx_Freeze import setup, Executable

base = None

executables = [Executable("localApp.py", base=base)]

packages = ["idna", "tweepy", "time", "atexit", "io", "timeit", "datetime"]
options = {
    'build_exe': {
        'packages': packages,
    },
}

setup(
    name = "foo",
    options = options,
    version = "0.1",
    description = 'bar',
    executables = executables
)