# Ratatool
A set of tools to make ratatouille speedrunning fair
## How it detects if the game is loading
For artistic reasons the game uses an other resolution when showing cut scenes, this resolution is kept when loading
This means that the only thing we need to do to check if the game is loading is checking if there are x (almost) black pixels
in the top and bottom of the screen 

## Installation
The installation is probably not correct, please contribute to the installation if you find anything (Gracias :))
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
pip3 install opencv-python, numpy, progress, pillow
### examples
These are just examples, read the flags to get a better understanding of the application
#### show the speedrun with analizer
python3 run.py -vi speedrun.mkv\
press q to stop\
when it is stopped, press any key to exit
#### start the run at a specific start and endpoint
python3 run.py -vi speedrun.mkv -b 400 -e 30000
#### export the run without visual interface
python3 run.py -i speedrun.mkv -o output.avi
#### use splits
The splits are hard coded into the software now, I'll change it later
The use vim bindings to navigate in the video\
h: move back\
l: move forward\
j: increase the speed\
k: decrease the speed\
space: set split\
python3 run.py -Svi speedrun.mkv
#### Change detection points and sensitivity
The detection points are coded into the program for now, but I'll change it in the future\
look for the line that contains PIXELS_TO_CHECK
python3 run.py -dvi speedrun.mkv -t 50

# Flags
## not optional
    -i <input> : location of the video
## optional
    -v : shows the speedrun visually.\
    -S : use splits\
    -d : shows the loading detectors
    -s : how much frames the progress bar should skip before updating again (default: 300).
    -b <beginframe> : the frame where it should start
    -e <endframe> : the frame where it should end
    -o <output> : the location of the output video
    -t <threshold> : how black should black be
