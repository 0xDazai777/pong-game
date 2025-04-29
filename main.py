import pygame as pg
import random

class Score:
    scoreText = None
    scoreRect = None
    score = 0

class Ball:
    
    bCoords = [0,0]
    bRadius = 0
    bDirection = [0,0]
    ball_speed = 5
    def move_ball(self,collision=False):
        """Calculates where to move the ball"""
        if collision:
            # refelection of (x,y) = (y,-x)
            self.bDirection = [self.bDirection[1], -self.bDirection[0]]
        
        self.bCoords[0] += self.ball_speed * self.bDirection[0]
        self.bCoords[1] += self.ball_speed * self.bDirection[1]

    def set_direction(self):
        """Sets random direction of ball"""
        
        dirs = {1:[-1,-1], 2:[1,-1], 3:[1,1], 4:[-1,1]}
        r = random.randint(1,4)
        self.bDirection = dirs[r]
        

cp = Score() # computer
pl = Score() # player
b = Ball()

r1 = None
r2 = None

pg.init()

# Open a window on the screen
screen_width = 700
screen_height = 400
black = (0,0,0)
white = (255,255,255)
grey = (128,128,128)
red = (255,0,0)

win_title = "Pong Game"
win_icon_name = "assets/icon.png"
lscreen_name = "assets/lscreen.png"
bg_sound = "assets/background-sound.mp3"
score_sound = pg.mixer.Sound("assets/buzzer.mp3")
hit_sound = pg.mixer.Sound("assets/blip.mp3")

screen=pg.display.set_mode((screen_width, screen_height), pg.RESIZABLE)
pg.display.set_caption(win_title)

win_icon = pg.image.load(win_icon_name)
pg.display.set_icon(win_icon)

lscreen = pg.image.load(lscreen_name).convert()

score_font = None
pointScored = True

clock = pg.time.Clock()

pg.mixer.music.load(bg_sound)
pg.mixer.music.set_volume(0.3)
score_sound.set_volume(0.5)



def disp_lscreen(curr_win_size: tuple):
    """Displays the loading screen"""
    
    global lscreen
    lscreen = pg.transform.scale(lscreen, curr_win_size)
    screen.blit(lscreen,(0,0))
    

