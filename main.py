import pygame as pg
import os
import sys
import pickle
import random
import math

from game_methods import Vector2, make_text_object, int_to_str, get_angle

TOPSCORE = 0

def save_load(msg):
    global TOPSCORE
    if msg == 'load':
        try:
            file = open('saves.pkl', 'rb')
            load = pickle.load(file)
            TOPSCORE = load['topscore']
            file.close()
        except FileNotFoundError:
            file = open('saves.pkl', 'wb')
            save = {'topscore':TOPSCORE, }
            pickle.dump(save, file)
            file.close()
    else:
        file = open('saves.pkl', 'wb')
        save = {'topscore':TOPSCORE, }
        pickle.dump(save, file)
        file.close()

save_load('load')

class SplashScreen(object):
    def __init__(self):
        self.image = pg.image.load('banner.png').convert()
        self.rect = self.image.get_rect()
    
    def update(self, buttons):
        if 1 in buttons.values():
            return 'finished'
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)


class InstructionScreen(object):
    def __init__(self):
        self.image = pg.image.load('instructions.png').convert_alpha()
        self.rect = self.image.get_rect()
    
    def update(self, buttons):
        if 1 in buttons.values():
            return 'finished'
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Game(object):
    def __init__(self, width=800, height=600):
        global LEVEL
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pg.init()
        pg.mouse.set_visible(False)
        self.width = width
        self.height = height
        self.window = pg.display.set_mode((self.width, self.height))
        pg.display.set_caption('Finger Snapper')
        pg.display.set_icon(pg.image.load('icon.ico'))
        self.screen = pg.surface.Surface((self.width, self.height)).convert()
        self.rect = self.screen.get_rect()
        self.pos = (0, 0)
        self.running = True

        self.timer = pg.time.Clock()
        self.fps = 60
        self.events = [pg.KEYDOWN, pg.KEYUP, pg.QUIT]
        self.buttons = {pg.K_UP:0, pg.K_DOWN:0, pg.K_LEFT:0,
                        pg.K_RIGHT:0, pg.K_LALT:0, pg.K_F4:0}
        self.restarts = 0
        self.active = []
        LEVEL = Levels()
        self.engine = Engine(Player())
        self.instructions = InstructionScreen()
        self.splashscreen = SplashScreen()

    def reset(self):
        del self.engine
        self.engine = Engine(Player())
        self.active[0] = self.engine
        LEVEL.create()
        if self.restarts == 1:
            del self.engine
            self.engine = Engine(Player())
            self.active[0] = self.engine
            LEVEL.create()
        
    def run(self):
        msg = None
        self.active.append(self.engine)
        self.active.append(self.instructions)
        self.active.append(self.splashscreen)
        while self.running:
            if msg == 'dead':
                #Blit Game Over Window
                SE.loop('bgm')
                pg.time.wait(1000)
                self.restarts += 1
                self.reset()
            elif msg == 'finished':
                self.active.pop(-1)
                pg.time.wait(1000)
                
                
            for event in pg.event.get(self.events):
                if event.type == pg.QUIT or (
                    self.buttons[pg.K_LALT] and self.buttons[pg.K_F4]):
                    self.quit()
                elif event.type == pg.KEYDOWN:
                    if event.key in self.buttons.keys():
                        self.buttons[event.key] = 1
                        SE.loop('press')
                elif event.type == pg.KEYUP:
                    if event.key in self.buttons.keys():
                        self.buttons[event.key] = 0

            self.timer.tick_busy_loop(self.fps)
            msg = self.active[-1].update(self.buttons)
##            print(msg)

            #Render
            for item in self.active:
                item.draw(self.screen)
            self.window.blit(self.screen, self.rect)
            pg.display.flip()
        self.quit()
        
    def quit(self):
        save_load('save')
        pg.quit()
        sys.exit()

