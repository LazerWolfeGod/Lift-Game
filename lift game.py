import pygame,math,random,os,time
import PyUI as pyui
pygame.init()
screen = pygame.display.set_mode((1000, 600),pygame.RESIZABLE)
pygame.scrap.init()
ui = pyui.UI()

class funcer:
    def __init__(self,level,main):
        self.func = lambda: main.gengame(level)
class funcerk:
    def __init__(self,ID,main):
        self.func = lambda: main.killpopup(ID)
class funcerbuy:
    def __init__(self,item,cost,main):
        self.func = lambda: main.buy(item,cost)

class image:
    def load(name,colorkey=(255,255,255)):
        try:
            path = sys._MEIPASS
        except Exception:
            path = os.path.abspath(".")
        fullpath = os.path.join(path,name)
        img = pygame.image.load(fullpath)
        img.set_colorkey(colorkey)
        return img
    def seperate(surf,w,h):
        images = []
        for a in range(round(surf.get_width()/w)):
            images.append(pygame.Surface((w,h)))
            images[-1].blit(surf,(-a*w,0))
        return images
    
    doorleft = load('assets\\door.png')
    doorright = pygame.transform.flip(doorleft,True,False)

    coins = seperate(load('assets\\coins.png',(0,0,0)),67,66)
##    coinsgrey = seperate(load('assets\\coin grey.png'),67,66)
    raincloud = load('assets\\raincloud.png')

    ## coin: https://www.shutterstock.com/image-vector/set-rotating-coins-popular-currency-symbols-1572677185?consentChanged=true&irclickid=SwCW4w2KrxyPRh5Vylw%3A0xWXUkFwFdTwPwibyU0&irgwc=1&utm_campaign=Eezy%2C%20LLC&utm_content=1636534&utm_medium=Affiliate&utm_source=38919&utm_term=www.vecteezy.com
    ## raincloud: https://www.istockphoto.com/vector/dark-clouds-with-lightning-thunderstorm-icon-vector-illustration-gm1311259120-400409859

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
    def __init__(self,floor,target,lifts,upgrades,level):
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
        self.speed = max(random.gauss(self.size/20,0.3),0.5)*(0.2*upgrades['floor speed']+1)
        self.image = personmaker(self.size,self.targetfloor)

        self.patience = max(random.gauss(1000,300),300)*((self.level[1]+1)**0.5)*len(lifts)/(self.speed**0.6)
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
                    self.lifts[self.targetlift].attemptload(self)
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
                if a.floor == self.floor and a.open == 0 and a.capacity>=len(a.people)+1:
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
        if self.floor == self.targetfloor: self.completed = True
        if self.angry: self.movetarget = -100
        else: self.movetarget = self.floorwidth+100
        
    def draw(self,offset):
        if self.lift == -1:
            rec = self.lifts[0].rects[self.floor]
            self.y = rec.y+rec.height+offset[1]
            self.blitsurf(screen,self.x-offset[0],self.y-offset[1])
            if self.angry:
                screen.blit(image.raincloud,(self.x-offset[0]+self.image.get_width()*0.5-image.raincloud.get_width()*0.5,self.y-offset[1]-self.image.get_height()-15-image.raincloud.get_height()))
    def blitsurf(self,surf,x,y):
        progress = min(max((self.patience/self.maxpatience),0),1)
        surf.blit(self.image,(x,y-self.image.get_height()))
        pyui.draw.pichart(surf,(x+self.image.get_width()*0.5,y-self.image.get_height()-10),8,(150,150,150),math.pi*2*progress,0,(100+150*(1-progress),250*progress,60),1)

class Lift:
    def __init__(self,x,width,upgrades,floors):
        self.x = x
        self.width = width
        self.height = self.width*1.75
        
        self.speed = 1.001**upgrades['lift speed']-1+0.004
        self.doorspeed = 1.005**upgrades['door speed']-1+0.006
        self.loadspeed = 400/(upgrades['load speed']+8)
        self.capacity = upgrades['lift capacity']
        self.floors = floors
