from cx_Freeze import setup, Executable

base = None

executables = [Executable("localApp.py", base=base)]

packages = ["idna", "tweepy", "time", "timeit", "datetime"]
options = {
    'build_exe': {
        'packages': packages,
    },
}

setup(
    name = "foo",
    options = options,
    version = "0.2",
    description = 'bar',
    executables = executables
)