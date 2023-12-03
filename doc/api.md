# The ScratchyPy API

API stands for "Application Programming Interface" and it is the documentation
of all the things that ScratchyPy can do.

The complete API generated directly from the code is published on the GitHub
pages site:
* [ScratchyPy API Documentation](https://jtmarkoise.github.io/scratchypy-api-master)

<a name="await"></a>

## What's all this `await` stuff? 
In Scratch, you can create multiple stacks of blocks and they will magically
run at the same time.

In most programming languages, instructions are run one after another in a 
sequence, called a *thread*.  It is possible and common to run two things in
parallel on multiple threads, but that can get complicated and is not
recommended for the beginner programmer.

Additionally, many UI frameworks work off an "event loop" model anyway.  This
has one central "forever" loop that handles events, such as mouse clicks or 
button presses, and pumps them out to custom code to do the special actions.
The most important thing the event loop does is redraw the screen many times
per second.  ScratchyPy uses an event loop model like this.

Some things in the ScratchyPy vocabulary are long-running animations or things
we have to wait for.
![ask and wait](img/ask-and-wait.png)

If we were to just stop the ScratchyPy code while these things 
happen, the event loop wouldn't run and the program would become unresponsive
 \- clicks wouldn't work and the screen would stop updating.

For these situations, you will see ScratchyPy code like this:

```python
    await sprite1.ask_and_wait("What is your name?")
```

Notice the special `await` before the function call.  In Python, this is a
special word that loosely means "pause this program while its waiting and go 
back to the event loop".  What it is really doing is fairly advanced, even for
experienced programmers, but don't worry.  Just know that any time you see a
function that ends with _wait(), you will be REQUIRED to put the `await` in
front of it.  If you forget, you will see a message in the console reminding 
you.

## The Woefully Incomplete List of Scratch Equivalents

### Motion

### Looks

### Sound

### Events

### Control
Things related to control are mostly part of the Python language itself.
These blocks are still covered here for completeness and to point out some
important caveats.

wait 1 seconds | `await wait(1)`
Note: do NOT use Python's `time.sleep(1)` as that will block the event loop!
See [the await section](#await) for more detail.

repeat 10 | `for i in range(10):  doSomething()`

forever | 
```
def runEachTick():
    doSomething()
sprite1.forever(runEachTick()
```
Note: Do NOT use `while True: doSomething()` as that will block the event loop!
See [the await section](#await) for more detail.

### Sensing

### Variables

### My Blocks