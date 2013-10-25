#Code by Ian Ford: Homework 7
import sys, math, random, time
from pyglet.gl import *
from pyglet.window import *

window = pyglet.window.Window(800,512)
player = pyglet.media.Player()

keyboard = key.KeyStateHandler()
window.push_handlers(keyboard)

jumpSound = pyglet.resource.media('jumpsound.wav', streaming = False)
shootSound = pyglet.resource.media('shootSound.wav', streaming = False)
bgSource = pyglet.resource.media('bgmus.wav')
player.queue(bgSource)
player.eos_action = pyglet.media.Player.EOS_LOOP
player.play() #Plays background music

tex1 = pyglet.image.load('sky.png').get_texture()
tex2 = pyglet.image.load('clouds.png').get_texture()
tex3 = pyglet.image.load('backdrop.png').get_texture()
tex4 = pyglet.image.load('levels.png').get_texture()
monTex = pyglet.image.load('monster.png').get_texture()

level0 = pyglet.graphics.vertex_list(4, ('v2f', [0,0, 1028,0, 0,512, 1028,512]), ('t2f', [0,0, 1,0, 0,1, 1,1]))
level1 = pyglet.graphics.vertex_list(4, ('v2f', [0,0, 1028,0, 0,512, 1028,512]), ('t2f', [0,0, 1,0, 0,1, 1,1]))
level2 = pyglet.graphics.vertex_list(4, ('v2f', [0,0, 1028,0, 0,512, 1028,512]), ('t2f', [0,0, 1,0, 0,1, 1,1]))
level3 = pyglet.graphics.vertex_list(4, ('v2f', [0,0, 1028,0, 0,512, 1028,512]), ('t2f', [0,0, 1,0, 0,1, 1,1]))
charVert = pyglet.graphics.vertex_list(4, ('v2f', [400,40, 128+400,40, 400,168, 128+400,168]), ('t2f', [0,0, 1,0, 0,1, 1,1]))

levelArray = [880,155, 1023,155, 880,250, 1023,250, 490,305, 879,305, 305,340, 440,340, 0,300, 255,300] #Keeps track of all platforms

def BoxCollidesWithBox(box1, box2, move1, move2, pos1, pos2):
    return (box1[0]+pos1[0]+move1-x <= box2[4]+pos2[0]+move2) and (box1[4]+pos1[0]+move1-x >= box2[0]+pos2[0]+move2) and (box1[1]+pos1[1] <= box2[5]+pos2[1]) and (box1[5]+pos1[1] >= box2[1]+pos2[1])

def CharCollidesWithBox(charX, charY, monsterArray, monsterMove, monsterPos):
        return (charX+400-x+30 <= monsterArray[4]+monsterPos[0]+monsterMove) and (charX+400+128-x-30 >= monsterArray[0]+monsterPos[0]+monsterMove) and (charY <= monsterArray[5]+monsterPos[1]) and (charY+128 >= monsterArray[1]+monsterPos[1])

class monsterSprite: #MONSTERS
    def __init__(self, width, height, pos, texture, health, x1, x2):
        self.movement = 0;
        self.xMin = x1
        self.xMax = x2
        self.width = width
        self.height = height
        self.pos = pos
        self.texture = texture
        self.directionCheck = True
        self.health = health
        self.verts = [-self.width/2.0,-self.height/2.0 ,self.width/2.0,-self.height/2.0 ,self.width/2.0,self.height/2.0, -self.width/2.0,self.height/2.0]
        self.vlistMon = pyglet.graphics.vertex_list(4, ('v2f',self.verts), ('t2f', [0,0,1,0,1,1,0,1]))
    def update(self, number):
        global obj
        if self.movement >= self.xMax-self.pos[0]-32 or not self.directionCheck: #Limit monsters to stay on the map
            self.movement -= 2
            self.directionCheck = False
        if self.movement <= self.xMin-self.pos[0]+32 or self.directionCheck:
            self.movement += 2
            self.directionCheck = True
        ranCheck = random.randint(0,1000) #Change Direction of Monsters
        if ranCheck == 24 and self.directionCheck:
            self.directionCheck = False
        if ranCheck == 9 and not self.directionCheck:
            self.directionCheck = True
        if self.health <= 0:
            for c in range(0,2):
                temp = monsterSprite(self.width, self.height, [random.randint(self.xMin,self.xMax), self.pos[1]], self.texture, self.health+100, self.xMin, self.xMax)
                obj += [temp]
            obj.pop(number)
    def draw(self):
        glPushMatrix()
        glTranslatef(self.pos[0]+x+self.movement, self.pos[1], 0)
        glBindTexture(GL_TEXTURE_2D, self.texture.id)
        self.vlistMon.draw(GL_QUADS)
        glPopMatrix()

