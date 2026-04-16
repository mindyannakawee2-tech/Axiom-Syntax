![image_alt](https://github.com/mindyannakawee2-tech/Axiom-Syntax/blob/57f9a2afe8b7481507e3b1eaac8255b5dd71c830/AxiomBanner.png)
# Axiom
# Table of Contents

* [Axiom](#axiom)

  * [Overview](#overview)
  * [Comments](#comments)
  * [Variables](#variables)
  * [Functions](#functions)
  * [Return Values](#return-values)
  * [Classes](#classes)
  * [Conditionals](#conditionals)
  * [Imports](#imports)
  * [Decorators](#decorators)
  * [Built-in Console Functions](#built-in-console-functions)
  * [Special Keywords](#special-keywords)
  * [Indentation Rules](#indentation-rules)
  * [Axiom Examples](#axiom-examples)
* [AxiomPlay](#axiomplay)

  * [Overview](#overview-1)
  * [Quick Start](#quick-start)
  * [Modules](#modules)

    * [core](#core)
    * [draw](#draw)
    * [input](#input)
    * [audio](#audio)
    * [assets](#assets)
    * [camera](#camera)
    * [physics](#physics)
    * [scene](#scene)
    * [entity](#entity)
    * [save](#save)
  * [AxiomPlay Example](#axiomplay-example)
* [Known Limitations](#known-limitations)

---

# Axiom

## Overview

**Axiom** is a custom scripting language designed for readable game scripting and lightweight general programming.

Its design focuses on:

* explicit block endings
* simple object-oriented syntax
* clean function declarations
* game-friendly readability
* easy transpilation to Python-based runtimes

Axiom currently uses a compiler/transpiler approach.
In the current toolchain, Axiom source code is compiled into Python code.

---

## Comments

Use `#` for comments.

```axiom
# this is a comment
```

---

## Variables

Axiom supports local, global, and constant-style variables.

### `l. name = value`

Create a **local variable**.

```axiom
l. hp = 100
l. playerName = "Hero"
```

### `g. name = value`

Create or assign a **global variable**.

```axiom
g. score = 0
g. worldName = "Axiom"
```

### `c. name = value`

Create a **constant-style value**.

```axiom
c. VERSION = "0.1"
```

### Notes

* local variables are typically scoped to the current function or block context in the transpiled output
* globals are intended for shared game state
* constants are naming conventions in the current implementation and may not yet be fully immutable

---

## Functions

Functions are declared with `f.` and closed with `fend.`

### Syntax

```axiom
f. functionName = (arg1, arg2)
    # body
fend.
```

### Example

```axiom
f. greet = (name)
    log("Hello " + name)
fend.
```

### Parameters

Function parameters are written inside parentheses.

```axiom
f. add = (a, b)
    r. a + b
fend.
```

---

## Return Values

Use `r.` to return a value from a function.

### Syntax

```axiom
r. value
```

### Example

```axiom
f. double = (x)
    r. x * 2
fend.
```

---

## Classes

Classes are declared with `cls.` and closed with `clsend.`

### Syntax

```axiom
cls. ClassName;
    f. init = (self, ...)
        # constructor body
    fend.
clsend.
```

### Constructor

Use `init` as the constructor.
In the current compiler, `init` maps to Python `__init__`.

```axiom
cls. Player;
    f. init = (self, name, hp)
        self.name = name
        self.hp = hp
    fend.
clsend.
```

### Methods

Methods are normal functions inside a class block.

```axiom
cls. Player;
    f. attack = (self)
        log(self.name + " attacks")
    fend.
clsend.
```

### Example

```axiom
cls. Character;
    f. init = (self, name, health)
        self.name = name
        self.health = health
    fend.

    f. takeDMG = (self, damage)
        self.health -= damage
    fend.
clsend.

g. player = Character("Hero", 20)
player.takeDMG(10)
```

---

## Conditionals

Axiom uses `i.`, `ef.`, `e.`, and `end` for conditional logic.

### `i. condition do`

Start an `if` block.

### `ef. condition do`

Start an `else if` block.

### `e. do`

Start an `else` block.

### `end`

Close the conditional chain.

### Syntax

```axiom
i. hp > 0 do
    log("alive")
ef. hp == 0 do
    log("zero")
e. do
    log("dead")
end
```

### Example

```axiom
f. checkHP = (hp)
    i. hp > 50 do
        log("healthy")
    ef. hp > 0 do
        log("hurt")
    e. do
        log("down")
    end
fend.
```

---

## Imports

Axiom supports multiple import styles.

### `bring moduleName`

Import a module.

```axiom
bring math
```

### `bring moduleName as alias`

Import a module with an alias.

```axiom
bring axiomplay.core as core
bring axiomplay.draw as draw
```

### `look moduleName bring something`

Import selected values from a module.

```axiom
look math bring fabs
```

### `look moduleName bring a.`

Import everything from a module.

```axiom
look axiomplay bring a.
```

### Notes

`look axiomplay bring a.` is the most convenient way to expose the common AxiomPlay modules directly.

---

## Decorators

Axiom supports decorator-style syntax with `$`.

### Syntax

```axiom
$trace
f. test = ()
    ign
fend.
```

### Notes

Decorator behavior depends on compiler support.
The syntax is reserved and intended for function or method metadata.

---

## Built-in Console Functions

### `log(...)`

Print normal output.

```axiom
log("Hello")
```

### `warn(...)`

Print warning-style output.

```axiom
warn("Be careful")
```

### `error(...)`

Print error-style output.

```axiom
error("Something went wrong")
```

### Notes

In the current Python backend, these are mapped to Python-side printing helpers.
Avoid naming your own functions `print` unless the compiler/runtime has protected built-in console output properly.

---

## Special Keywords

### `ign`

Do nothing.
Equivalent to `pass` in Python.

```axiom
f. noop = ()
    ign
fend.
```

### `self`

Used inside class methods to refer to the current object.

```axiom
self.hp = 100
```

### `none`

Represents an empty/null value.

```axiom
g. player = none
```

### `true` / `false`

Boolean values.

```axiom
l. alive = true
```

---

## Indentation Rules

Axiom is indentation-sensitive inside blocks.
Use one indentation level per nested block.

### Rules

* inside `cls.`: indent 1 level
* inside `f.`: indent 1 more level
* inside `i. ... do`: indent 1 more level
* `fend.` aligns with `f.`
* `clsend.` aligns with `cls.`
* `end` aligns with `i.` / `ef.` / `e.`

### Good example

```axiom
cls. Player;
    f. update = (self, dt)
        i. self.hp > 0 do
            log("alive")
        end
    fend.
clsend.
```

### Bad example

```axiom
cls. Player;
    f. update = (self, dt)
    i. self.hp > 0 do
        log("alive")
    end
    fend.
clsend.
```

---

## Axiom Examples

### Hello World

```axiom
f. main = ()
    log("Hello Axiom")
fend.

main()
```

### Function Example

```axiom
f. add = (a, b)
    r. a + b
fend.

log(add(4, 5))
```

### Class Example

```axiom
cls. Enemy;
    f. init = (self, name, hp)
        self.name = name
        self.hp = hp
    fend.

    f. hit = (self, dmg)
        self.hp -= dmg
    fend.
clsend.

g. e = Enemy("Slime", 30)
e.hit(10)
```

### Conditional Example

```axiom
l. hp = 25

i. hp > 50 do
    log("healthy")
ef. hp > 0 do
    log("hurt")
e. do
    log("dead")
end
```

---

# AxiomPlay

## Overview

**AxiomPlay** is the 2D game framework for Axiom.
It is designed for windowed game applications and engine-style scripting.

AxiomPlay currently focuses on:

* creating and controlling the game window
* update/render loop management
* keyboard and mouse input
* drawing primitive shapes and text
* asset loading
* simple game state architecture

---

## Quick Start

```axiom
look axiomplay bring a.

cls. Player;
    f. init = (self, x, y)
        self.x = x
        self.y = y
        self.speed = 200
    fend.

    f. update = (self, dt)
        i. input.keyDown("a") do
            self.x -= self.speed * dt
        end

        i. input.keyDown("d") do
            self.x += self.speed * dt
        end
    fend.

    f. render = (self)
        draw.rect(self.x, self.y, 60, 60)
    fend.
clsend.

g. player = Player(100, 100)

f. load = ()
    core.title("AxiomPlay Demo")
    core.size(960, 540)
fend.

f. update = (dt)
    player.update(dt)
fend.

f. render = ()
    draw.clear(20, 20, 30)
    player.render()
fend.

core.run(load, update, render)
```

---

## Modules

## core

Main game startup and window control.

### `core.title(text)`

Set the window title.

**Parameters**

* `text` (`string`): window title text

**Example**

```axiom
core.title("My Game")
```

---

### `core.size(width, height)`

Set the window size.

**Parameters**

* `width` (`number`): width in pixels
* `height` (`number`): height in pixels

**Example**

```axiom
core.size(960, 540)
```

---

### `core.icon(path)`

Set the window icon.

**Parameters**

* `path` (`string`): path to an image file

**Example**

```axiom
core.icon("my_icon.png")
```

---

### `core.run(loadFn, updateFn, renderFn)`

Start the main game loop.

**Parameters**

* `loadFn` (`function`): called once at startup
* `updateFn` (`function`): called every frame with `dt`
* `renderFn` (`function`): called every frame for drawing

**Example**

```axiom
core.run(load, update, render)
```

---

## draw

Rendering helpers.

### `draw.clear(r, g, b)`

Clear the frame using an RGB color.

```axiom
draw.clear(20, 20, 30)
```

### `draw.rect(x, y, w, h)`

Draw a rectangle.

**Parameters**

* `x` (`number`)
* `y` (`number`)
* `w` (`number`)
* `h` (`number`)

```axiom
draw.rect(100, 100, 60, 60)
```

### `draw.circle(x, y, radius)`

Draw a circle.

```axiom
draw.circle(300, 200, 40)
```

### `draw.text(message, x, y)`

Draw text on screen.

**Parameters**

* `message` (`string`)
* `x` (`number`)
* `y` (`number`)

```axiom
draw.text("Hello", 20, 20)
```

### `draw.image(sprite, x, y)`

Draw an image/texture reference.

```axiom
draw.image(playerSprite, 100, 100)
```

### `draw.sprite(texture, x, y, sx, sy, rot)`

Draw a sprite with optional scale/rotation style parameters.

```axiom
draw.sprite(playerTex, 100, 100, 1, 1, 0)
```

---

## input

Keyboard and mouse input helpers.

### `input.keyDown(key)`

Return whether a key is currently being held.

```axiom
i. input.keyDown("a") do
    log("moving left")
end
```

### `input.keyPressed(key)`

Return whether a key was pressed this frame.

```axiom
i. input.keyPressed("space") do
    log("jump")
end
```

### `input.mouseDown(button)`

Return whether a mouse button is currently held.

```axiom
i. input.mouseDown("left") do
    log("holding mouse")
end
```

### `input.mousePressed(button)`

Return whether a mouse button was pressed this frame.

```axiom
i. input.mousePressed("left") do
    log("clicked")
end
```

### `input.mouseX()`

Return the current mouse x position.

```axiom
l. mx = input.mouseX()
```

### `input.mouseY()`

Return the current mouse y position.

```axiom
l. my = input.mouseY()
```

---

## audio

Audio playback helpers.

### `audio.play(sound)`

Play a sound.

```axiom
audio.play(hitSound)
```

### `audio.stop(sound)`

Stop a sound.

```axiom
audio.stop(hitSound)
```

### `audio.music(sound, looped)`

Play music, optionally looped.

```axiom
audio.music(bgMusic, true)
```

---

## assets

Asset loading helpers.

### `assets.image(path)`

Load an image asset.

```axiom
l. playerTex = assets.image("player.png")
```

### `assets.sound(path)`

Load a sound asset.

```axiom
l. hitSound = assets.sound("hit.wav")
```

### `assets.font(path, size)`

Load a font asset.

```axiom
l. fontMain = assets.font("font.ttf", 16)
```

---

## camera

Simple camera holder.

### `camera.Camera()`

Create a camera object.

### `Camera.follow(target)`

Move the camera to follow a target with `x` and `y` properties.

```axiom
l. cam = camera.Camera()
cam.follow(player)
```

---

## physics

Basic physics/collision helpers.

### `physics.box(x, y, w, h)`

Create a box body.

```axiom
l. body = physics.box(100, 100, 32, 32)
```

### `physics.overlaps(a, b)`

Return whether two bodies overlap.

```axiom
i. physics.overlaps(hitbox, enemyBox) do
    log("hit")
end
```

### `physics.Body`

Body class with basic position and size properties.

Common fields:

* `x`
* `y`
* `w`
* `h`
* `vx`
* `vy`
* `solid`

---

## scene

Scene management helpers.

### `scene.Scene(name)`

Create a scene.

### `Scene.add(obj)`

Add an object/entity to the scene.

### `Scene.load()`

Scene startup hook.

### `Scene.update(dt)`

Scene update hook.

### `Scene.render()`

Scene render hook.

Example:

```axiom
cls. MainScene;
    f. init = (self)
        self.name = "main"
        self.entities = []
    fend.

    f. render = (self)
        draw.text("Main Scene", 40, 40)
    fend.
clsend.
```

---

## entity

Base object helpers.

### `entity.Entity(x, y)`

Create a base entity.

Common fields:

* `x`
* `y`
* `visible`
* `active`
* `tag`

### `Entity.update(dt)`

Per-frame update hook.

### `Entity.render()`

Render hook.

---

## save

Save/load helpers.

### `save.write(slot, data)`

Write data to a save slot.

```axiom
save.write("slot1", playerData)
```

### `save.read(slot)`

Read data from a save slot.

```axiom
l. data = save.read("slot1")
```

---

## AxiomPlay Example

```axiom
look axiomplay bring a.
bring math

cls. Player;
    f. init = (self, x, y)
        self.x = x
        self.y = y
        self.speed = 200
    fend.

    f. update = (self, dt)
        i. input.keyDown("space") do
            self.speed = 400
        e. do
            self.speed = 200
        end

        i. input.keyDown("a") do
            self.x -= self.speed * dt
        end

        i. input.keyDown("d") do
            self.x += self.speed * dt
        end

        i. input.keyDown("w") do
            self.y -= self.speed * dt
        end

        i. input.keyDown("s") do
            self.y += self.speed * dt
        end
    fend.

    f. render = (self)
        draw.rect(self.x, self.y, 60, 60)
        draw.text(str(math.fabs(self.x)) + ", " + str(math.fabs(self.y)), 0, 0)
    fend.
clsend.

g. player = Player(100, 100)

f. load = ()
    core.title("AxiomPlay Demo")
    core.size(960, 540)
fend.

f. update = (dt)
    player.update(dt)
fend.

f. render = ()
    draw.clear(20, 20, 30)
    player.render()
fend.

core.run(load, update, render)
```

---

# Known Limitations

* Axiom currently transpiles to Python rather than compiling directly to native code
* language/runtime behavior still depends on backend implementation details
* some advanced features such as loops, decorators, and richer type semantics may still be incomplete
* text rendering behavior may vary depending on the runtime backend
* some modules are starter-framework level and may need further expansion for full production games