class Engine(object):
    def __init__(self, player, width=800, height=600):
        self.player = player
        self.shooters = pg.sprite.Group()
        self.collidable = pg.sprite.Group()
        self.collectible = pg.sprite.Group()
        self.screen = pg.surface.Surface((width, height)).convert()
        self.message = 'continue'
        self.bg = pg.surface.Surface((width, height*2)).convert()
        self.bg_rect = self.bg.get_rect()
        self.bg_rect.topleft = (0, -480)
        self.flag = pg.surface.Surface((630, 64)).convert()
        self.flag_rect = self.flag.get_rect()
        self.flag_rect.topleft = (85, -3000)
        self.last_flag = pg.surface.Surface((630, 64)).convert()
        self.last_flag_rect = self.last_flag.get_rect()
        self.last_flag_rect.topleft = (85, -3000)
        self.font = pg.font.SysFont('Times', 24, True)
        self._make_bg()
        self._make_flag()

        self.level = -1
        self.score = 0
        self.add_level()
        self.overlay = pg.surface.Surface((600, 200)).convert_alpha()
        self.ov_rect = self.overlay.get_rect()
        self.ov_rect.topleft = (100, 0)
        self._make_overlay()

    def _make_overlay(self):
        self.overlay.fill((0, 0, 0, 0))
        st, sr = make_text_object('Score: ' + int_to_str(self.score),
                                  self.font, (50, 50, 50))
        tt, tr = make_text_object('Top Score: ' + int_to_str(TOPSCORE),
                                  self.font, (50, 50, 50))
        lt, lr = make_text_object('Level: ' + int_to_str(self.level),
                                  self.font, (50, 50, 50))
        sr.topleft = (20, 10)
        tr.topleft = (20, 40)
        lr.topleft = (500, 10)
        self.overlay.blit(st, sr)
        self.overlay.blit(tt, tr)
        self.overlay.blit(lt, lr)

    def _make_bg(self):
        self.bg.fill((220, 220, 220))
        rects = []
        lrects = []
        long = 0
        for y in range(0, 1201, 120):
            for x in (0, 700):
                if long:
                    if x == 700:
                        rects.append((x+20, y, 80, 120))
                        lrects.append((x+22, y+2, 76, 116))
                    else:
                        rects.append((x, y, 80, 120))
                        lrects.append((x+2, y+2, 76, 116))
                else:
                    if x == 700:
                        rects.append((x+40, y, 60, 120))
                        lrects.append((x+42, y+2, 56, 116))
                    else:
                        rects.append((x, y, 60, 120))
                        lrects.append((x+2, y+2, 56, 116))
            long = not long
        for rect in rects:
            pg.draw.rect(self.bg, (100, 100, 100), rect)
        for rect in lrects:
            pg.draw.rect(self.bg, (0, 0, 0), rect)
        for x in (83, 715):
            pg.draw.line(self.bg, (255, 255, 255), (x, 0), (x, 1200), 2)

    def _make_flag(self):
        up = 1
        self.flag.fill((50, 50, 50))
        self.last_flag.fill((50, 50, 50))
        for x in range(0, 630, 45):
            if up:
                pg.draw.rect(self.flag, (255, 255, 255), (x, 0, 45, 32))
                pg.draw.rect(self.last_flag, (255, 255, 0), (x, 0, 45, 32))
            else:
                pg.draw.rect(self.flag, (255, 255, 255), (x, 32, 45, 32))
                pg.draw.rect(self.last_flag, (255, 255, 0), (x, 32, 45, 32))
            up = not up

    def add_level(self):
        self.level += 1
        sh, bo, col = LEVEL.get(self.level)
        for i in sh:
            self.shooters.add(i)
        for i in bo:
            self.shooter.add(i)
        for i in col:
            self.collectible.add(i)
        self.collidable.add(Persistent((100, 100), 5, -17))
        if self.level == 4:
            self.flag = self.last_flag

    def update_static(self):
        bx, by = self.bg_rect.topleft
        by += 2
        if by == 0:
            by = -480
        self.bg_rect.topleft = (bx, by)
        fx, fy = self.flag_rect.topleft
        fy += 2
        if fy > 700:
            fy = -2400
            self.score += 10000
            self.add_level()
            self._make_overlay()
        self.flag_rect.topleft = (fx, fy)

    def update(self, buttons):
        SE.play('bgm')
        self.update_static()
        for sprite in self.collidable:
            sprite.update()
        for sprite in self.collectible:
            sprite.update()
        for shooter in self.shooters:
            self.collidable.add(shooter.update())
        self.player.update(buttons)
        
        #Collision detection
        #Enemy
        collided = pg.sprite.spritecollide(self.player, self.collidable, False)
        if collided:
            for col in collided:
                if pg.sprite.collide_mask(self.player, col):
                    global TOPSCORE
                    self.message = 'dead'
                    TOPSCORE = max(TOPSCORE, self.score)
        #Moving Shooter (Exploding Bullets)
        shoot = pg.sprite.spritecollide(self.player, self.shooters, False)
        for col in shoot:
            if pg.sprite.collide_mask(self.player, col):
                self.message = 'dead'
        #Collectible
        collect = pg.sprite.spritecollide(self.player, self.collectible, False)
        for col in collect:
            if pg.sprite.collide_mask(self.player, col):
                self.score += col.points
                SE.loop('coin')
                col.kill()
                self._make_overlay()
            
        #Render to self.screen
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.bg, self.bg_rect)
        self.screen.blit(self.flag, self.flag_rect)
        self.player.draw(self.screen)
        for sprite in self.shooters:
            sprite.draw(self.screen)
        for sprite in self.collidable:
            sprite.draw(self.screen)
        for sprite in self.collectible:
            sprite.draw(self.screen)
        self.screen.blit(self.overlay, self.ov_rect)
        return self.message

    def draw(self, screen):
        screen.blit(self.screen, (0, 0))