class bulletSprite: #BULLETS
    def __init__(self, pos, orien):
        self.movement = 0;
        self.width = 64
        self.height = 64
        self.orientation = orien
        self.pos = pos
        self.texture = monTex
        self.verts = [-self.width/2.0,-self.height/2.0 ,self.width/2.0,-self.height/2.0 ,self.width/2.0,self.height/2.0, -self.width/2.0,self.height/2.0]
        self.vlistBul = pyglet.graphics.vertex_list(4, ('v2f',self.verts), ('t2f', [0,0, 1,0 ,1,1, 0,1]))
    def update(self):
        global bulletLimiter, bullets
        if self.orientation == False:
            self.movement -= 6
        if self.orientation == True:
            self.movement += 6
        if self.movement >= 200 or self.movement <= -200:
            bullets.pop(0)
        if (self.movement >= 82 and self.movement <= 86) or (self.movement <= -82 and self.movement >= -86):
            bulletLimiter = True
    def draw(self):
        glPushMatrix()
        glTranslatef(self.pos[0]+self.movement, self.pos[1], 0)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor3f(0,1,0)
        glBindTexture(GL_TEXTURE_2D, self.texture.id)
        self.vlistBul.draw(GL_QUADS)
        glColor3f(1,1,1)
        glPopMatrix()

jump = False #JUMP LIMITER
up = False #FLOAT LIMITER
jumpY = 0 #Keeps track of how high one has jumped since leaving the platform

currentLevel = [0,0] #Keeps x values of the current platform
onLevel = False #True = ON A PLATFORM, False = ON BASE LEVEL

cloudx = 0 #CLOUD MOVEMENT
x = 0 #MAP MOVEMENT
charx = 0 #CHARACTER X LOCATION
chary = 0 #CHARACTER Y LOCATION
charOrientation = True #True = RIGHT, False = LEFT
bulletLimiter = True #BULLET SHOOTING SPEED LIMITER

monst1 = monsterSprite(128,128,[random.randint(100,1000),100],monTex, 100, 0,1028) #Bottom Level
monst2 = monsterSprite(128,128,[random.randint(490,879),100+265],monTex, 100, 490,879) #Top Right Platform
monst3 = monsterSprite(128,128,[random.randint(0,255),100+265],monTex, 100, 0,255) #Top Left Platform

score = 0
health = 100

label1 = pyglet.text.Label('Score:', font_name='Times New Roman', font_size=36, x=60, y=25, anchor_x='center', anchor_y='center')
label2 = pyglet.text.Label(str(score), font_name='Times New Roman', font_size=36, x=200, y=25, anchor_x='center', anchor_y='center')
label3 = pyglet.text.Label('Health:', font_name='Times New Roman', font_size=36, x=600, y=25, anchor_x='center', anchor_y='center')
label4 = pyglet.text.Label(str(health), font_name='Times New Roman', font_size=36, x=740, y=25, anchor_x='center', anchor_y='center')


obj = [monst1, monst2, monst3]

bullets = []

@window.event
def on_draw():
    glClearColor(0, 0, 0, 0)
    glClear(GL_COLOR_BUFFER_BIT)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    #BACKGROUND
    glBindTexture(GL_TEXTURE_2D, tex1.id)
    glTranslatef(x*0.1,0,0)
    level0.draw(GL_TRIANGLE_STRIP)
    glTranslatef(-x*0.1,0,0)

    #CLOUDS
    glPushMatrix()
    glBindTexture(GL_TEXTURE_2D, tex2.id)
    glTranslatef(cloudx+(x*0.3),0,0)
    level1.draw(GL_TRIANGLE_STRIP)
    glTranslatef(1024,0,0)
    level1.draw(GL_TRIANGLE_STRIP)
    glTranslatef(-cloudx-1024-(x*0.3),0,0)
    glPopMatrix()

    #BACKDROP
    glBindTexture(GL_TEXTURE_2D, tex3.id)
    glTranslatef(x*0.7,0,0)
    level2.draw(GL_TRIANGLE_STRIP)
    glTranslatef(-x*0.7,0,0)

    #LEVELS (PLATFORMS)
    glBindTexture(GL_TEXTURE_2D, tex4.id)
    glTranslatef(x,0,0)
    level3.draw(GL_TRIANGLE_STRIP)
    glTranslatef(-x,0,0)
    
    #PLAYABLE CHARACTER
    glBindTexture(GL_TEXTURE_2D, monTex.id)
    glColor3f(1,0,0)
    glTranslatef(charx,chary,0)
    charVert.draw(GL_TRIANGLE_STRIP)
    glColor3f(1,1,1)
    glTranslatef(-charx,-chary,0)

    #MONSTERS
    for o in obj:
        o.draw()

    #BULLETS
    for b in bullets:
        b.draw()

    #Score Keeper/Player Health Display
    label1.draw()
    label2.draw()
    label3.draw()
    label4.draw()

    glDisable(GL_BLEND)
    glDisable(GL_TEXTURE_2D)

hitAmmo = 0