##        print(self.speed,self.doorspeed,self.loadspeed,self.capacity)

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
        self.delay-=tickmul
        if self.open == 0:
            if self.people!=[]:
                off = -1
                for i,a in enumerate(self.people):
                    if a.targetfloor == self.floor or a.angry:
                        off = i
                if off!=-1:
                    if self.delay<0:
                        self.people[off].unload(self)
                        self.people.remove(self.people[off])
                        self.delay = self.loadspeed
    def attemptload(self,person):
        if self.delay<-1:
            if self.capacity>=len(self.people)+1:
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
            for a in self.people:
                a.blitsurf(surf,a.liftpos,self.height)
            
        surf.blit(self.ldoor,(-self.width/2*d,0))
        surf.blit(self.rdoor,(self.width/2+self.width/2*d,0))
        return surf
        
class Building:
    def __init__(self,level,userdata,newgui=True):
        ## people, patience, arrival speed, floors, score mi
        self.level = level
        self.userdata = userdata
        self.floornum = self.level[3]
        self.liftnum = userdata['upgrades']['lifts']
        self.offset = [-350,-400]
        self.lifts = [Lift(a*140,80,userdata['upgrades'],self.floornum) for a in range(self.liftnum)]
        
        self.people = []
        self.peoplecount = 0
        self.score = 0
        self.coins = 0
        ## angry, complete, score, coins
        self.stats = [0,0,0,0]
        self.popups = []

        self.delay = 0
        self.prevframe = time.time()

        if newgui: self.makegui()
        else: self.updategui()
    def makegui(self):
        ui.maketext(0,0,str(self.score),40,'game','score display',anchor=('w-10',10),objanchor=('w',0),backingcol=(255,255,255))
        ui.maketext(17,70,'',40,'game',img=personmaker(30,'G'),objanchor=(0,'h/2'),colorkey=(0,0,0))
        ui.maketext(95,70,'3',40,'game',objanchor=(0,'h/2'),backingcol=(255,255,255),ID='person count')
        
    def tick(self,animation):
        tickmul = 60*(time.time()-self.prevframe)
        self.prevframe = time.time()

        mprs = pygame.mouse.get_pressed()
        mpos = pygame.mouse.get_pos()
        rel = pygame.mouse.get_rel()
        if mprs[2]:
            self.offset[0]-=rel[0]
            self.offset[1]-=rel[1]
        for a in self.popups:
            a.textoffsetx = -self.offset[0]
            a.textoffsety = -self.offset[1]

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
                self.people.append(Person(f,t,self.lifts,self.userdata['upgrades'],self.level))
                ui.IDs['person count'].text = str(self.level[0])
                ui.IDs['person count'].refresh(ui)
        return False
        
    def draw(self,animation):
        tempoffset = [self.offset[0],self.offset[1]-animation]
        for a in self.lifts:
            a.draw(tempoffset)
        for a in self.people:
            a.draw(tempoffset)
        if self.level[0]>0: ang = math.pi*2*(self.delay/self.level[2])
        else: ang = 0
        pyui.draw.pichart(screen,(70*ui.scale,(70+animation)*ui.scale),15*ui.scale,ui.defaultcol,ang)
            
    def addscore(self,person):
        base = 100
        new = base*(person.patience/person.maxpatience)
        if person.angry:
            self.stats[0]+=1
            new = base*-1
            if person.completed:
                new*=0.5
            self.makepopup('cloud',(person.x+person.image.get_width()/2,person.y-person.image.get_height()-10))
            
        self.score+=int(round(new))
        if person.completed:
            self.stats[1]+=1
            if person.patience>person.maxpatience*0:
                self.coins+=1
                main.userdata['coins']+=1
                main.updatecoindisplay()
                self.makepopup('coin',(person.x+person.image.get_width()/2,person.y-person.image.get_height()))
        self.updategui()
    def updategui(self):
        ui.IDs['score display'].text = str(self.score)
        ui.IDs['score display'].refresh(ui)
        ui.IDs['score display'].resetcords(ui)

    def makepopup(self,typ,cords):
        if typ in ['coin','cloud']:
            if typ == 'coin': img = image.coins
            elif typ == 'cloud': img = image.raincloud
            self.popups.append(ui.maketext(cords[0],cords[1],'',33,'game','popup '+typ,img=img,center=True,textoffsetx=-self.offset[0],textoffsety=-self.offset[1]))
            func = funcerk(self.popups[-1].ID,self)
            ui.makeanimation(self.popups[-1].ID,'current',(0,-100),'sinin',command=func.func,relativemove=True)
    def killpopup(self,ID):
        self.popups.remove(ui.IDs[ID])
        ui.delete(ID)
        
