#For finger_snapper.py
#on cmd type: python setup.py build

from cx_Freeze import setup, Executable
includefiles = ['banner.png', 'instructions.png', 'icon.ico', 'Audio'] #Add Images and Music here
includes = []
packages = ["pygame", "pickle", "math", "random", "sys", "os", "game_methods"]

target = Executable(script='main.py',
                    base='WIN32GUI',
                    compress=False,
                    copyDependentFiles=True,
                    appendScriptToExe=True,
                    appendScriptToLibrary=False,
                    icon='icon.ico')

setup(
    name = 'Finger Snapper',
    version = '1.0.0',
    description = 'A game that will make you lose your senses.',
    author = 'Seraph Wedd',
    author_email = 'seraphwedd18@gmail.com',
    options = {'build_exe': {'packages':packages, 'include_files':includefiles}},
    executables = [target]
    )
