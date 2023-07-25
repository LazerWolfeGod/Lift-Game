import pygame,math,random,os,time
import PyUI as pyui
pygame.init()
screen = pygame.display.set_mode((1000, 600),pygame.RESIZABLE)
pygame.scrap.init()
ui = pyui.UI()

class funcer:
    def __init__(self,level,main):
        self.func = lambda: main.gengame(level)

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
    if target == 0:
        target = 'G'
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
    def __init__(self,floor,target,lifts,level):
        self.floor = floor
        self.targetfloor = target
        self.level = level
        self.lifts = lifts
        self.lift = -1
        
        self.movetarget = -100
        self.targetlift = -1
        self.x = -100
        self.floorwidth = (self.lifts[-1].x+self.lifts[-1].width)
        
        self.size = random.randint(10,40)
        self.speed = max(random.gauss(self.size/20,0.3),0.5)
        self.image = personmaker(self.size,self.targetfloor)

        self.patience = max(random.gauss(1000,300),300)*self.level[1]/(self.speed**0.6)
        self.maxpatience = self.patience

        self.delay = 0
        self.completed = False
        self.angry = False
        self.available = []
        
    def move(self,tickmul,people):
        self.checklifts()
        self.passivedrain(tickmul,sum([a.angry for a in people]))
        if self.lift == -1:
            if self.x == self.movetarget:
                if self.completed or self.angry:
                    return True
                if self.targetlift in self.available:
                    self.lifts[self.targetlift].attemptload(tickmul,self)
                    if self in self.lifts[self.targetlift].people:
                        self.lift = self.targetlift
                        self.targetlift = -1
                else:
                    self.delay-=tickmul
                    if self.delay<0:
                        self.randompath()
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
            self.available.sort(key=lambda i:abs(self.lifts[i].x-self.x))
            if self.available!=[]:
                if self.targetlift != self.available[0]:
                    self.targetlift = self.available[0]
                    self.pathtolift(self.targetlift)
            elif self.targetlift != -1:
                self.targetlift = -1
                self.movetarget = self.x
                self.delay = random.gauss(300,120)
                self.patience-=40
    def randompath(self):
        if not(self.angry or self.completed):
            self.movetarget = random.randint(0,self.floorwidth)
    def pathtolift(self,lift):
        if not(self.angry or self.completed):
            self.movetarget = self.lifts[self.targetlift].x
            if self.x>self.lifts[self.targetlift].x:
                if self.x<self.lifts[self.targetlift].x+self.lifts[self.targetlift].width-self.image.get_width():
                    self.movetarget = self.x
                else:
                    self.movetarget+=self.lifts[self.targetlift].width-self.image.get_width()

    def passivedrain(self,tickmul,angry):
        mul = 1
        if self.completed: mul = 0.2
        elif self.lift != -1:
            mul = 0.5
            if self.lifts[self.lift].open == 0:
                mul = 2
        mul*=1+0.05*angry
        self.patience-=tickmul*mul
        if self.patience<0 and not self.angry:
            self.angry = True
            self.speed*=2
            if not self.completed:
                self.movetarget = -100
    
    def unload(self,lift):
        self.x = lift.x
        self.lift = -1
        self.floor = lift.floor
        self.completed = True
        if self.angry: self.movetarget = -100
        else: self.movetarget = self.floorwidth+100
        
        
    def draw(self,offset):
        if self.lift == -1:
            progress = min(max((self.patience/self.maxpatience),0),1)
            rec = self.lifts[0].rects[self.floor]
            screen.blit(self.image,(self.x-offset[0],rec.y+rec.height-self.image.get_height()))
            pygame.draw.rect(screen,(150,150,150),pygame.Rect(self.x-offset[0]-self.image.get_width()*0.2,rec.y+rec.height-self.image.get_height()-10,self.image.get_width()*1.4,7))
            pygame.draw.rect(screen,(100+150*(1-progress),250*progress,60),pygame.Rect(self.x-offset[0]-self.image.get_width()*0.2+1,rec.y+rec.height-self.image.get_height()-10+1,(self.image.get_width()*1.4-2)*progress,5))