def update(dt):
    global x, cloudx, charx, chary, jump, up, jumpY, levelArray, currentLevel, onLevel, bullets, charOrientation, bulletLimiter, obj, score, hitAmmo, health

    label2.text = str(score) #Update Score
    label4.text = str(health) #Update Health
    
    #MONSTER MOVEMENT UPDATE
    for o in range(0, len(obj)):
        obj[o].update(o)
        
    #BULLET MOVEMENT UPDATE
    for b in bullets:
        b.update()
    
    target = 0
    for a in obj:
        if CharCollidesWithBox(charx, chary, a.verts, a.movement, a.pos):
            health -= 0.01
        ammo = 0
        for c in bullets:
            if BoxCollidesWithBox(c.verts,a.verts, c.movement,a.movement, c.pos,a.pos):
                if obj[target].health == 50:
                    score += 100
                obj[target].health -= 50 #DAMAGE
                if -82 < bullets[ammo].movement < 82:
                    hitAmmo = bullets[ammo].movement
                bullets.pop(ammo)
                break
                break
            ammo += 1
        target += 1

    if hitAmmo < 0:
        hitAmmo -= 6
    elif hitAmmo > 0:
        hitAmmo += 6
    if hitAmmo >= 82 or hitAmmo <= -82:
        hitAmmo = 0
        bulletLimiter = True
                
    #JUMP MOVEMENT/ LAND ON PLATFORMS
    if jump:
        if up:
            chary += 10 #JUMPING SPEED
            jumpY += 10

        if jumpY >= 120: #MAX JUMP HEIGHT
            up = False
        
        if not up:
            for b in range(0, len(levelArray)):
                if b <= 16:
                    minX = levelArray[b]+x
                    levelY = levelArray[b+1]
                    maxX = levelArray[b+2]+x
                if b <= 16 and (charx+400+128-30) > minX and (charx+400+30) < maxX and chary+40 >= levelY and chary+40 <= (levelY + 14):
                    jump = False
                    chary = levelY-40
                    jumpY = 0
                    onLevel = True
                    currentLevel = [b,b+2]
                if jump: b += 3
            chary -= 10
            jumpY -= 10
            
        if chary <= 0:
            jump = False
            chary = 0
            jumpY = 0
            onLevel = False

    #CLOUD MOVEMENT
    if cloudx > -1024:
        cloudx -= 1
    if cloudx <= -1024:
        cloudx = 0
    
    #KEYBOARD INPUT HANDLER
    if keyboard[pyglet.window.key.ENTER]: #SHOOT
        if charOrientation == True and bulletLimiter == True: #SHOOT RIGHT
            shootSound.play()
            newBullet = bulletSprite([charx+400+128,chary+100], True)
            bullets += [newBullet]
        if charOrientation == False and bulletLimiter == True: #SHOOT LEFT
            shootSound.play()
            newBullet = bulletSprite([charx+400,chary+100], False)
            bullets += [newBullet]
        bulletLimiter = False #Stop the ability to infinitly shoot
        
    if keyboard[pyglet.window.key.RIGHT]: #MOVE RIGHT
        charOrientation = True
        
        if charx == 0 and x > -224: #Move Map
            x -= 4
        if charx < 400-128+30 and x < -223: #Go Right when on Right side of Map
            charx += 4     
        if charx < 0 and x == 0: #Go Right when on Left side of Map
            charx += 4
        if onLevel and not jump: #Go right when not on the base level
            currentLevelMax = currentLevel[1]
            if charx+400+30 > levelArray[currentLevelMax]+x:
                jump = True
                up = False
                chary -= 0.1
                
    if keyboard[pyglet.window.key.LEFT]: #MOVE LEFT
        charOrientation = False
        if charx == 0 and x < 0: #Move Map
            x += 4
        if charx > -413 and x == 0: #Go Left when on Right side of Map
            charx -= 4
        if charx > 0 and x < -223: #Go Left when on Right side of Map
            charx -= 4
        if onLevel and not jump: #Go left when not on the base level
            currentLevelMin = currentLevel[0]
            if charx+400+128-30 < levelArray[currentLevelMin]+x:
                jump = True
                up = False
                chary -= 0.1
                
    if keyboard[pyglet.window.key.DOWN] and keyboard[pyglet.window.key.SPACE]: #JUMP DOWN
        if chary > 0 and not jump:
            jump = True
            up = False
            jumpSound.play()
            chary -= 0.1

    if keyboard[pyglet.window.key.SPACE]: 
       if not jump and not keyboard[pyglet.window.key.DOWN]: #JUMP
            jump = True
            up = True
            jumpSound.play()
            
    if health <= 0:
        health = 100
        obj = []
        monst1a = monsterSprite(128,128,[random.randint(100,1000),100],monTex, 100, 0,1028)
        monst2b = monsterSprite(128,128,[random.randint(490,879),100+265],monTex, 100, 490,879)
        monst3c = monsterSprite(128,128,[random.randint(0,255),100+265],monTex, 100, 0,255)
        obj = [monst1a,monst2b,monst3c]

pyglet.clock.schedule_interval(update,1/60.0)
pyglet.app.run()
