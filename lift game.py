import pygame,math,random,os,time
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

def personmaker(size,target):
    w = 20
    h = size+10
    col = [random.randint(50,255),random.randint(50,255),random.randint(50,255)]
    surf = pygame.Surface((w,h))#,pygame.SRCALPHA)
    surf.set_colorkey((0,0,0))
    pygame.draw.rect(surf,col,pygame.Rect(3,3,14,h-10),0,4)
    pyui.draw.roundedline(surf,col,(6,h-2),(6,h-12),2)
    pyui.draw.roundedline(surf,col,(13,h-2),(13,h-12),2)
    ui.write(surf,10,size/2,str(target),15,(255,255,255))
    return surf

class Person:
    def __init__(self,floor,target,lifts):
        self.floor = floor
        self.targetfloor = target
        self.lifts = lifts
        self.lift = -1
        
        self.movetarget = -100
        self.targetlift = -1
        self.x = -100
        self.floorwidth = (self.lifts[-1].x+self.lifts[-1].width)
        
        self.size = random.randint(10,40)
        self.speed = max(random.gauss(self.size/40,0.3),0.1)
        self.image = personmaker(self.size,self.targetfloor)

        self.delay = 0
        self.completed = False
        self.available = []
        
    def move(self,tickmul):
        self.checklifts()
        if self.x == self.movetarget:
            if self.completed:
                return True
            if self.targetlift in self.available:
                self.lifts[self.targetlift].attemptload(tickmul,self)
                if self in self.lifts[self.targetlift].people:
                    self.lift = self.targetlift
                    self.targetlift = -1
            else:
                self.delay-=tickmul
                if self.delay<0:
                    self.movetarget = random.randint(0,self.floorwidth)
                    self.delay = random.gauss(300,120)

        if self.x<self.movetarget:
            self.x+=self.speed
            if self.x>self.movetarget: self.x = self.movetarget
        if self.x>self.movetarget:
            self.x-=self.speed
            if self.x<self.movetarget: self.x = self.movetarget
        return False
    def checklifts(self):
        if self.lift == -1 and not self.completed:
            self.available = []
            for i,a in enumerate(self.lifts):
                if a.floor == self.floor and a.open == 0 and a.capacity>sum([a.size for a in a.people])+self.size:
                    self.available.append(i)
            if self.available!=[]:
                if not(self.targetlift in self.available):
                    self.targetlift = self.available[0]
                    self.movetarget = self.lifts[self.targetlift].x+random.randint(0,self.lifts[self.targetlift].width-self.image.get_width())
                    
    def unload(self,lift):
        self.x = lift.x
        self.lift = -1
        self.movetarget = self.floorwidth+100
        self.floor = lift.floor
        self.completed = True
        
    def draw(self,offset):
        if self.lift == -1:
            rec = self.lifts[0].rects[self.floor]
            screen.blit(self.image,(self.x-offset[0],rec.y+rec.height-self.image.get_height()))

class Lift:
    def __init__(self,x,width,speed,doorspeed,loadspeed,floors):
        self.x = x
        self.width = width
        self.height = self.width*1.75
        self.speed = speed
        self.doorspeed = doorspeed
        self.loadspeed = loadspeed
        self.floors = floors
        self.capacity = 100

        self.ldoor = pygame.transform.scale(image.doorleft,(self.width/2,self.height))
        self.rdoor = pygame.transform.scale(image.doorright,(self.width/2,self.height))

        self.open = 1
        self.floor = 0
        self.targetfloor = 0
        self.movestage = -1
        self.delay = 0
        self.people = []
    def getclicked(self,mpos,mprs,offset):
        self.rects = [pygame.Rect(self.x-offset[0],-a*(self.height+30)-offset[1],self.width,self.height) for a in range(self.floors)]
        for i,a in enumerate(self.rects):
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
    def idle(self,tickmul):
        if self.open == 0:
            if self.people!=[]:
                off = -1
                for i,a in enumerate(self.people):
                    if a.targetfloor == self.floor:
                        off = i
                if off!=-1:
                    self.delay-=tickmul
                    if self.delay<0:
                        self.people[off].unload(self)
                        self.people.remove(self.people[off])
                        self.delay = self.loadspeed
    def attemptload(self,tickmul,person):
        self.delay-=tickmul
        if self.delay<0:
            if self.capacity>sum([a.size for a in self.people])+person.size:
                self.delay = self.loadspeed
                self.people.append(person)
        
    def draw(self,offset):
        for a in range(self.floors):
            door = self.drawdoors(a==self.floor)
            screen.blit(door,(self.x-offset[0],-a*(self.height+30)-offset[1]))
        pyui.draw.circle(screen,(250,50,100),(self.x-offset[0]-10,-self.floor*(self.height+30)-offset[1]+self.height/2),5)
    def drawdoors(self,shut=True):
        surf = pygame.Surface((self.width,self.height))
        surf.fill((100,100,100))
        d = 0
        if shut:
            d = 1-self.open
            x = 2
            for a in self.people:
                surf.blit(a.image,(x%self.width,self.height-a.image.get_height()))
                x+=(a.image.get_width()+2)
            
        surf.blit(self.ldoor,(-self.width/2*d,0))
        surf.blit(self.rdoor,(self.width/2+self.width/2*d,0))
        return surf
        
class Building:
    def __init__(self):
        self.floornum = 3
        self.liftnum = 2
        self.offset = [-350,-400]
        self.lifts = [Lift(a*140,80,0.01,0.05,30,self.floornum) for a in range(self.liftnum)]
        self.people = []

        self.delay = 0
        self.prevframe = time.time()
    def tick(self):
        tickmul = 60*(time.time()-self.prevframe)
        self.prevframe = time.time()

        mprs = pygame.mouse.get_pressed()
        mpos = pygame.mouse.get_pos()
        rel = pygame.mouse.get_rel()
        if mprs[2]:
            self.offset[0]-=rel[0]
            self.offset[1]-=rel[1]

        for a in self.lifts:
            a.getclicked(mpos,mprs,self.offset)
            a.navigate(tickmul)
            a.idle(tickmul)
        remlist = []
        for a in self.people:
            if a.move(tickmul):
                remlist.append(a)
        for a in remlist:
            self.people.remove(a)

        self.delay-=tickmul
        if self.delay<0:
            self.delay = 300
            f = random.randint(0,self.floornum-1)
            choices = [a for a in range(self.floornum)]
            choices.remove(f)
            t = random.choice(choices)
            self.people.append(Person(f,t,self.lifts))
        
        
    def draw(self):
        for a in self.lifts:
            a.draw(self.offset)
        for a in self.people:
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
