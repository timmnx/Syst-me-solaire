from random import randint
import sys
import pygame
import pygame.locals
import sqlite3
from math import pi, cos, sin, log

# paramètres systeme
ua      = 149597870700#150*10**9 # en metres
g       = 6.67*10**-11
orbit   = False
trace   = False
d_t     = 60*60*24*7 # = /\t

# parametres gui
dim     = (1080,720)
ua_p    = ua / 100 # nb de metres/pixel
axis    = [0,0] 
fps     = 120
show_fps= False
zoom    = 0
time    = 0
slide   = [0,0]
run     = True

class Astres:
    def __init__(self, name, belong, a, e, weight, s, color, orbit, rings):
        self.name   = name
        self.belong = None
        for centre in astres:
            if centre.name == belong:
                self.belong = centre
        if self.belong != None:
            self.a      = a
            self.e      = e
            self.b      = self.a*(1-self.e**2)**0.5
        self.teta   = 0
        self.weight = weight
        self.size   = s
        self.color  = color
        self.orbit  = orbit # nb de sec/orbite
        self.rings  = rings
        self.coords = {'x' : 0, 'y' : 0}
        self.c      = {'x' : 0, 'y' : 0}
        self.acc    = {'x' : 0, 'y' : 0}
        self.f      = {'x' : 0, 'y' : 0}
    def coords_initials(self, teta):
        if self.belong != None:
            self.teta       = teta
            self.coords['x']= self.a*cos(self.teta) + self.belong.coords['x']
            self.coords['y']= self.b*sin(self.teta) + self.belong.coords['y']
    def c_initial(self):
        if self.belong != None:
            µ            = g*self.belong.weight
            a            = self.a
            d_x          = self.coords['x']-self.belong.coords['x']
            d_y          = self.coords['y']-self.belong.coords['y']
            r            = (d_x**2+d_y**2)**0.5
            c_0          = (µ*(2/r-1/a))**0.5
            print("\n",self.name,"\n\tµ   =", µ, "\n\tr   =", r, "\n\ta   =", a, "\n\tc_0 =", c_0)
            v_dir        = {'x' : -self.a*sin(self.teta),
                            'y' : self.b*cos(self.teta)}
            n_dir        = (v_dir['x']**2+v_dir['y']**2)**0.5
            self.c['x']  = self.belong.c['x'] + v_dir['x']*c_0/n_dir
            self.c['y']  = self.belong.c['y'] + v_dir['y']*c_0/n_dir
    def force(self, other):
        d_x             = other.coords['x'] - self.coords['x']
        d_y             = other.coords['y'] - self.coords['y']
        d               = (d_x**2 + d_y**2)**0.5
        f               = g*self.weight*other.weight/d**2
        self.f['x']     += f*d_x/d
        self.f['y']     += f*d_y/d
    def acceleration(self):
        self.acc['x']   = self.f['x']/self.weight
        self.acc['y']   = self.f['y']/self.weight
    def celerity(self):
        self.c['x']     += self.acc['x']*d_t/fps
        self.c['y']     += self.acc['y']*d_t/fps
    def position(self):
        self.coords['x']+= self.c['x']*d_t/fps
        self.coords['y']+= self.c['y']*d_t/fps

astres = []
base = sqlite3.connect('systeme.db')
for e in base.execute('''SELECT * FROM Astres'''):
    astres += [Astres(e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7], e[8])]
base.close()

for astre in astres:
    if astre.name != "Soleil":
        astre.coords_initials(randint(0,6))
        astre.c_initial()
        print("\tc   =", astre.c)

pygame.init()
screen  = pygame.display.set_mode(dim, pygame.locals.RESIZABLE)
pygame.display.set_caption("Le Système Solaire")
clock   = pygame.time.Clock()
center  = astres[0]