def init_scores(curr_win_size: tuple):
    """Initializing Scores for drawing on the screen"""
    S_W = curr_win_size[0]
    S_H = curr_win_size[1]

    score_font = pg.font.SysFont('ariel',int(1/5*S_H))
    Y = 60

    cp.scoreText = score_font.render(str(cp.score),True,grey,black)
    pl.scoreText = score_font.render(str(pl.score),True,grey,black)
    
    cp.scoreRect = cp.scoreText.get_rect()
    pl.scoreRect = pl.scoreText.get_rect()
    
    cp.scoreRect.center = (S_W//4, Y)
    pl.scoreRect.center = ((3*S_W)//4, Y)

def init_sprites(curr_win_size: tuple):
    """Initalizing the sprites as part of load_game function"""
    global r1,r2
    S_W = curr_win_size[0]
    S_H = curr_win_size[1]
    
    ROD_H = int(1/10 * S_H)
    ROD_W = 10  
    ROD_T = S_H//2 - ROD_H//2
    ROD_L = 30  
    
    r1= pg.Rect(ROD_L,ROD_T,ROD_W,ROD_H)
    r2 = pg.Rect(S_W-ROD_L,ROD_T,ROD_W,ROD_H)
    


def load_game(curr_win_size: tuple):
    """Loads/Resets the game after ENTER is pressed"""
    
    global screen
    S_W = curr_win_size[0]
    S_H = curr_win_size[1]
    cp.score = 0
    pl.score = 0
    screen = pg.display.set_mode(curr_win_size, pg.RESIZABLE)
    screen.fill(black)
    init_sprites(curr_win_size)
    pg.draw.rect(screen,white,r1)
    pg.draw.rect(screen,white,r2)
    pg.draw.line(screen, white, (0,S_W//2), (S_H,S_W//2))
    
    pg.mixer.music.play(-1)


def calc_trajectory(curr_win_size: tuple, ball: Ball, rod: pg.Rect, rod_speed: int) -> tuple:
    """calculates the trajectory of the ball"""
    # r1 = computer
    # r2 = player
    print("calculating trajectory")
    S_W,S_H = curr_win_size
    X,Y = ball.bCoords
    direction = ball.bDirection
    radius = ball.bRadius
    y = 0
    #y = m * (x-X) + Y
    #x = (y-Y)//m + X
    while X > r1.left+r1.width+radius:
        m = direction[0]*direction[1]
        if direction == [-1,-1]:
            
            x = r1.left+r1.width+radius
            y = m * (x-X) + Y
            if y < radius:
                # this means collision
                # we change the direction and coordinate
                # to the collision spot repeat
                y = radius
                x = (y-Y)//m + X
                Y = y
                # direction is altered by reflection
                direction = [direction[0],-direction[1]]
            
        
        elif direction == [-1,1]:
            
            x = r1.left+r1.width+radius
            y = m * (x-X) + Y
            if y > S_H-radius:
                
                y = S_H-radius
                x = (y-Y)//m + X
                Y = y
                direction = [direction[0],-direction[1]]
                
        
        elif direction == [1,-1]:
            
            x = r2.left-radius
            y = m * (x-X) + Y
            if y < radius:
                
                y = radius
                x = (y-Y)//m + X
                Y = y
                
            if r2.left-radius <= x <= r2.left-radius+5:
                direction = [-direction[0], direction[1]]
            else:     
                direction = [direction[0],-direction[1]]     
        
        elif direction == [1,1]:
            
            x = r2.left-radius
            y = m * (x-X) + Y
            if y > S_H-radius:
                
                y = S_H-radius
                x = (y-Y)//m + X
                Y = y
                
            if r2.left-radius <= x <= r2.left-radius+5:
                direction = [-direction[0], direction[1]]
            else:     
                direction = [direction[0],-direction[1]]    
                
        Y = y
        X = x
    # X,Y are the predicted coordinates for the paddle to intercept
    # r1.left is the left measurement of rod1 from screen border
    return X,Y


def move_computer(curr_win_size: tuple, rod: pg.Rect, location:tuple, rod_speed: int)->None:
    if location == (0,0):
        return
    Y = location[1]
    S_H = curr_win_size[1]
    if 0 <= rod.top <= S_H-rod.height and rod.top+rod.height-10 < Y:
        rod.top += rod_speed
    elif 0 <= rod.top <= S_H-rod.height and rod.top+10 > Y:
        rod.top -= rod_speed
    #print(location[1],":",rod.top)


def spawn_ball(curr_win_size: tuple):
    """Calculates where to spawn the ball"""
    S_W,S_H = curr_win_size
    X = S_W//2 + b.bRadius + 10
    start = b.bRadius + 10
    end = S_H - b.bRadius - 10
    Y = random.randint(start,end)
    b.bCoords = [X,Y]
    b.set_direction()

def draw_game(curr_win_size: tuple):
    """Draws the current instance of the game"""
    
    S_W,S_H = curr_win_size
    screen.fill(black)
    pg.draw.rect(screen,white,r1)
    pg.draw.rect(screen,white,r2)
    pg.draw.line(screen, white, (S_W//2,0), (S_W//2,S_H))
    pg.draw.circle(screen,red,b.bCoords,b.bRadius)
    init_scores(curr_win_size)
    screen.blit(cp.scoreText,cp.scoreRect)
    screen.blit(pl.scoreText,pl.scoreRect)
    

# Our main game loop where everything is starts happening

running = True
findTrajectory = False
flag = True
prev = (0,0)
X,Y = 0,0
pointScored = True
collision = False
rod_speed = 4
while running:
    
    curr_win_size = pg.display.get_window_size() # gets the current window size
    keys = pg.key.get_pressed() # gets all the keys pressed atm
    rod_step_size = 0.15 * (curr_win_size[1]/screen_height) # to mainpulate rod speed
    for event in pg.event.get(): # searching for quit event in the event queue
        if event.type == pg.QUIT:
            running = False
        
    if keys[pg.K_RETURN]:  # to reset or load the game
        flag = False
        #print("Starting the game...")
        load_game(curr_win_size)
        prev = curr_win_size
    
    if keys[pg.K_UP] and r2.top > 0:  # to move your rod up
            r2.top -= rod_speed
        
    
    if keys[pg.K_DOWN] and r2.top < (curr_win_size[1]-r2.height): # to move your rod down
            r2.top += rod_speed
          
    
    if flag:
        disp_lscreen(curr_win_size)
    else:
        yDiff = curr_win_size[1] - prev[1]
        xDiff = curr_win_size[0] - prev[0]
        r1.top += yDiff//2
        r2.top += yDiff//2
        r1.height = r2.height = int(1/10 * curr_win_size[1])
        r2.left += xDiff
        prev = curr_win_size
        b.bRadius = r1.height//9
        b.bCoords[0] += xDiff//2
        b.bCoords[1] += yDiff//2
        #S_W,S_H = curr_win_size[0],curr_win_size[1]
        
        if pointScored:
            # play buzzer sound
            score_sound.play()
            pg.time.wait(int(score_sound.get_length() * 1000))  # Wait until sound finishes
            spawn_ball(curr_win_size)
            init_sprites(curr_win_size)
            pointScored = False
            findTrajectory = True
        
        

        r2x = r2.left - b.bRadius
        r1x = r1.left + r1.width + b.bRadius
        b.move_ball(collision)
        collision = False

        if findTrajectory:    
            X,Y = calc_trajectory(curr_win_size,b,r1,rod_speed)
            findTrajectory = False

        move_computer(curr_win_size,r1,(X,Y),rod_speed)
        
        if b.bCoords[0] >= curr_win_size[0] - b.bRadius:
            # point has been scored for computer
            pointScored = True
            cp.score += 1


        elif b.bCoords[0] <= b.bRadius:
            # point has been scored for the player
            pointScored = True
            pl.score += 1

         
        if not pointScored and (
         
            (b.bCoords[1] >= curr_win_size[1] - b.bRadius) or
            (b.bCoords[0] <= b.bRadius) or
            (b.bCoords[1] <= b.bRadius) or
            (r2x <= b.bCoords[0] <= r2x + 10 and r2.top <= b.bCoords[1] <= r2.top + r2.height) or
            (r1x-10 <= b.bCoords[0] <= r1x and r1.top <= b.bCoords[1] <= r1.top + r2.height)
        ):
            hit_sound.play()
            collision = True
        
        if(r1x-10 <= b.bCoords[0] <= r1x and r1.top <= b.bCoords[1] <= r1.top + r2.height):
            findTrajectory = True

        draw_game(curr_win_size) 
    
    pg.display.flip()
    clock.tick(60)

pg.mixer.music.stop()
pg.quit()