# Ratatool
A set of tools to make ratatouille speedrunning fair
## How it detects if the game is loading
For artistic reasons the game uses an other resolution when showing cut scenes, this resolution is kept when loading
This means that the only thing we need to do to check if the game is loading is checking if there are x (almost) black pixels
in the top and bottom of the screen 

## Installation
### clone
Use git clone or download the repo to your computer
### download python3 and pip
#### windows
[insert windows tutorial]
#### linux
Use your package manager
##### ubuntu
sudo apt install python3, python3-pip
##### arch
sudo pacman -Sy\
sudo pacman -S python3, python3-pip
#### mac
download it from the python website or use the following command\
brew install python3, python3-pip
### install OpenCV
pip3 install opencv-python 
### start the script
python3 run.py speedrun.mkv

# Flags
## not optional
    -i <video> : location of the video
## optional
    -v : shows the speedrun visually.\
    -s : how much frames the progress bar should skip before updating again (default: 300).

# Features
Watch your run with data analizer

# Future features
* Render video without loading times
* Render video with data analizer