class Main:
    def __init__(self):
        ## people, patience, arrival speed, floors, score min
        self.levels = [[3,10,300,2,100],
                       [10,2,250,2,400],
                       [20,1.8,180,3,800],
                       [50,1.6,150,3,2700],
                       [75,1.5,130,3,4500],
                       [100,1.4,120,3,7000],
                       [140,1.3,110,4,95000],
                       [180,1.2,105,4,12500],
                       [220,1.1,100,4,15000],
                       [300,1.0,95,5,22000]]
                       
        self.loaddata()
               
        random.seed(0)
        for a in range(len(self.levels)):
            self.levels[a].append(random.randint(0,1000))
        self.building = 0


        self.makegui()
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

        ## upgrades
        ui.maketext(10,10,'',33,'universal',img=image.coins,menuexceptions=['complete'])
        ui.maketext(52,31,str(self.userdata['coins']),40,'universal','coin display',objanchor=(0,'h/2'),backingcol=(255,255,255),menuexceptions=['complete'])

        for i,a in enumerate(list(self.userdata['upgrades'])):
            ui.maketext(100,80+80*i,a,40,'upgrades',backingcol=(255,255,255),center=True)
            self.makebuybar(a,200,80+80*i)
            
        ## levels
        ui.maketable(20,70,[[0,0]],menu='levels',roundedcorners=4,boxwidth=[400,300],textsize=30,verticalspacing=4,ID='level tables')
        self.refreshleveltable()

        ## complete menu
        ui.makewindowedmenu(0,0,400,300,'complete','game',anchor=('w/2','h/2'),center=True,roundedcorners=10)
        ui.maketext(200,10,'Level - Complete',45,'complete','level complete title',backingcol=(115,115,115),objanchor=('w/2',0))
        ui.maketable(10,50,[[0,0]],menu='complete',boxwidth=[200,174],boxheight=50,textsize=30,backingdraw=False,borderdraw=False,col=(115,115,115),ID='complete table')
        
    def gengame(self,level=-1):
        if level!=-1: self.level = self.levels[level][:]
        else: self.level = [10000000,1,180,2,3,1,time.time()]

        if self.building == 0:
            self.building = Building(self.level[:],self.userdata,True)
        else:
            self.building = Building(self.level[:],self.userdata,False)
        ui.movemenu('game','up')
    def finishgame(self):
        levelnum = self.levels.index(self.level)
        ui.movemenu('complete','down')
        del ui.backchain[-1]
        ui.IDs['level complete title'].text = f'Level {levelnum+1} Complete'
        ui.IDs['level complete title'].refresh(ui)
        ui.IDs['complete table'].data = [[a,self.building.stats[i]] for i,a in enumerate(['Angered','Completed','score','Coins'])]
        ui.IDs['complete table'].boxheight=45
        ui.IDs['complete table'].refresh(ui)

        if self.userdata['highscores'][levelnum] == '-' or self.building.stats[2]>self.userdata['highscores'][levelnum]:
            self.userdata['highscores'][levelnum] = self.building.stats[2]
        self.userdata['unlocked'] = 1
        while (self.userdata['highscores'][self.userdata['unlocked']-1] != '-' and self.userdata['highscores'][self.userdata['unlocked']-1]>self.levels[self.userdata['unlocked']-1][4]):
            self.userdata['unlocked']+=1
        self.refreshleveltable()
        self.storedata()
            
    def refreshleveltable(self):
        ui.IDs['level tables'].wipe(ui)
        data = []
        for a in range(len(self.levels)):
            func = funcer(a,self)
            if a<self.userdata['unlocked']: data.append([ui.makebutton(0,0,f'Level {a+1}',30,func.func,roundedcorners=4,verticalspacing=4)])
            else: data.append([ui.makebutton(0,0,'{lock scale=0.6}',30,roundedcorners=4,verticalspacing=4,clickdownsize=0)])
            data[-1].append(f"{self.userdata['highscores'][a]}/{self.levels[a][4]}")
        ui.IDs['level tables'].data = data
        ui.IDs['level tables'].refresh(ui)
    def makebuybar(self,item,x=0,y=0):
        upgrades = 20
        if item+'buybar' in ui.IDs:
            ui.IDs[item+'buybar'].wipe(ui)
        else:
            ui.maketable(x,y-19,[[]],menu='upgrades',ID=item+'buybar',roundedcorners=4,boxwidth=[60,40]+[20 for a in range(upgrades)]+[40])
        cost = 2**self.userdata['real upgrades'][item]
        if item == 'lifts': cost = (cost**2)*2
        elif item == 'lift capacity': cost*=3
        
        func = funcerbuy(item,cost,self)
        data = [ui.makebutton(0,0,str(cost),30,func.func,roundedcorners=4),'-']
        for a in range(upgrades):
            col = (120,120,120)
            if a<self.userdata['upgrades'][item]: col = (120,160,120)
            if a<self.userdata['real upgrades'][item]: col = (100,250,140)
            data.append(ui.maketext(0,0,'',10,backingcol=col,roundedcorners=4))
        data.append('+')
        ui.IDs[item+'buybar'].data = [data]
        ui.IDs[item+'buybar'].refresh(ui)
                        
                
    def buy(self,item,cost):
        if self.userdata['coins']>=cost:
            if self.userdata['real upgrades'][item]<20:
                self.userdata['coins']-=cost
                self.userdata['real upgrades'][item]+=1
                self.userdata['upgrades'][item]+=1
                self.makebuybar(item)
                self.updatecoindisplay()
                self.storedata()
    def updatecoindisplay(self):
        ui.IDs['coin display'].text = str(self.userdata['coins'])
        ui.IDs['coin display'].refresh(ui) 
        
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
                        self.finishgame()
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

    def storedata(self):
        with open(pyui.resourcepath('assets\\data.txt'),'w') as f:
            f.write(str(self.userdata))
    def loaddata(self):
        if not os.path.isfile(pyui.resourcepath('assets\\data.txt')):
            self.cleardata()
        with open(pyui.resourcepath('assets\\data.txt'),'r') as f:
            item = f.readlines()[0]
        exec('globaluserdata = '+item,globals())
        self.userdata = globaluserdata
    def cleardata(self):
        self.userdata = {'unlocked':1,'highscores':['-' for a in range(len(self.levels))],'coins':0,
                     'upgrades':{'lifts':1,'lift speed':1,'load speed':1,'door speed':1,'lift capacity':1,'floor speed':1}}
        self.userdata['real upgrades'] = {}
        for a in list(self.userdata['upgrades']):
            self.userdata['real upgrades'][a] = self.userdata['upgrades'][a]
        self.storedata()
main = Main()
main.main()


##ui.makerect(100,300,200,6,glow=10,glowcol=(50,20,160,30),col=(245,235,255),roundedcorners=2,menu='game')


