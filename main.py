import pgzrun
from pygame import Rect


# CONFIG AND CONSTANTS
# ==========================================

# Window config
TITLE = "Alien Platformer Adventure"
WIDTH = 825
HEIGHT = 512 


TILE_SIZE = 64
GRAVITY = 0.8
JUMP_FORCE = -14
PLAYER_SPEED = 5

# Game States
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_WIN = "win"
STATE_LOSE = "lose"

# Global Variables
current_state = STATE_MENU
sound_enabled = True
music_playing = False


# MAP ASSETS
# ==========================================

LEVEL_MAP = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 99],
    [11, 12, 13, 0, 0, 0, 0, 13, 0, 0, 0, 7, 8], 
    [2, 2, 2, 3, 0, 0, 1, 2, 2, 3, 0, 0, 0], 
    [5, 5, 5, 6, 0, 0, 4, 5, 5, 6, 0, 0, 0],
    [5, 5, 5, 6, 0, 0, 4, 5, 5, 6, 0, 0, 0], 
]

TILE_IMAGES = {
    1: "grass1", 2: "grass2", 3: "grass3", 4: "ground1", 5: "ground2", 6: "ground3", 7: "isle1", 8: "isle2", 9: "isle3",
    11: "fence", 12: "fence_broken", 13: "plant", 99: "door"
}
SOLID_TILES = [1, 2, 3, 4, 5, 6, 7, 8, 9]

# ==========================================
# CLASSES
# ==========================================

class Player:
    def __init__(self):
        self.rect = Rect(100, 50, 40, 50) # Spawn
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.is_dead = False
        # Anim config
        self.frame_index = 0
        self.anim_timer = 0

    def update(self, tiles):
        # Physics
        self.vy += GRAVITY
        
        # Horizontal Movement
        self.rect.x += self.vx
        
        # Prevents exiting the screen
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > WIDTH: self.rect.right = WIDTH

        self.check_collision(tiles, "x")
        
        # Vertical Movement
        self.rect.y += self.vy
        self.on_ground = False
        self.check_collision(tiles, "y")
        
        # Fall death
        if self.rect.top > HEIGHT:
            self.is_dead = True

        self.animate()

    def check_collision(self, tiles, axis):
        for tile_rect in tiles:
            if self.rect.colliderect(tile_rect):
                if axis == "x":
                    if self.vx > 0: self.rect.right = tile_rect.left
                    elif self.vx < 0: self.rect.left = tile_rect.right
                elif axis == "y":
                    if self.vy > 0:
                        self.rect.bottom = tile_rect.top
                        self.vy = 0
                        self.on_ground = True
                    elif self.vy < 0:
                        self.rect.top = tile_rect.bottom
                        self.vy = 0

    def animate(self):
        self.anim_timer += 1
        if self.anim_timer > 10:
            self.anim_timer = 0
            self.frame_index = (self.frame_index + 1) % 2

    def draw(self):
        state_prefix = "hero_idle" if self.vx == 0 else "player_run"
        img_name = f"{state_prefix}_{self.frame_index}"
        offset_x = 12
        offset_y = 66 # Ajust hero position
        screen.blit(img_name, (self.rect.x - offset_x, self.rect.y - offset_y))

    def jump(self):
        if self.on_ground:
            self.vy = JUMP_FORCE
            if sound_enabled:
                sounds.jump.play()

class Enemy:
    def __init__(self, x, y):
        self.rect = Rect(x, y, 30, 30)
        self.speed = 2
        self.direction = 1
        self.frame_index = 0
        self.anim_timer = 0

    def update(self, tiles):
        self.rect.x += self.speed * self.direction
        
        # Turn when hit tiles
        for tile_rect in tiles:
            if self.rect.colliderect(tile_rect):
                self.direction *= -1
                self.rect.x += self.direction * 5
        
        # Turn when hit the screen border
        if self.rect.right >= WIDTH:
            self.direction = -1
        if self.rect.left <= 0:
            self.direction = 1
        
        # Animation loop
        self.anim_timer += 1
        if self.anim_timer > 15:
            self.anim_timer = 0
            self.frame_index = (self.frame_index + 1) % 2

    def draw(self):
        screen.blit(f"enemy_{self.frame_index}", self.rect.topleft)


