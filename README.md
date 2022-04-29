# scratchypy
Scratch-like library for Python using Pygame.

## Who's it for?
If you feel like you've mastered the graphical programming of Scratch, or started to hit some limitations, then ScratchyPy may be a good next step into the world of system programming.

[legal] This project is not affiliated with Scratch in any way.  Scratch(TM) is a trademark of the Scratch Team.  Scratch is developed by the Lifelong Kindergarten Group at the MIT Media Lab. See http://scratch.mit.edu.

### What you need to know
Some basic knowledge of Python is required.  There are many good introductory tutorials on the internet that can teach you the basics.

Knowledge of pygame is not required, but you may end up learning some as you go.  

## How to install
ScratchyPy requires Python 3.8 or higher.

You'll need `pip3 install pygame`

TODO: ScratchyPy is not a pip package yet; how to copy

## Features
ScratchyPy does not aim to reproduce Scratch exactly and faithfully.  Python, Pygame, and general UI programming patterns work differently and this library is more of a bridge into that world using familiar concepts.

See the complete Scratch mapping [here]()

### Bonus Features
There are several areas where ScratchyPy adds on some bonus functionality on top of Scratch capabilities.
- TextSprite
- AnimatedSprite
- Multiple stages and substages
- Direct messages with parameters
- stage.when_drawing to hook in pygame drawing

## Sharing
What makes Scrach fun is its social coding aspect.  You can easily try out others' work and it is safe to do so in the confines of a browser.

Python is a powerful system language.  It can create and delete files, do networking and downloads, and generally do anything your computer account can do.  This makes it dangerous to try out programs from people you don't know or trust, since they could very well delete all your files or install a virus.  In general, please do not share or accept programs.

TODO: Safe alternatives?

## Limitations
See the Python design page for expert information TBD

## Support
In short, there is none.

If you find an issue with the library itself, please open an issue on GitHub.

## TODO
- colors

## How to make images / transparency

Sprite with single costume:

```
sp = Sprite("larry.png")
```

Sprite with multiple costumes:

```
sp = Sprite(["explosion1.png", "explosion2.png"])
```

Loading sprites with setting transparent color:

```
costume = image.load("curly.bmp", color.WHITE)
sp = Sprite(costume)
```

Convenient way to load separate images in an animation: image01.png, image02.png, etc.  Make the black background transparent.

```
frames = image.loadPattern("animation/image*.png", Color.BLACK)
sp = Sprite(frames)
```

## Graduating from ScratchyPy
- other libs like pygame-menu and UI