class Player(pg.sprite.Sprite):
    def __init__(self, width=32, height=32):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.surface.Surface((width, height)).convert_alpha()
        self.rect = self.image.get_rect()
        self.color = (0, 0, 200)
        self.pos = Vector2(400, 500)
        self.speed = 3
        self._set_sprite()

    def _set_sprite(self):
        self.image.fill((0, 0, 0, 0))
        pos = Vector2(self.rect.center)
        for add in [(0, 5), (0, -5), (5, 0), (-5, 0)]:
            pg.draw.circle(self.image, self.color,
                           tuple(map(int, pos + add)), 10)
        pg.draw.circle(self.image, (0, 0, 255), self.rect.center, 10)
        pg.draw.circle(self.image, (100, 100, 255), self.rect.center, 5)

    def update(self, buttons):
        target = Vector2(0, 0)
        if buttons[pg.K_UP]:
            target += (0, -self.speed)
        elif buttons[pg.K_DOWN]:
            target += (0, self.speed)
        if buttons[pg.K_LEFT]:
            target += (-self.speed, 0)
        elif buttons[pg.K_RIGHT]:
            target += (self.speed, 0)

        #Move the player
        time_passed = pg.time.get_ticks()/1000
        distance = target.get_length()
        heading = target.get_normalized()
        travel = min(distance, time_passed*self.speed)
        self.pos += heading * travel
        #Player pos is limited to x:100 to 700, y:550 to 100
        x, y = self.pos
        x = max(100, min(700, x))
        y = max(50, min(580, y))
        self.pos = Vector2(x, y)
        self.rect.center = self.pos
            

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Collidable(pg.sprite.Sprite):
    def __init__(self, pos, speed, angle, width=64, height=64):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.surface.Surface((width, height)).convert_alpha()
        self.rect = self.image.get_rect()
        self.pos = Vector2(pos)
        self.rect.center = self.pos
        self.angle = angle
        self.speed = speed
        self.add_x, self.add_y = 0, 0
        self.create()

    def create(self):
        self.add_x = self.speed*math.cos(self.angle*math.pi/180)
        self.add_y = -self.speed*math.sin(self.angle*math.pi/180)
        self.image.fill((0, 0, 0, 0))
        color = (random.randint(80, 180),
                 random.randint(80, 180),
                 random.randint(80, 180))
        w, h = self.rect.width//2, self.rect.height//2
        pg.draw.circle(self.image, color, (w, h), w)

    def update(self):
        self.move()
        if self.pos[1] > 700:
            self.kill()
            
    def move(self):
        nx, ny = self.pos + (self.add_x, self.add_y)
        if nx <= 85:
            nx = 170 - nx
            self.add_x = -self.add_x
        elif nx >= 715:
            nx = 1430 - nx
            self.add_x = -self.add_x
        self.pos = Vector2(nx, ny)
        self.rect.center = self.pos

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Dissolvable(Collidable):
    def __init__(self, pos, speed, angle, width=10, height=10):
        Collidable.__init__(self, pos, speed, angle, width, height)

    def update(self):
        self.move()
        if (self.pos[1] > 700 or self.pos[1] < -100) or (
            self.pos[0] < 100 or self.pos[0] > 700):
            self.kill()

