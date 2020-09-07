import pygame
import random
from time import sleep
import math

pygame.init()

# DEFINING THE ESSENTIALS #

fps = 50  # frames per second (standard: 50)
display_x = 800  # screen width in pixel (standard: 800)
display_y = 480  # screen hight in pixel (standard: 480)

insetSize = 180  # inset for the radial cut

# start postion of ion (relative to center)
xi = 0
yi = 0.4
zi = 0
vxi = 100
vyi = 0
vzi = 60

# start postion of atom
ya = 0.5
za = 0.5
vya = 0
vza = 0

# constant zooms
zoomR = 2
zoomZ = 2
zoomInset = 42

white = (255, 255, 255)
black = (0, 0, 0)
atomcolor = (255, 0, 0)
ioncolor = (0, 0, 255)
linecolor = (100, 100, 100)
mainFont = pygame.font.Font('Kirang Haerang regular.ttf', 50)

# wire positions for r0=1
wirepos1 = 0.382683
wirepos2 = 0.92388


class vector:  
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        
    def __repr__(self):
        return "[{}, {}, {}]".format(self.x, self.y, self.z)
        
    def __add__(self, other):
        return vector(self.x + other.x, self.y + other.y, self.z + other.z)
        
    def __sub__(self, other):
        return vector(self.x - other.x, self.y - other.y, self.z - other.z)
        
    def __mul__(self, other):
        if isinstance(other, vector):
            return self.x * other.x + self.y * other.y + self.z * other.z
        elif isinstance(other, (int, float, complex)):
            return vector(self.x * other, self.y * other, self.z * other)
        return NotImplemented
        
    def __truediv__(self, other):
        if isinstance(other, (int, float, complex)):
            return vector(self.x / other, self.y / other, self.z / other)
        return NotImplemented
        
    def __abs__(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
        
    def rotate(self, theta, phi):
        radius = math.sqrt(self.x**2 + self.y**2 + self.z**2)
        self.x = radius * math.cos(phi) * math.sin(theta)
        self.y = radius * math.sin(phi) * math.sin(theta)
        self.z = radius * math.cos(theta)


class particleAtom:
    
    size = 20
    ypos = 0
    zpos = 0
    
    def __init__(self, status):
        self.status = status
        
    def display(self, zoom, color = (255, 0, 0)):
        self.ypos = int(center_y + self.status[0] * zoomR * zoom)
        self.zpos = int(center_x + self.status[2] * zoomZ * zoom)
        sizeScaled = int(self.size * zoom / 100)
        pygame.draw.circle(gameDisplay, color, (self.zpos, self.ypos), sizeScaled)
        
    def fly(self):
        speedSteps = 3
        dt = 2. * 10.**-4
        self.status[3] += accelerateZ * speedSteps
        self.status[1] += accelerateY * speedSteps
        self.status[0] += self.status[1] * dt
        self.status[2] += self.status[3] * dt


class particleIon:
    
    lengthTail = 400
    tail = [[yi, zi, xi, yi] for i in range(lengthTail)]
    maxR = 1
    maxZ = 1
    listN = 0
    size = 4
    mimo = 0
    mimoX = 0
    mimoY = 0

    def __init__(self, status):
        self.status = status
        
    def resetTail(self):
        current = self.tail[self.listN]
        self.tail = [current for i in range(lengthTail)]
        
    def display(self, zoom):
        for i in range(self.lengthTail - 1):
            n1 = (self.listN + i + 1) % self.lengthTail
            start = self.tail[n1]
            n2 = (self.listN + i + 2) % self.lengthTail
            end = self.tail[n2]
            ypos1 = int(center_y + start[0] * zoomR * zoom)
            zpos1 = int(center_x + start[1] * zoomZ * zoom)
            ypos2 = int(center_y + end[0] * zoomR * zoom)
            zpos2 = int(center_x + end[1] * zoomZ * zoom)
            color = (0, 0, int(i / (self.lengthTail - 1) * 255))
            sizeScaled = int(self.size * zoom / 100)
            pygame.draw.line(gameDisplay, color, (zpos1, ypos1), (zpos2, ypos2), sizeScaled)
        pygame.draw.circle(gameDisplay, color, (zpos2, ypos2), 3 * sizeScaled)
        
    def displayInset(self, zoom, cenX, cenY):
        for i in range(self.lengthTail - 1):
            n1 = (self.listN + i + 1) % self.lengthTail
            start = self.tail[n1]
            n2 = (self.listN + i + 2) % self.lengthTail
            end = self.tail[n2]
            xpos1 = int(cenX + start[2] * zoomR * zoomInset)
            ypos1 = int(cenY + start[3] * zoomR * zoomInset)
            xpos2 = int(cenX + end[2] * zoomR * zoomInset)
            ypos2 = int(cenY + end[3] * zoomR * zoomInset)
            color = (0, 0, int(i / (self.lengthTail - 1) * 255))
            pygame.draw.line(gameDisplay, color, (xpos1, ypos1), (xpos2, ypos2), 1)
        pygame.draw.circle(gameDisplay, color, (xpos2, ypos2), 3)

    def fly(self, time):
        mimo_frequ = 1.
        mimo_amp = 0.3
        # convert to cylindrical coordinates
        xpos = self.status[0]
        ypos = self.status[2]
        radius = math.sqrt(xpos**2 + ypos**2)
        phi = math.atan2(ypos, xpos)
        if phi < 0:
            phi += 2 * math.pi

        # calculate the velocity change
        dt = 2. * 10.**-4
        qx = 1. * 10**5
        qz = 1. * 10**3
        dvx = - qx * dt * radius**5 * math.cos(phi)
        dvy = - qx * dt * radius**5 * math.sin(phi)
        dvz = - qz * self.status[4] * dt

        # calculate new status
        self.status[1] += dvx
        self.status[3] += dvy
        self.status[5] += dvz
        self.status[0] += self.status[1] * dt
        self.status[2] += self.status[3] * dt
        self.status[4] += self.status[5] * dt
        self.mimo = radius**3 * mimo_amp * math.sin(time / mimo_frequ)
        self.mimoX = - self.mimo * math.cos(3 * (phi + 2 * math.pi / 16))
        self.mimoY = self.mimo * math.sin(3 * (phi + 2 * math.pi / 16))
        #self.size = int(3 + self.status[2] / self.maxR * 2)
        self.listN = time % self.lengthTail
        self.tail[self.listN] = [self.status[2] + self.mimo, self.status[4],
            self.status[0] + self.mimoX, self.status[2] + self.mimoY]
    
    def checkEnergy(self):
        qx = 1. * 10**5
        qz = 1. * 10**3
        xpos = self.status[0]
        ypos = self.status[2]
        radius = math.sqrt(xpos**2 + ypos**2)
        Veff = qx * radius**6 / 6
        Er = 1/2 * (self.status[1]**2 + self.status[3]**2) + Veff
        Vz = qz * self.status[4]**2 / 2
        Ez = 1/2 * self.status[5]**2 + Vz
        return [Er, Ez, (Er + Ez) / 20]

        
def collisionCheck(zoom):
    global collisionActive
    distanceY = abs(ion.status[2] - atom.status[0]) * zoomR * zoom
    distanceZ = abs(ion.status[4] - atom.status[2]) * zoomZ * zoom
    distance = math.sqrt(distanceZ**2 + distanceY**2)
    if distance <= (atom.size + ion.size * 3) * zoom / 100 and not collisionActive:
        collision()
        collisionActive = True
        print("collision detected")
    if collisionActive and distance > 2 * (atom.size + ion.size * 3) * zoom / 100:
        #collisionOver()
        collisionActive = False
        print("collision over")


def pickAngles():
    phi = random.uniform(0, 1) * 2 * math.pi
    while True:
        theta = random.uniform(0, 1) * math.pi
        test = random.uniform(0, 1)
        if math.sin(theta) > test:
            break
    return phi, theta


def collision():
    #global zoomNew
    #zoomNew = 250
    #global center_xNew 
    #center_xNew = display_x / 2 - atom.status[2] * zoomZ * zoomNew
    #global center_yNew 
    #center_yNew = display_y / 2 - atom.status[0] * zoomR * zoomNew
    mi = 17
    ma = 85
    energy = ion.checkEnergy()
    mimoMax = 2 * math.sqrt(2 * energy[0])
    factor = 100   #mimoMax / ion.mimo
    vix = factor * ion.mimoX + ion.status[1]
    viy = factor * ion.mimoY + ion.status[3]
    viz = ion.status[5]
    vi = vector(vix, viy, viz)
    vay = atom.status[1]
    vaz = atom.status[3]
    va = vector(0, vay, vaz)
    
    vrel = vi - va
    vcom = (vi * mi + va * ma) / (mi + ma)
    phi, theta = pickAngles()
    vrel.rotate(phi, theta)
    vinew = vcom + vrel * ma / (mi + ma)
    vanew = vcom - vrel * mi / (mi + ma)
    
    ion.status[1] = vinew.x - factor * ion.mimoX
    ion.status[3] = vinew.y - factor * ion.mimoY
    ion.status[5] = vinew.z
    atom.status[1] = vanew.y + vanew.x
    atom.status[3] = vanew.z
    
    global temp
    temp = ion.checkEnergy()
    tempText.value = temp[2]

   
def collisionOver():
    global zoomNew
    zoomNew = 100
    global center_xNew 
    center_xNew = display_x / 2
    global center_yNew 
    center_yNew = display_y / 2
    
    
def drawInset(zoom):
    # draw the surrounding rectangle
    xcorner = display_x - insetSize
    ycorner = display_y - insetSize
    inset = pygame.Surface((insetSize, insetSize))
    inset.fill((0, 0, 0))
    pygame.draw.rect(inset, white, (0, 0, insetSize, insetSize), 2)
    # draw atom if it is inside the inset
    check1 = atom.ypos > display_y - insetSize - atom.size * zoom / 100
    check2 = atom.zpos > display_x - insetSize - atom.size * zoom / 100
    if check1 and check2 :
        ypos = int(- display_y / 2 + insetSize + atom.status[0] * zoomR * zoom)
        xpos = int(- display_x / 2 + insetSize + atom.status[2] * zoomZ * zoom)
        sizeScaled = int(atom.size * zoom / 100)
        pygame.draw.circle(inset, (50, 0, 0), (xpos, ypos), sizeScaled)
    # draw wires
    color = (150, 100, 0)
    rad = 3
    cen = int(insetSize / 2)
    wire1 = int(wirepos1 * zoomInset * zoomR)
    wire2 = int(wirepos2 * zoomInset * zoomR)
    pygame.draw.circle(inset, color, (cen + wire2, cen + wire1), rad)
    pygame.draw.circle(inset, color, (cen - wire2, cen + wire1), rad)
    pygame.draw.circle(inset, color, (cen + wire2, cen - wire1), rad)
    pygame.draw.circle(inset, color, (cen - wire2, cen - wire1), rad)
    pygame.draw.circle(inset, color, (cen + wire1, cen + wire2), rad)
    pygame.draw.circle(inset, color, (cen - wire1, cen + wire2), rad)
    pygame.draw.circle(inset, color, (cen + wire1, cen - wire2), rad)
    pygame.draw.circle(inset, color, (cen - wire1, cen - wire2), rad)
    gameDisplay.blit(inset, (xcorner, ycorner))
    # draw the trajectory
    xcen = display_x - insetSize/2
    ycen = display_y - insetSize/2
    ion.displayInset(zoom, xcen, ycen)
    
    
def drawArrow(xpos, ypos):
    headL = 30
    headW = 35
    lineL = 30
    lineW = 20
    offset = atom.size * zoom / 100
    headX = math.sqrt(headW**2 + headL**2)
    headY = (headW - lineW) / math.sqrt(2)
    lineX = lineL / math.sqrt(2)
    if xpos < -offset and ypos < -offset:
        # arrow to the top left
        pygame.draw.polygon(gameDisplay, (255, 0, 0), ( 
            (headY + lineX, headX - headY + lineX),
            (headY, headX - headY),
            (0, headX),
            (0, 0),
            (headX, 0),
            (headX - headY, headY),
            (headX - headY + lineX, headY + lineX)))
    elif xpos > display_x + offset and ypos < -offset:
        # arrow to the top right
        pygame.draw.polygon(gameDisplay, (255, 0, 0), ( 
            (display_x - headY - lineX, headX - headY + lineX),
            (display_x - headY, headX - headY),
            (display_x, headX),
            (display_x, 0),
            (display_x - headX, 0),
            (display_x - headX + headY, headY),
            (display_x - headX + headY - lineX, headY + lineX)))
    elif xpos > display_x + offset and ypos > display_y + offset:
        # arrow to the bottom right
        pygame.draw.polygon(gameDisplay, (255, 0, 0), ( 
            (display_x - headY - lineX, display_y - headX + headY - lineX),
            (display_x - headY, display_y - headX + headY),
            (display_x, display_y - headX),
            (display_x, display_y),
            (display_x - headX, display_y),
            (display_x - headX + headY, display_y - headY),
            (display_x - headX + headY - lineX, display_y - headY - lineX)))
    elif xpos > display_x + offset and ypos > display_y + offset:
        # arrow to the bottom left
        pygame.draw.polygon(gameDisplay, (255, 0, 0), ( 
            (headY + lineX, display_y - headX + headY - lineX),
            (headY, display_y - headX + headY),
            (0, display_y - headX),
            (0, display_y),
            (headX, display_y),
            (headX - headY, display_y - headY),
            (headX - headY + lineX, display_y - headY - lineX)))
    elif xpos > display_x + offset:
        # arrow to the right
        pygame.draw.polygon(gameDisplay, (255, 0, 0), ( 
            (display_x - headL - lineL, ypos - lineW),
            (display_x - headL, ypos - lineW),
            (display_x - headL, ypos - headW),
            (display_x, ypos),
            (display_x - headL, ypos + headW),
            (display_x - headL, ypos + lineW),
            (display_x - headL - lineL, ypos + lineW)))
    elif xpos < -offset:
        # arrow to the left
        pygame.draw.polygon(gameDisplay, (255, 0, 0), ( 
            (headL + lineL, ypos - lineW),
            (headL, ypos - lineW),
            (headL, ypos - headW),
            (0, ypos),
            (headL, ypos + headW),
            (headL, ypos + lineW),
            (headL + lineL, ypos + lineW)))
    elif ypos > display_y + offset:
        # arrow to the bottom
        pygame.draw.polygon(gameDisplay, (255, 0, 0), ( 
            (xpos - lineW, display_y - headL - lineL),
            (xpos - lineW, display_y - headL),
            (xpos - headW, display_y - headL),
            (xpos, display_y),
            (xpos + headW, display_y - headL),
            (xpos + lineW, display_y - headL),
            (xpos + lineW, display_y - headL - lineL)))
    elif ypos < -offset:
        # arrow to the top
        pygame.draw.polygon(gameDisplay, (255, 0, 0), ( 
            (xpos - lineW, headL + lineL),
            (xpos - lineW, headL),
            (xpos - headW, headL),
            (xpos, 0),
            (xpos + headW, headL),
            (xpos + lineW, headL),
            (xpos + lineW, headL + lineL)))

           
class messageText:
    
    def __init__(self, text, font, color, xpos, ypos, numbers = False, alignment = 0):
        self.what = -1
        self.text = text
        self.numbers = numbers
        self.value = 0
        self.font = font
        self.color = color
        self.xpos = xpos
        self.ypos = ypos
        self.alignment = alignment
        
    def display(self, speed = None):
        if self.numbers:
            text = self.font.render(self.text + str(int(self.value)) + ' K', True, self.color)
        else:
            text = self.font.render(self.text, True, self.color)
        textRect = text.get_rect()
        textRect.center = (self.xpos, self.ypos)
        if self.alignment == -1:
            textRect.left = self.xpos
        if self.alignment == 1:
            textRect.right = self.xpos
        gameDisplay.blit(text, textRect)

    
def drawWires(zoom, wires, color = (255, 215, 0)):
    for wire in wires:
        wire1 = int(center_y + wire * zoom * zoomR)
        wire2 = int(center_y - wire * zoom * zoomR)
        pygame.draw.line(gameDisplay, color, (0, wire1), (display_x, wire1), 3)
        pygame.draw.line(gameDisplay, color, (0, wire2), (display_x, wire2), 3)


def updateScreen(zoom):
    gameDisplay.fill((0, 0, 0))
    drawWires(zoom, [wirepos1 - 0.05, wirepos2 - 0.025], (100, 60, 0))
    ion.display(zoom)
    atom.display(zoom)
    drawWires(zoom, [wirepos1 + 0.05, wirepos2 + 0.025], (200, 150, 0))
    drawInset(zoom)
    tempText.display()
    drawArrow(atom.zpos, atom.ypos)
    pygame.display.update()
    clock.tick(fps)

    
def flyParticles(zoom):
    global time
    ion.fly(time)
    atom.fly()
    collisionCheck(zoom)
    time += 1
    ion.checkEnergy()


zoomSteps = 100
zoomCounter = 0
collisionActive = False
zoomActive = False
zoom = 30.
zoomNew = 30.

ion = particleIon([xi, vxi, yi, vyi, zi, vzi])
atom = particleAtom([ya, vya, za, vza])

center_x = display_x / 2.
center_y = display_y / 2.
center_xNew = display_x / 2.
center_yNew = display_y / 2.

gameDisplay = pygame.display.set_mode((display_x, display_y))
pygame.display.set_caption('Ion coooooooooling...')
clock = pygame.time.Clock()
time = 0

gameExit = False
accelerateY = 0
accelerateZ = 0

temp = ion.checkEnergy()
tempText = messageText('current temperature: ', mainFont, (0, 0, 255), display_x * 0.13, 28, True, -1)
tempText.value = temp[2]

while not gameExit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameExit = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                gameExit = True
            if event.key == pygame.K_LEFT:
                accelerateZ += -1
            if event.key == pygame.K_RIGHT:
                accelerateZ += 1
            if event.key == pygame.K_DOWN:
                accelerateY += 1
            if event.key == pygame.K_UP:
                accelerateY += -1
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                accelerateZ += 1
            if event.key == pygame.K_RIGHT:
                accelerateZ += -1
            if event.key == pygame.K_DOWN:
                accelerateY += -1
            if event.key == pygame.K_UP:
                accelerateY += 1
            
    
    if zoomActive == False:
        zooming = zoomNew - zoom
        shiftingX = center_xNew - center_x
        shiftingY = center_yNew - center_y
    
    if abs(zooming) < 0.01 and abs(shiftingX) < 0.01 and abs(shiftingY) < 0.01 or zoomCounter == zoomSteps:
        zoomActive = False
        zoomCounter = 0
        flyParticles(zoom)
    else:
        zoomActive = True
        zoomCounter += 1
        zoom += zooming / zoomSteps
        center_x += shiftingX / zoomSteps
        center_y += shiftingY / zoomSteps
        
    if time == 200:
        zoomNew = 100.

    updateScreen(zoom)

pygame.quit()
quit()