while run:
    clock.tick(fps)
    if orbit:
        trace = False
    if not trace:
        screen.fill("black")
    if show_fps:
        show_o = "Activées" if orbit else "Désactivées"
        pygame.display.set_caption(f"Le Systeme"
                                   f" --- Centre : {center.name}"
                                   f" --- Décallage (x, y) : {axis[0], -axis[1]}"
                                   f" --- Orbites : {show_o}"
                                   f" --- Échelle : {round(ua_p/ua,3)} ua/pixel"
                                   f" --- {round(d_t/(60*60*24), 3)} jours/s"
                                   f" --- FPS : {int(clock.get_fps())}")
    ### Events manager ###
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            sys.exit()
        if event.type == pygame.KEYDOWN:
            #print(str(pygame.key.name(event.key)))
            if event.key == pygame.K_ESCAPE:
                run = False
                sys.exit()
            elif event.key == pygame.K_RETURN:
                orbit   = not orbit
                trace   = False
                screen.fill("black")
            elif event.key == pygame.K_t:
                trace   = not trace
                orbit   = False
                screen.fill("black")
            elif event.key == pygame.K_F3:
                show_fps= not show_fps
                if not show_fps:
                    pygame.display.set_caption("Le Systeme Solaire")
            elif event.key == pygame.K_SPACE:
                ua_p    = ua/100
                d_t     = 60*60*24*7
                axis    = [0,0]
                center  = astres[0]
                screen.fill("black")
            elif str(pygame.key.name(event.key)) in ("0","1","2","3","4","5","6","7","8","9"):
                center  = astres[int(pygame.key.name(event.key))]
                screen.fill("black")

            if event.key in (pygame.K_UP,pygame.K_DOWN):
                zoom    = 1.01 if event.key==pygame.K_UP else (100/101)
            if event.key in (pygame.K_LEFT,pygame.K_RIGHT):
                time    = 1.01 if event.key==pygame.K_RIGHT else (100/101)
            if event.key in (pygame.K_q,pygame.K_d):
                slide[0]= 1 if event.key==pygame.K_d else -1
            if event.key in (pygame.K_z,pygame.K_s):
                slide[1]= 1 if event.key==pygame.K_s else -1
            
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_UP, pygame.K_DOWN):
                zoom    = 0
            if event.key in (pygame.K_LEFT,pygame.K_RIGHT):
                time    = 0
            if event.key in (pygame.K_q,pygame.K_d):
                slide[0]= 0
            if event.key in (pygame.K_z,pygame.K_s):
                slide[1]= 0
    
    if zoom != 0 :
        ua_p    /= zoom
        screen.fill("black")
    if ua_p > 0.25*ua:
        ua_p    = 0.25*ua
    elif ua_p < 0.0001*ua:
        ua_p    = 0.0001*ua

    if time != 0:
        d_t     *= time
    if d_t < 86400:
        d_t     = 86400
    elif d_t > 10368000:
        d_t     = 10368000
    
    if slide != [0,0]:
        screen.fill("black")
        axis[0] += slide[0]
        axis[1] += slide[1]

    for astre in astres:
        if astre.name != "Soleil":
            astre.f['x'], astre.f['y'] = 0,0
            for other in astres:
                if other != astre:
                    astre.force(other)
    for astre in astres:
        if astre.name != "Soleil":
            astre.acceleration()
            astre.celerity()
            astre.position()
        x : float =  (astre.coords['x'] - center.coords['x'])/ua_p + screen.get_size()[0]/2
        # y est inversé car l'axe y de pygame est positif vers le bas
        y : float = -(astre.coords['y'] - center.coords['y'])/ua_p + screen.get_size()[1]/2
        # grossissement à une échelle logarithmique pour voir la "taille" des astres
        s : int = (1.5*10**8)*log(astre.size)/ua_p
        if astre.rings:
            r : int = int(s*1.5 if s*1.5>3 else 3)
            w : int = int(s/4 if s/4>1 else 1)
            pygame.draw.circle(screen, "grey", (x+axis[0], y+axis[1]), int(s*1.5), int(s/4))
        if orbit and astre.belong!=None:
            '''Affiche les orbites (cercles)'''
            d_x : float = astre.coords['x'] - astre.belong.coords['x']
            d_y : float = astre.coords['y'] - astre.belong.coords['y']
            d   : float = ((d_x**2 + d_y**2)**0.5) / ua_p
            c_x : float =  (astre.belong.coords['x'] - center.coords['x'])/ua_p + screen.get_size()[0]/2
            c_y : float = -(astre.belong.coords['y'] - center.coords['y'])/ua_p + screen.get_size()[1]/2
            pygame.draw.circle(screen, astre.color, (c_x+axis[0], c_y+axis[1]), d+1, 1)
        pygame.draw.circle(screen, astre.color, (x+axis[0], y+axis[1]), (s if s>1 else 1))
    pygame.display.flip()
