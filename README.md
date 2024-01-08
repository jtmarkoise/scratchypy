# Welcome to ScratchyPy!
ScratchyPy is a graphics-focused library for Python using [Pygame](https://www.pygame.org).
It uses the same vocabulary as the popular [Scratch](https://scratch.mit.edu) block-based programming lanugage.

Meet the mascot, Axel, the friendly axolotl.

<center>

![logo image](https://raw.githubusercontent.com/jtmarkoise/scratchypy/1d8230349054a9015fa2be823813872e7f90284f/examples/assets/axolotl1.png)

</center>

> [!NOTE]
> ScratchyPy is a work-in-progress and does not have a stable release yet. 
> The API is mostly in place, but there could be further changes that change 
> behavior.

## Who's it for?
If you feel like you've mastered the graphical programming of Scratch, or started to hit some limitations, then ScratchyPy may be a good next step into the world of system programming.

(LEGAL) *This project is not affiliated with Scratch in any way.  Scratch(TM) is a trademark of the Scratch Team.  Scratch is developed by the Lifelong Kindergarten Group at the MIT Media Lab. See [scratch.mit.edu](http://scratch.mit.edu).*

## How to install
ScratchyPy requires Python 3.8 or higher.

Install with `pip3 install scratchypy`

ScratchyPy is built on top of the `pygame` library, which will be installed as a dependency.

### What you need to know
Some basic knowledge of Python is required.  There are many good introductory tutorials on the internet that can teach you the basics.

Knowledge of pygame is not required, but you may end up learning some as you go.  

## Quick Start

<table border="1">
<tr><th> This Scratch code... </th><th>... is equivalent to this ScratchyPy</th></tr>
<tr><td>

![scratch block image](https://raw.githubusercontent.com/jtmarkoise/scratchypy/1d8230349054a9015fa2be823813872e7f90284f/doc/img/quickstart-scratch.png)

</td><td>

```python
from scratchypy import *
def startItUp(stage):
    sprite1 = Sprite("assets/axolotl1.png")
    stage.add(sprite1)
    sprite1.turn(45)
    sprite1.move(50)
start(startItUp)
```

</td></tr>
</table>

You can run this fully-annotated example and see many others in the /examples folder.


## Features
ScratchyPy does not aim to reproduce Scratch exactly and faithfully.  Python, Pygame, and general UI programming patterns work differently and this library is more of a bridge into that world using familiar concepts.

See the [almost-complete Scratch mapping](https://github.com/jtmarkoise/scratchypy/blob/1d8230349054a9015fa2be823813872e7f90284f/doc/api.md).

The generated code documentation is continuously published at [https://jtmarkoise.github.io/scratchypy/](https://jtmarkoise.github.io/scratchypy/)

### Bonus Features
There are several areas where ScratchyPy adds on some bonus functionality on top of Scratch capabilities.
- TextSprite
- AnimatedSprite
- Multiple stages and substages
- Direct messages with parameters
- stage.when_drawing to hook in pygame drawing

## Sharing
What makes Scrach fun is its social coding aspect.  You can easily try out others' work and it is safe to do so in the confines of a browser.

Python is a powerful system language.  It can create and delete files, do networking and downloads, and generally do anything your computer account can do.  This makes it dangerous to try out programs from people you don't know or trust, since they could very well delete all your files or install a virus.  
> [!CAUTION]
> Before running a shared program, make sure you trust the person who sent it to you.

TODO: Safe alternatives?

## Limitations
See the Python design page for expert information TBD

## Support
In short, there is nothing official.  I hope you will enjoy learning Python
and programming, and that a friendly community of support evolves.

If you find bug with the library itself, please open an issue on GitHub.
Enhancement requests are welcome too (even better with a patch provided!).

## TODO
- colors

## How to make images / transparency

Sprite with single costume:

```python
sp = Sprite("larry.png")
```

Sprite with multiple costumes:

```python
sp = Sprite(["explosion1.png", "explosion2.png"])
```

Loading sprites with setting transparent color:

```python
costume = image.load("curly.bmp", color.WHITE)
sp = Sprite(costume)
```

Convenient way to load separate images in an animation: image01.png, image02.png, etc.  Make the black background transparent.

```python
frames = image.loadPattern("animation/image*.png", Color.BLACK)
sp = Sprite(frames)
```

## Expanding further
- other libs like pygame-menu and UI
