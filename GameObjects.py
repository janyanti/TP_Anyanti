##############################################
# Game Objects | 15-112 Term Project
#  Joel Anyanti | Janyanti
##############################################

##############################################
# Imports
##############################################

import pygame as pg
import os
import Note
from Settings import *
import random

##############################################
# Class Functions
##############################################


def load_images(filename):
    imagefile = filename + '.png'
    path = os.path.join('assets', imagefile)
    image = pg.image.load(path)
    return image


def joinFuntion(obj, function):
    result = obj + '.' + function
    return result


##############################################
# Classes
##############################################

class GameObject(pg.sprite.Sprite):
    # Generic game sprite object
    def __init__(self, x, y, image, radius):
        super(GameObject, self).__init__()
        # x, y define the center of the object
        self.x, self.y, self.image, self.radius = x, y, image.convert_alpha(), radius
        self.baseImage = image.copy()  # non-rotated version of image
        w, h = image.get_size()
        self.updateRect()
        self.velocity = (0, 0)
        self.angle = 0

    def updateRect(self):
        # update the object's rect attribute with the new x,y coordinates
        w, h = self.image.get_size()
        self.width, self.height = w, h
        self.rect = pg.Rect(self.x - w / 2, self.y - h / 2, w, h)

    def update(self, screenWidth=WIDTH, screenHeight=HEIGHT):
        self.image = pg.transform.rotate(self.baseImage, self.angle)
        vx, vy = self.velocity
        # self.x += vx
        # self.y += vy
        self.updateRect()
        # wrap around, and update the rectangle again
        if self.rect.left > screenWidth:
            self.x -= screenWidth + self.width
        elif self.rect.right < 0:
            self.x += screenWidth + self.width
        if self.rect.top > screenHeight:
            self.y -= screenHeight + self.height
        elif self.rect.bottom < 0:
            self.y += screenHeight + self.height
        self.updateRect()