# ==========================================
# GAME SETUP
# ==========================================

player = Player() # Create player
enemies = [Enemy(200, 190), Enemy(600, 250)] # Create enemy

level_tiles = []
door_rect = None

# Build Level
for r, row in enumerate(LEVEL_MAP):
    for c, tile_id in enumerate(row):
        if tile_id in SOLID_TILES: # Append to the collision list
            level_tiles.append(Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        if tile_id == 99:
            door_rect = Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)

# Menu Buttons
btn_start = Rect(WIDTH//2 - 100, 200, 200, 50)
btn_sound = Rect(WIDTH//2 - 100, 270, 200, 50)
btn_exit = Rect(WIDTH//2 - 100, 340, 200, 50)

# ==========================================
# CORE FUNCTIONS
# ==========================================

def update():
    global current_state, music_playing

    # Music Logic
    if sound_enabled and not music_playing:
        music.play("music.wav") 
        music.set_volume(0.2)
        music_playing = True
    elif not sound_enabled and music_playing:
        music.stop()
        music_playing = False

    if current_state == STATE_PLAYING:
        player.vx = 0
        if keyboard.left: player.vx = -PLAYER_SPEED
        if keyboard.right: player.vx = PLAYER_SPEED
        
        player.update(level_tiles)
        
        for enemy in enemies:
            enemy.update(level_tiles)
            if player.rect.colliderect(enemy.rect):
                if sound_enabled:
                    sounds.hit.play()
                current_state = STATE_LOSE
        
        if door_rect and player.rect.colliderect(door_rect):
            current_state = STATE_WIN
            
        if player.is_dead:
            current_state = STATE_LOSE

def draw():
    screen.clear()
    
    if current_state == STATE_MENU:
        draw_menu()
    elif current_state == STATE_PLAYING:
        draw_game()
    elif current_state in (STATE_WIN, STATE_LOSE):
        draw_game_over()

def draw_menu():
    screen.fill((30, 30, 40))
    screen.draw.text("ALIEN ADVENTURE", center=(WIDTH//2, 100), fontsize=60, color="white")
    
    for btn, text in [(btn_start, "START GAME"), (btn_sound, f"SOUND: {'ON' if sound_enabled else 'OFF'}"), (btn_exit, "EXIT")]:
        screen.draw.filled_rect(btn, (50, 50, 150))
        screen.draw.text(text, center=btn.center, fontsize=30, color="white")

def draw_game():
    for x in range(0, WIDTH, TILE_SIZE):
        for y in range(0, HEIGHT, TILE_SIZE):
            screen.blit("bg_sky", (x, y))
            
    for r, row in enumerate(LEVEL_MAP):
        for c, tile_id in enumerate(row):
            if tile_id in TILE_IMAGES:
                screen.blit(TILE_IMAGES[tile_id], (c * TILE_SIZE, r * TILE_SIZE))
                
    player.draw()
    for enemy in enemies:
        enemy.draw()

def draw_game_over():
    screen.fill((20, 0, 0) if current_state == STATE_LOSE else (0, 20, 0))
    msg = "VICTORY!" if current_state == STATE_WIN else "GAME OVER"
    screen.draw.text(msg, center=(WIDTH//2, HEIGHT//2), fontsize=60, color="white")
    screen.draw.text("Click to Return to Menu", center=(WIDTH//2, HEIGHT//2 + 60), fontsize=30)

def on_key_down(key): # Check UP Inputs
    if current_state == STATE_PLAYING:
        if key == keys.UP:
            player.jump()

def on_mouse_down(pos): # Checck mouse Inputs
    global current_state, sound_enabled
    
    if current_state == STATE_MENU:
        if btn_start.collidepoint(pos):
            reset_game()
            current_state = STATE_PLAYING
        elif btn_sound.collidepoint(pos):
            sound_enabled = not sound_enabled
        elif btn_exit.collidepoint(pos):
            quit()
            
    elif current_state in (STATE_WIN, STATE_LOSE):
        current_state = STATE_MENU

def reset_game(): #Restart game
    global player, enemies
    player = Player()
    enemies = [Enemy(200, 190), Enemy(600, 250)]

pgzrun.go()