class Shooter(pg.sprite.Sprite):
    def __init__(self, pos, angle, count, delay, interval=20):
        pg.sprite.Sprite.__init__(self)
        self.pos = Vector2(pos)
        self.angle = angle
        self.count = count
        self.timing = -delay
        self.interval = interval
        self.rect = pg.rect.Rect(-1000, -1000, 1, 1)

    def update(self):
        if self.count > 1:
            if self.timing > self.interval:
                self.pos += (0, -2)
                self.count -= 1
                self.timing = 0
                return Collidable(self.pos, 5, self.angle, 10, 10)
        else:
            if self.timing > self.interval:
                self.pos += (0, -2)
                self.kill()
                return Collidable(self.pos, 5, self.angle, 10, 10)
        self.timing += 1
        return []

    def draw(self, screen):
        pass

class FragShooter(pg.sprite.Sprite):
    def __init__(self, pos, speed, target, delay, interval):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.surface.Surface((40, 40)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.pos = Vector2(pos)
        self.speed = speed
        self.target = target
        self.timing = -delay
        self.interval = interval
        self.angle = get_angle(self.pos, self.target)
        self.add_x = self.speed*math.cos(self.angle*math.pi/180)
        self.add_y = self.speed*math.sin(self.angle*math.pi/180)
        self.image.fill((0, 0, 0, 0))
        color = (random.randint(60, 120),
                 random.randint(60, 120),
                 random.randint(60, 120))
        w, h = self.rect.width//2, self.rect.height//2
        pg.draw.circle(self.image, color, (w, h), w)

    def update(self):
        #After delay, move
        if self.timing < 0:
            self.timing += 1
        elif self.timing != self.interval: #After interval, explode
            self.timing += 1
            self.pos += (self.add_x, self.add_y)
            self.rect.center = self.pos
        else:
            SE.play('boom')
            self.kill()
            return [Dissolvable(
                self.pos, 5, x, 10, 10) for x in range(0, 360, 30)]
        return []

    def draw(self, screen):
        screen.blit(self.image, self.rect)
            


class Collectible(Collidable):
    def __init__(self, pos, width=20, height=20):
        Collidable.__init__(self, pos, 0, 0, width, height)
        self.image.fill((0, 0, 0, 0))
        pg.draw.rect(self.image, (255, 255, 0), (5, 5, 10, 10))
        self.image = pg.transform.rotate(self.image, 45)
        self.image = pg.transform.scale(self.image, (30, 48))
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.points = 500

    def move(self):
        self.pos += (0, 2)
        self.rect.center = self.pos

class Persistent(Collidable):
    def __init__(self, pos, speed, angle, width=20, height=20, bounces=250):
        Collidable.__init__(self, pos, speed, angle, width, height)
        self.bounces = bounces

    def update(self):
        nx, ny = self.pos + (self.add_x, self.add_y)
        if nx <= 85:
            nx = 170 - nx
            self.add_x = -self.add_x
            self.bounces -= 1
        elif nx >= 715:
            nx = 1430 - nx
            self.add_x = -self.add_x
            self.bounces -= 1
        if ny <= 50:
            ny = 100 - ny
            self.add_y = -self.add_y
            self.bounces -= 1
        elif ny >= 580:
            ny = 1160 - ny
            self.add_y = -self.add_y
            self.bounces -= 1
        if self.bounces <= 0:
            self.kill()
        self.pos = Vector2(nx, ny)
        self.rect.center = self.pos


class Levels(object):
    def __init__(self):
        self.curr = 0
        self.producers = {}
        self.boss = {}
        self.collectibles = {}
        self.create()

    def create(self):
        #Levels0
        self.producers[0] = [
            Shooter((200, -100), -15, 12, 400),
            Shooter((200, -100), -160, 13, 415),
            Shooter((200, -100), -15, 12, 800),
            Shooter((200, -100), -160, 13, 815)
            ]
        self.collectibles[0] = [Collectible(pos) for pos in [
            (650, y) for y in range(-1800, -1000, 100)] +
            [(150, y) for y in range(-2600, -1800, 100)]
                                ]
        #Level 1
        self.producers[1] = [
            Shooter((400, -100), -10, 29, 0),
            Shooter((400, -100), -170, 29, 10),
            Shooter((350, -100), -90, 4, 600, 60),
            Shooter((400, -100), -90, 4, 610, 60),
            Shooter((450, -100), -90, 4, 620, 60)
            ]
        self.collectibles[1] = [Collectible(pos) for pos in [
            (650, -100), (650, -200), (650, -300), (400, -400)] +
            [(150, y) for y in range(-1800, -400, 100)] +
            [(350, y) for y in range(-2000, -700, 100)]
                                ]
        
        #Level 2
        self.producers[2] = [
            Shooter((400, -100), -11, 15, 10),
            Shooter((400, -100), -17, 15, 10),
            Shooter((350, -100), -95, 16, 600, 50),
            Shooter((450, -100), -85, 16, 620, 50),
            Shooter((350, -100), -100, 16, 600, 50),
            Shooter((450, -100), -80, 16, 620, 50),
            FragShooter((200, -100), 5, (500, 300), 630, 100),
            FragShooter((600, -100), 5, (300, 300), 630, 100),
            FragShooter((200, -100), 5, (500, 300), 780, 100),
            FragShooter((600, -100), 5, (300, 300), 780, 100),
            FragShooter((200, -100), 5, (500, 300), 930, 100),
            FragShooter((600, -100), 5, (300, 300), 930, 100),
            FragShooter((200, -100), 5, (500, 300), 1080, 100),
            FragShooter((600, -100), 5, (300, 300), 1080, 100),
            FragShooter((200, -100), 5, (500, 300), 1230, 100),
            FragShooter((600, -100), 5, (300, 300), 1230, 100),
            FragShooter((200, -100), 5, (500, 300), 1380, 100),
            FragShooter((600, -100), 5, (300, 300), 1380, 100),
            ]
        self.collectibles[2] = [
            Collectible(pos) for pos in [
            (350, y) for y in range(-1800, -400, 175)] +
            [(400, y) for y in range(-1830, -430, 175)] +
            [(450, y) for y in range(-1860, -460, 175)] +
            [(150, y) for y in range(-2200, -400, 300)] +
            [(650, y) for y in range(-2200, -400, 300)]
                                ]

        #Level 3
        self.producers[3] = [
            Shooter((100, -100), -10, 16, 10, 50),
            Shooter((120, -100), -15, 16, 10, 50),
            Shooter((140, -100), -20, 16, 10, 50),
            Shooter((160, -100), -25, 16, 10, 50),
            Shooter((700, -100), -170, 16, 10, 50),
            Shooter((720, -100), -165, 16, 10, 50),
            Shooter((740, -100), -160, 16, 10, 50),
            Shooter((760, -100), -155, 16, 10, 50),
            FragShooter((200, -100), 5, (500, 300), 630, 100),
            FragShooter((600, -100), 5, (300, 300), 630, 100),
            FragShooter((200, -100), 5, (500, 300), 780, 100),
            FragShooter((600, -100), 5, (300, 300), 780, 100),
            FragShooter((200, -100), 5, (500, 300), 930, 100),
            FragShooter((600, -100), 5, (300, 300), 930, 100),
            FragShooter((200, -100), 5, (500, 300), 1080, 100),
            FragShooter((600, -100), 5, (300, 300), 1080, 100),
            FragShooter((200, -100), 5, (500, 300), 1230, 100),
            FragShooter((600, -100), 5, (300, 300), 1230, 100),
            FragShooter((200, -100), 5, (500, 300), 1380, 100),
            FragShooter((600, -100), 5, (300, 300), 1380, 100),
            ]
        self.collectibles[3] = [Collectible(pos) for pos in [
            (120, y) for y in range(-2200, -600, 100)] +
            [(680, y) for y in range(-2200, -600, 100)] +
            [(400, y) for y in range(-2200, -800, 100)]
                                ]

        #Level 4
        self.producers[4] = [
            Shooter((260, -400), -70, 10, 10, 150),
            Shooter((300, -400), -75, 10, 10, 150),
            Shooter((340, -400), -80, 10, 10, 150),
            Shooter((380, -400), -85, 10, 10, 150),
            Shooter((400, -400), -90, 10, 10, 150),
            Shooter((420, -400), -95, 10, 10, 150),
            Shooter((460, -400), -100, 10, 10, 150),
            Shooter((500, -400), -105, 10, 10, 150),
            Shooter((540, -400), -110, 10, 10, 150),
            FragShooter((400, -100), 5, (600, 500), 630, 120),
            FragShooter((400, -100), 5, (200, 500), 630, 120),
            FragShooter((400, -100), 5, (600, 100), 690, 60),
            FragShooter((400, -100), 5, (200, 100), 690, 60),
            FragShooter((400, -100), 5, (600, 500), 940, 120),
            FragShooter((400, -100), 5, (200, 500), 940, 120),
            FragShooter((400, -100), 5, (600, 100), 1000, 60),
            FragShooter((400, -100), 5, (200, 100), 1000, 60),
            FragShooter((400, -100), 5, (600, 500), 1200, 120),
            FragShooter((400, -100), 5, (200, 500), 1200, 120),
            FragShooter((400, -100), 5, (600, 100), 1260, 60),
            FragShooter((400, -100), 5, (200, 100), 1260, 60),
            ]
        self.collectibles[4] = [Collectible(pos) for pos in [
            (120, y) for y in range(-2200, -600, 100)] +
            [(350, y) for y in range(-2200, -800, 100)] +
            [(400, y) for y in range(-2200, -800, 100)] +
            [(450, y) for y in range(-2200, -800, 100)] +
            [(680, y) for y in range(-2200, -600, 100)]
                                ]
                                
    def get(self, level):
##        level = 5
        if level > 4:
            return [
                FragShooter((400, -100), 5, (600, 500), 630, 120),
                FragShooter((400, -100), 5, (200, 500), 630, 120),
                FragShooter((400, -100), 5, (600, 100), 690, 60),
                FragShooter((400, -100), 5, (200, 100), 690, 60),
                FragShooter((400, -100), 5, (600, 500), 940, 120),
                FragShooter((400, -100), 5, (200, 500), 940, 120),
                FragShooter((400, -100), 5, (600, 100), 1000, 60),
                FragShooter((400, -100), 5, (200, 100), 1000, 60),
                FragShooter((400, -100), 5, (600, 500), 1200, 120),
                FragShooter((400, -100), 5, (200, 500), 1200, 120),
                FragShooter((400, -100), 5, (600, 100), 1260, 60),
                FragShooter((400, -100), 5, (200, 100), 1260, 60),
                ], [], [Collectible(pos) for pos in [
                    (120, y) for y in range(-2200, -600, 100)] +
                    [(350, y) for y in range(-2200, -800, 100)] +
                    [(400, y) for y in range(-2200, -800, 100)] +
                    [(450, y) for y in range(-2200, -800, 100)] +
                    [(680, y) for y in range(-2200, -600, 100)]]
        try:
            return (self.producers[level],
                    self.boss[level],
                    self.collectibles[level])
        except KeyError:
            return (self.producers[level],
                    [],
                    self.collectibles[level])
        

class Sound(object):
    def __init__(self):
        self.music_lib = {}

    def load_music(self, name, title):
        self.music_lib[name] = pg.mixer.Sound(title)
        self.music_lib[name].play()
        self.music_lib[name].stop()
        if name == 'press':
            self.music_lib[name].set_volume(.1)
        elif name != 'bgm':
            self.music_lib[name].set_volume(.5)

    def play(self, name):
        if self.music_lib[name].get_num_channels() == 0:
            self.music_lib[name].play()
        elif name != 'bgm':
            self.music_lib[name].play()

    def stop(self, name):
        if self.music_lib[name].get_num_channels() != 0:
            self.music_lib[name].stop()

    def loop(self, name):
        if self.music_lib[name].get_num_channels() != 0:
            self.music_lib[name].stop()
            if name == 'bgm':
                self.music_lib[name].play(10)
            else:
                self.music_lib[name].play()
            
        else:
            self.music_lib[name].play()

LEVEL = None
SE = None

if __name__ == "__main__":
    while True:
        game = Game()
        SE = Sound()
        SE.load_music('bgm', 'Audio/instrumental.wav')
        SE.load_music('coin', 'Audio/coin2.wav')
        SE.load_music('boom', 'Audio/explosion.wav')
        SE.load_music('press', 'Audio/button.wav')
        game.run()