class Hero(GameObject):
    img = load_images('hero_down')
    direction = 1
    spawnable = ['spawn1', 'spawn2', 'spawn3',
                 'spawn4', 'spawn5']

    def __init__(self, x=WIDTH // 3, y=STEP * 5):
        super().__init__(x, y, Hero.img, 20)
        self.dy = Lines.margin
        self.dx = 0
        self.loadFrames()
        self.image = self.frames[0].convert_alpha()
        self.currentFrame = 0
        self.prev_time = 0
        self.velocity = (0, 0)
        self.baseImage = self.image

    def changeDirection(self, dir):
        if dir == Hero.direction:
            return
        Hero.direction = dir

    def move(self, screenWidth, screenHeight):
        self.y += self.dy * Hero.direction
        self.updateRect()

    def cpuMove(self, height):
        self.y = height
        self.updateRect()

    def update(self, screenWidth=WIDTH, screenHeight=HEIGHT):
        super().update(screenWidth, screenHeight)
        self.animate()

    def loadFrames(self):
        images = ['hero_down', 'hero_up1',
                  'hero_up', 'hero_down1']
        loaded = []
        for file in images:
            loaded.append(load_images(file))
        self.frames = loaded

    def animate(self):
        currTime = pg.time.get_ticks()
        if currTime - self.prev_time > 350:
            self.prev_time = currTime
            self.currentFrame = (self.currentFrame + 1) % len(self.frames)
            self.updateFrame(self.frames[self.currentFrame])

    def updateFrame(self, frame):
        self.image = frame
        self.baseImage = frame

    def spawnNote(self):
        x, y = self.x, self.y + 25
        max = len(startHero.spawnable) - 1
        index = random.randint(0, max)
        spawnImage = startHero.spawnable[index]
        image = load_images(spawnImage)
        spawned = spawnedNote(x, y, image)
        return spawned


class startHero(Hero):
    spawnable = ['spawn1', 'spawn2', 'spawn3',
                 'spawn4', 'spawn5']

    def __init__(self, x=WIDTH // 2, y=0 + STEP * 2):
        super(startHero, self).__init__(x, y)
        self.dx = 2
        self.dy = 0
        self.velocity = (self.dx, self.dy)

    def spawnNote(self):
        x, y = self.x, self.y + 25
        max = len(startHero.spawnable) - 1
        index = random.randint(0, max)
        spawnImage = startHero.spawnable[index]
        image = load_images(spawnImage)
        spawned = spawnedNote(x, y, image)
        return spawned

    def update(self, screenWidth=WIDTH, screenHeight=HEIGHT):
        super().update()
        dx, dy = self.velocity
        # self.x += dx
        if not STEP < self.x < WIDTH - STEP:
            self.dx *= -1
        self.velocity = (self.dx, dy)
        self.updateRect()


class MusicNote(GameObject):
    noteheads = ['notehead', 'halfnotehead', 'wholenotehead']
    stem = load_images('stem')
    sharp = load_images('sharp')
    cross = load_images('cross')
    notesDict = dict()

    def __init__(self, stem, x, note, dx, y=0, img=0, rad=20, ):
        self.x, self.y = x, y
        self.Note = note
        self.stem = stem
        self.type = self.noteType()
        # self.type = note.getType()
        self.getNoteHeadIndex()
        image = load_images(MusicNote.noteheads[self.noteHeadIndex])
        super(MusicNote, self).__init__ \
            (x, y, image, rad)
        self.image.convert_alpha()
        self.dx = dx
        self.velocity = (-self.dx, 0)
        self.y = self.Note.getHeight()


    def draw(self, screen):
        self.rect = self.getRect()
        screen.blit(self.image, self.rect)
        stemRect = self.noteType()
        if not self.type == 'whole':
            screen.blit(MusicNote.stem, stemRect)
        sharpRect = self.getSharpRect()
        if self.Note.isAccidental():
            screen.blit(MusicNote.sharp, sharpRect)
        if self.Note.cross:
            screen.blit(MusicNote.cross, self.getCrossRect())

    def getNoteHeadIndex(self):
        typ = self.type
        index = 0
        if typ is 'whole':
            index = 2
        elif typ is 'half':
            index = 1
        else:
            index = 0
        self.noteHeadIndex = index

    def getRect(self):
        # gets Rect attribute of note
        w, h = self.image.get_size()
        self.width, self.height = w, h
        rect = pg.Rect(self.x - w // 2, self.y - h // 2, w, h)
        return rect

    def getCrossRect(self):
        x, y = self.x, self.y
        w, h = 75, 3
        rect = pg.Rect(x - w // 2, y - h // 2, w, h)
        return rect

    def getSharpRect(self):
        # gets position of accidental
        x, y = self.x - 40, self.y + 5
        w, h = 26, 60
        rect = pg.Rect(x - w // 2, y - h // 2, w, h)
        return rect

    def noteType(self):
        # returns the orientation of a given note
        x, y = self.x, self.y
        if self.stem == 'up':
            return pg.Rect(x + 15, y - 105, x + 17, y)
        else:
            return pg.Rect(x - 19, y, x - 21, y + 105)
        # clef = self.Note.getClef()
        # noteID = self.Note.noteID
        # if clef is "Treble":
        #     if noteID >= 71:
        #         return downNote
        #     return upNote
        # if clef is 'Bass':
        #     if noteID >= 50:
        #         return downNote
        #     return upNote

    def checkStem(self):
        if not self.group in MusicNote.notesDict:
            result = self.noteType()
            MusicNote.notesDict[self.group] = result
            self.type = result
        else:
            self.type = MusicNote.notesDict[self.group]


    def update(self, screenWidth=WIDTH, screenHeight=WIDTH):
        self.image = pg.transform.rotate(self.baseImage, self.angle)
        vx, vy = self.velocity
        self.x += vx
        self.y += vy
        self.updateRect()


class spawnedNote(GameObject):
    def __init__(self, x, y, img, rad=0):
        super().__init__(x, y, img, rad)
        dx = random.randint(-2, 2)
        self.velocity = (dx, 10)
        self.maxDx = 2
        self.dx = 2
        self.updateRect()

    def update(self, screenWidth=WIDTH, screenHeight=HEIGHT):
        dx, dy = self.velocity
        self.x += dx
        self.y += dy
        if dx > 0:
            dx *= 1.1
        elif dx >= self.maxDx:
            dx = -self.dx
        if dx < 0:
            dx *= 1.1
        elif dx <= -self.maxDx:
            dx = self.dx
        self.velocity = (dx, dy)
        if not 0 < self.x < WIDTH:
            self.kill()
        if not 0 < self.y < HEIGHT:
            self.kill()
        self.updateRect()


class Lines(pg.sprite.Sprite):
    # line object used to draw staff lines
    lineSpace = HEIGHT / 16
    margin = STEP
    clefLines = 5

    def __init__(self, x, y):
        super(Lines, self).__init__()
        self.x = x
        self.y = y
        self.height = 2
        self.width = WIDTH - 2 * Lines.margin
        w, h = self.width, self.height
        self.rect = pg.Rect(self.x, self.y, w, h)

    def draw(self, screen):
        rect = self.rect
        pg.draw.rect(screen, BLACK, rect, 0)

    @staticmethod
    def generateStaff():
        # makes music sheet ledger for game
        linesList = []
        x = Lines.margin
        y = Lines.margin * 4

        # Treble Clef Lines
        for i in range(Lines.clefLines):
            line = Lines(x, y)
            linesList.append(line)
            y += Lines.margin

        y += Lines.margin * 6
        # Bass Clef Lines
        for i in range(Lines.clefLines):
            line = Lines(x, y)
            linesList.append(line)
            y += Lines.margin

        linesList.append(LedgerLine(STEP, STEP * 4))
        linesList.append(LedgerLine(WIDTH - STEP, STEP * 4))
        return linesList


class LedgerLine(pg.sprite.Sprite):
    def __init__(self, x, y):
        super(LedgerLine, self).__init__()
        self.x = x
        self.y = y
        self.height = 452
        self.width = 4
        w, h = self.width, self.height
        self.rect = pg.Rect(self.x, self.y, w, h)

    def draw(self, screen):
        rect = self.rect
        pg.draw.rect(screen, BLACK, rect, 0)


class TrebleClef(GameObject):
    image = load_images('treble')

    def __init__(self, x, y):
        super(TrebleClef, self).__init__(x, y, TrebleClef.image, 20)


class BassClef(GameObject):
    image = load_images('bass')

    def __init__(self, x, y):
        super(BassClef, self).__init__(x, y, BassClef.image, 20)


class NextNote(pg.sprite.Sprite):
    # should be a part of player class
    def __init__(self):
        super(NextNote, self).__init__()
        self.x = WIDTH // 2
        self.y = HEIGHT // 2 + NOTESTEP
        self.width = NOTESTEP * 12
        self.height = NOTESTEP * 6
        self.defineRect()

    def defineRect(self):
        w, h = self.width, self.height
        x, y = self.x, self.y
        self.rect = pg.Rect((x - w / 2, y - h / 2), (w, h))
        self.image = pg.Surface((w, h))
        self.image.fill(WHITE)


class Button(pg.sprite.Sprite):
    actions = {'play': 'play', 'help': 'help', 'options': 'options',
               'next': 'next', 'back': 'back', 'retry': 'play',
               'newsong': 'select', 'mainmenu': 'start', 'backarrow': 'start'}

    def __init__(self, x, y, image):
        super(Button, self).__init__()
        self.x, self.y = x, y
        self.name = image
        self.image = load_images(image)
        w, h = self.image.get_size()
        self.width, self.height = w, h
        self.defineRect()

    def defineRect(self):
        w, h = self.width, self.height
        x, y = self.x, self.y
        self.rect = pg.Rect((x - w / 2, y - h / 2), (w, h))

    def click(self, actionCode):
        action = Button.actions[actionCode]
        return action


class SongFile(pg.sprite.Sprite):
    songs = ['canon', 'the_entertainer', 'minuet', 'ode_to_joy']
    status = dict()
    songFileList = []

    def __init__(self, x, y, index=0):
        super(SongFile, self).__init__()
        self.x, self.y = x, y
        self.name = SongFile.songs[index]
        self.id = 'music/' + self.name + '.mid'
        self.image = load_images(SongFile.songs[index])
        w, h = self.image.get_size()
        self.width, self.height = w, h
        self.defineRect()
        SongFile.status[self.name] = False
        SongFile.songFileList.append(self)

    def defineRect(self):
        w, h = self.width, self.height
        x, y = self.x, self.y
        self.rect = pg.Rect((x - w / 2, y - h / 2), (w, h))

    def getRect(self):
        w, h = self.width, self.height
        x, y = self.x, self.y
        return x, y, w, h

    def click(self):
        status = SongFile.status
        if status[self.name]:
            SongFile.status[self.name] = False
            self.recolor()
            return
        for key in status:
            status[key] = False
        SongFile.status[self.name] = True
        for file in SongFile.songFileList:
            file.recolor()

    def recolor(self):
        imageName = self.name
        status = SongFile.status[imageName]
        if status:
            imageName += '_on'
        self.image = load_images(imageName)
        self.update()


class InputModes(pg.sprite.Sprite):
    modes = ['cpumode', 'dualmode', 'singlemode', 'pianomode']
    status = dict()
    modesList = []

    def __init__(self, x, y, index=0):
        super(InputModes, self).__init__()
        self.x, self.y = x, y
        self.name = InputModes.modes[index]
        self.image = load_images(self.name)
        w, h = self.image.get_size()
        self.width, self.height = w, h
        self.defineRect()
        InputModes.status[self.name] = False
        InputModes.modesList.append(self)

    def defineRect(self):
        w, h = self.width, self.height
        x, y = self.x, self.y
        self.rect = pg.Rect((x - w / 2, y - h / 2), (w, h))

    def getRect(self):
        w, h = self.width, self.height
        x, y = self.x, self.y
        return x, y, w, h

    def click(self):
        status = InputModes.status
        if status[self.name]:
            InputModes.status[self.name] = False
            self.recolor()
            return
        for key in status:
            status[key] = False
        InputModes.status[self.name] = True
        for file in InputModes.modesList:
            file.recolor()

    def recolor(self):
        imageName = self.name
        status = InputModes.status[imageName]
        if status:
            imageName += '_on'
        self.image = load_images(imageName)
        self.update()


class NotesModes(pg.sprite.Sprite):
    modes = ['trebleplay', 'bassplay']
    status = dict()
    modesList = []

    def __init__(self, x, y, index=0):
        super(NotesModes, self).__init__()
        self.x, self.y = x, y
        self.name = NotesModes.modes[index]
        self.image = load_images(self.name)
        w, h = self.image.get_size()
        self.width, self.height = w, h
        self.defineRect()
        NotesModes.status[self.name] = False
        NotesModes.modesList.append(self)

    def defineRect(self):
        w, h = self.width, self.height
        x, y = self.x, self.y
        self.rect = pg.Rect((x - w / 2, y - h / 2), (w, h))

    def getRect(self):
        w, h = self.width, self.height
        x, y = self.x, self.y
        return x, y, w, h

    def click(self):
        status = NotesModes.status
        if status[self.name]:
            NotesModes.status[self.name] = False
            self.recolor()
            return
        for key in status:
            status[key] = False
        NotesModes.status[self.name] = True
        for file in NotesModes.modesList:
            file.recolor()

    def recolor(self):
        imageName = self.name
        status = NotesModes.status[imageName]
        if status:
            imageName += '_on'
        self.image = load_images(imageName)
        self.update()


class NotePortal(pg.sprite.Sprite):
    states = ['noteportal', 'noteportal_hit', 'noteportal_miss']

    def __init__(self, y, x=422, state=0):
        super(NotePortal, self).__init__()
        self.x, self.y = x, y
        self.name = NotePortal.states[state]
        self.image = load_images(self.name)
        w, h = self.image.get_size()
        self.width, self.height = w, h
        self.defineRect()
        self.radius = 80
        self.images = self.getImageStates()

    def defineRect(self):
        w, h = self.width, self.height
        x, y = self.x, self.y
        self.rect = pg.Rect((x - w / 2, y - h / 2), (w, h))

    def getRect(self):
        w, h = self.width, self.height
        x, y = self.x, self.y
        return x, y, w, h

    @staticmethod
    def getImageStates():
        stateImages = [load_images(state) for state in NotePortal.states]
        return stateImages

    def hit(self, n):
        state = self.images[n]
        self.image = state
        self.update()