class Lift:
    def __init__(self,x,width,speed,doorspeed,loadspeed,floors):
        self.x = x
        self.width = width
        self.height = self.width*1.75
        self.speed = speed
        self.doorspeed = doorspeed
        self.loadspeed = loadspeed
        self.floors = floors
        self.capacity = 400

        self.ldoor = pygame.transform.scale(image.doorleft,(self.width/2,self.height))
        self.rdoor = pygame.transform.scale(image.doorright,(self.width/2,self.height))

        self.open = 1
        self.floor = 0
        self.targetfloor = 0
        self.movestage = -1
        self.delay = 0
        self.people = []

        self.liftposes = [5,30,55,15,40,1,25,59,10,50,35,20,45]
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
                    if a.targetfloor == self.floor or a.angry:
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
                i = 0
                pos = self.liftposes[i]
                while pos in [a.liftpos for a in self.people]:
                    i+=1
                    if i == len(self.liftposes):
                        pos = random.randint(0,self.width-person.image.get_width())
                        break
                    pos = self.liftposes[i]
                person.liftpos = pos
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
                surf.blit(a.image,(a.liftpos,self.height-a.image.get_height()))
                x+=(a.image.get_width()+2)
            
        surf.blit(self.ldoor,(-self.width/2*d,0))
        surf.blit(self.rdoor,(self.width/2+self.width/2*d,0))
        return surf
        
class Building:
    def __init__(self,level,newgui=True):
        ## people, patience, arrival speed, lifts, floors, coin multiplier
        self.level = level
        self.floornum = self.level[4]
        self.liftnum = self.level[3]
        self.offset = [-350,-400]
        self.lifts = [Lift(a*140,80,0.01,0.05,30,self.floornum) for a in range(self.liftnum)]
        self.people = []
        self.peoplecount = 0
        self.score = 0
        self.coins = 0
        self.permacoins = 0
        ## angry, complete, score, coins, permacoins
        self.stats = [0,0,0,0,0]

        self.delay = 0
        self.prevframe = time.time()

        if newgui:
            self.makegui()
    def makegui(self):
        ui.maketext(0,0,str(self.score),40,'game','score display',anchor=('w-10',10),objanchor=('w',0),backingcol=(255,255,255))
        
    def tick(self,animation):
        tickmul = 60*(time.time()-self.prevframe)
        self.prevframe = time.time()

        mprs = pygame.mouse.get_pressed()
        mpos = pygame.mouse.get_pos()
        rel = pygame.mouse.get_rel()
        if mprs[2]:
            self.offset[0]-=rel[0]
            self.offset[1]-=rel[1]

        for a in self.lifts:
            tempoffset = [self.offset[0],self.offset[1]-animation]
            a.getclicked(mpos,mprs,tempoffset)
            a.navigate(tickmul)
            a.idle(tickmul)
        remlist = []
        for a in self.people:
            if a.move(tickmul,self.people):
                remlist.append(a)
        for a in remlist:
            self.addscore(a)
            self.people.remove(a)
            if self.level[0] <= 0 and len(self.people) == 0:
                self.stats[2] = self.score
                self.stats[3] = self.coins
                self.stats[4] = self.permacoins
                return True

        self.delay-=tickmul
        if self.delay<0:
            self.level[0]-=1
            if self.level[0] >= 0:
                self.peoplecount+=1
                random.seed(self.level[-1]+self.peoplecount)
                self.delay = self.level[2]
                f = random.randint(0,self.floornum-1)
                choices = [a for a in range(self.floornum)]
                choices.remove(f)
                t = random.choice(choices)
                self.people.append(Person(f,t,self.lifts,self.level))
        return False
        
    def draw(self,animation):
        tempoffset = [self.offset[0],self.offset[1]-animation]
        for a in self.lifts:
            a.draw(tempoffset)
        for a in self.people:
            a.draw(tempoffset)

    def addscore(self,person):
        base = 100
        new = base*(person.patience/person.maxpatience)
        if person.angry:
            self.stats[0]+=1
            new = base*-0.5
            if person.completed:
                new*=0.5
        self.score+=int(round(new))
        if person.completed:
            self.coins+=1
            if person.patience>person.maxpatience*0.4:
                self.permacoins+=1
        ui.IDs['score display'].text = str(self.score)
        ui.IDs['score display'].refresh(ui)
        ui.IDs['score display'].resetcords(ui)

