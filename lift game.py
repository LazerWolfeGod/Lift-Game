import pygame,math,random,os
import PyUI as pyui
pygame.init()
screen = pygame.display.set_mode((1000, 600),pygame.RESIZABLE)
pygame.scrap.init()
ui = pyui.UI()
done = False
clock = pygame.time.Clock()
ui.movemenu('game')

class image:
    def load(name,colorkey=(255,255,255)):
        try:
            path = sys._MEIPASS
        except Exception:
            path = os.path.abspath(".")
        fullpath = os.path.join(path,name)
        return pygame.image.load(fullpath)
    doorleft = load('assets\\door.png')
    doorright = pygame.transform.flip(doorleft,True,False)

class Lift:
    def __init__(self,x,width,speed,doorspeed,floors):
        self.x = x
        self.width = width
        self.height = self.width*1.75
        self.speed = speed
        self.doorspeed = doorspeed
        self.floors = floors

        self.ldoor = pygame.transform.scale(image.doorleft,(self.width/2,self.height))
        self.rdoor = pygame.transform.scale(image.doorright,(self.width/2,self.height))

        self.open = 1
        self.floor = 0
        self.targetfloor = 0
        self.movestage = -1
    def getclicked(self,mpos,mprs,offset):
        rects = [pygame.Rect(self.x-offset[0],-a*(self.height+30)-offset[1],self.width,self.height) for a in range(self.floors)]
        for i,a in enumerate(rects):
            if a.collidepoint(mpos) and mprs[0]:
                self.targetfloor = i
    def navigate(self,tickmul):
        if self.targetfloor!=self.floor:
            if self.movestage == -1:
                self.movestage = 0
            elif self.movestage == 0:
                self.open+=self.doorspeed*tickmul
                if self.open>1:
                    self.open = 1
                    self.movestage = 1
            elif self.movestage == 1:
                if self.floor>self.targetfloor:
                    self.floor-=self.speed*tickmul
                    if self.floor<self.targetfloor:
                        self.floor = self.targetfloor
                        self.movestage = -1
                else:
                    self.floor+=self.speed*tickmul
                    if self.floor>self.targetfloor:
                        self.floor = self.targetfloor
                        self.movestage = -1
        else:
            self.open-=self.doorspeed*tickmul
            self.open = max(self.open,0)
                
    def draw(self,offset):
        for a in range(self.floors):
            door = self.drawdoors(a==self.floor)
            screen.blit(door,(self.x-offset[0],-a*(self.height+30)-offset[1]))
        pygame.draw.circle(screen,(250,50,100),(self.x-offset[0]-10,-self.floor*(self.height+30)-offset[1]+self.height/2),5)
    def drawdoors(self,shut=True):
        surf = pygame.Surface((self.width,self.height))
        surf.fill((100,100,100))
        d = 0
        if shut: d = 1-self.open
        surf.blit(self.ldoor,(-self.width/2*d,0))
        surf.blit(self.rdoor,(self.width/2+self.width/2*d,0))
        return surf
        
class Building:
    def __init__(self):
        self.floornum = 3
        self.liftnum = 2
        self.offset = [-350,-400]
        self.lifts = [Lift(a*140,80,0.01,0.05,self.floornum) for a in range(self.liftnum)]
    def tick(self):
        fps = clock.get_fps()
        if fps == 0: tickmul = 1
        else: tickmul = 60/clock.get_fps()

        mprs = pygame.mouse.get_pressed()
        mpos = pygame.mouse.get_pos()
        rel = pygame.mouse.get_rel()
        if mprs[2]:
            self.offset[0]-=rel[0]
            self.offset[1]-=rel[1]

        for a in self.lifts:
            a.getclicked(mpos,mprs,self.offset)
            a.navigate(tickmul)
        
    def draw(self):
        for a in self.lifts:
            a.draw(self.offset)

building = Building()

##ui.makerect(100,300,200,6,glow=10,glowcol=(50,20,160,30),col=(245,235,255),roundedcorners=2,menu='game')

while not done:
    pygameeventget = ui.loadtickdata()
    for event in pygameeventget:
        if event.type == pygame.QUIT:
            done = True
    screen.fill((255,255,255))
    building.tick()
    building.draw()
    ui.rendergui(screen)
    pygame.display.flip()
    clock.tick(60)                                               
pygame.quit() 