class Main:
    def __init__(self):
        ## people, patience, arrival speed, lifts, floors, coin multiplier
        self.levels = [[3,10,300,1,2,1],
                       [10,2,250,2,2,1],
                       [20,1.8,180,2,3,1.4],
                       [50,1,10,2,3,1.4]]
        random.seed(0)
        for a in range(len(self.levels)):
            self.levels[a].append(random.randint(0,1000))
        
        self.makegui()
        self.building = 0
    def makegui(self):
        self.titleglow = 0
        trans = 7
        self.titleglowcols = pyui.genfade([(255,0,0,trans),(255,255,0,trans),(0,255,0,trans),(0,255,255,trans),(0,0,255,trans),(255,0,255,trans),(255,0,0,trans)],120)

        ## title screen
        ui.maketext(0,0,'Lift Game',100,backingcol=(255,255,255),anchor=('w/2','h/2-150'),objanchor=('w/2','h'),ID='main title',pregenerated=False,textoffsety=6)
        ui.makebutton(0,0,'Infinite',60,self.gengame,roundedcorners=6,verticalspacing=6,anchor=('w/2','h/2'),center=True)
        ui.makebutton(0,80,'Levels',60,lambda: ui.movemenu('levels','left'),roundedcorners=6,verticalspacing=6,anchor=('w/2','h/2'),center=True)
        ui.makebutton(0,160,'Upgrades',60,lambda: ui.movemenu('upgrades','left'),roundedcorners=6,verticalspacing=6,anchor=('w/2','h/2'),center=True)
        ui.makerect(0,0,1,1,menu='game',ID='animation tracker',enabled=False)

        ## levels
        ui.maketext(20,20,'Levels',50,'levels',backingcol=(255,255,255))

        data = []
        for a in range(len(self.levels)):
            func = funcer(a,self)
            data.append([f'Level {a+1}',ui.makebutton(0,0,'Play',30,func.func,roundedcorners=4,verticalspacing=4)])
        ui.maketable(20,70,data,menu='levels',roundedcorners=4,boxwidth=[300,100],textsize=30)

        ## complete menu
        ui.makewindowedmenu(0,0,400,300,'complete','game',anchor=('w/2','h/2'),center=True,roundedcorners=10)
    def gengame(self,level=-1):
        if level!=-1: self.level = self.levels[level][:]
        else: self.level = [10000000,1,180,2,3,1,time.time()]

        if self.building == 0:
            self.building = Building(self.level,True)
        else:
            self.building = Building(self.level,False)
        ui.movemenu('game','up')
    def main(self):
        done = False
        clock = pygame.time.Clock()
        while not done:
            pygameeventget = ui.loadtickdata()
            for event in pygameeventget:
                if event.type == pygame.QUIT:
                    done = True
            screen.fill((255,255,255))
            if ui.activemenu == 'game' or ui.activemenu == 'complete':
                if ui.activemenu == 'game':
                    if self.building.tick(ui.IDs['animation tracker'].y):
                        ui.movemenu('complete','down')
                        del ui.backchain[-1]
                self.building.draw(ui.IDs['animation tracker'].y)
            elif ui.activemenu == 'main':
                self.titleglow+=1
                ui.IDs['main title'].glow = int(math.sin(self.titleglow/120*math.pi)*12+45)
                ui.IDs['main title'].glowcol = self.titleglowcols[self.titleglow%len(self.titleglowcols)]
                ui.IDs['main title'].refreshglow(ui)
            ui.rendergui(screen)
            pygame.display.flip()
            clock.tick(60)
        pygame.quit() 

main = Main()
main.main()


##ui.makerect(100,300,200,6,glow=10,glowcol=(50,20,160,30),col=(245,235,255),roundedcorners=2,menu='game')


