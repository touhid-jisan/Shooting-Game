from glob import glob
from settings import * 
from sprites import * 
# from sprites import COUNT

from groups import AllSprites
from support import * 
from timer import Timer
from random import randint

class Game:
    def __init__(self):
        pygame.init()
        
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Platformer')
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()
        self.running = True
        self.score = 0

        # groups 
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # load game 
        self.load_assets()
        self.setup()

        # timers 
        self.bat_timer = Timer(100, func = self.create_bat, autostart = True, repeat = True)
    
    def create_bat(self):
        Bat(frames = self.bat_frames, 
            pos = ((self.level_width + WINDOW_WIDTH),(randint(0,self.level_height))), 
            groups = (self.all_sprites, self.enemy_sprites),
            speed = randint(300,500))

    def create_bullet(self, pos, direction):
        y_offset = -25  # Change this value to adjust the height
        x = pos[0] + direction * 34 if direction == 1 else pos[0] + direction * 34 - self.bullet_surf.get_width()
        Bullet(self.bullet_surf, (x, pos[1] + y_offset), direction, (self.all_sprites, self.bullet_sprites))
        Fire(self.fire_surf, pos, self.all_sprites, self.player)
        self.audio['shoot'].play()

    def load_assets(self):
        # graphics 
        self.player_frames = import_folder('images', 'player')
        self.bullet_surf = import_image('images', 'gun', 'bullet')
        self.fire_surf = import_image('images', 'gun', 'fire')
        self.bat_frames = import_folder('images', 'enemies', 'bat')
        self.zombie_frames = import_folder('images', 'enemies', 'zombie')
        self.background_image = pygame.image.load('./data/background/bg_1.jpg').convert()
        # sounds 
        self.audio = audio_importer('audio')

    # def display_win_message(self):
    #     win_surface = self.font.render("You Win!", True, (255, 255, 255))  # White color
    #     win_rect = win_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    #     self.display_surface.blit(win_surface, win_rect)
    #     pygame.display.update()

    #     # Pause for a few seconds to let the player see the message
    #     pygame.time.delay(2000)  # Delay for 2 seconds

    def display_win_popup(self):
        # Create a surface for the popup
        popup_surface = pygame.Surface((400, 200))  # Width, Height of popup
        popup_surface.fill((0, 0, 0))  # Fill with black color
        popup_surface.set_alpha(200)  # Make it semi-transparent

        # Create text for the win message
        win_surface = self.font.render("You Win!", True, (255, 255, 255))  # White color
        message_surface = self.font.render("Press any key to exit.", True, (255, 255, 255))  # White color

        # Get the rectangles for centering
        win_rect = win_surface.get_rect(center=(200, 70))
        message_rect = message_surface.get_rect(center=(200, 130)) 
        # Calculate the position of the popup
        popup_x = (WINDOW_WIDTH - popup_surface.get_width()) // 2
        popup_y = (WINDOW_HEIGHT - popup_surface.get_height()) // 2

        # Draw the popup and text
        self.display_surface.blit(popup_surface, (popup_x, popup_y))  
        self.display_surface.blit(win_surface, (popup_x + win_rect.x, popup_y + win_rect.y)) 
        self.display_surface.blit(message_surface, (popup_x + message_rect.x, popup_y + message_rect.y)) 

        # Update the display
        pygame.display.update()

        # Wait for a key press to exit
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                if event.type == pygame.KEYDOWN:  # Exit on any key press
                    waiting = False

        pygame.time.wait(4000)


    def setup(self):
        tmx_map = load_pygame(join('data', 'maps', 'world.tmx'))
        self.level_width = tmx_map.width * TILE_SIZE
        self.level_height = tmx_map.height * TILE_SIZE

        for x, y, image in tmx_map.get_layer_by_name('Main').tiles():
            Sprite((x * TILE_SIZE,y * TILE_SIZE), image, (self.all_sprites, self.collision_sprites))
        
        for x, y, image in tmx_map.get_layer_by_name('Decoration').tiles():
            Sprite((x * TILE_SIZE,y * TILE_SIZE), image, self.all_sprites)
        
        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.player_frames, self.create_bullet)
            if obj.name == 'Worm':
                Zombie(self.zombie_frames, pygame.Rect(obj.x, obj.y, obj.width, obj.height), (self.all_sprites, self.enemy_sprites))

        # self.audio['music'].play(loops = -1)

    def collision(self):
        # bullets -> enemies 
        for bullet in self.bullet_sprites:
            sprite_collision = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
            if sprite_collision:
                self.audio['impact'].play()
                self.score += 1
                bullet.kill()
                for sprite in sprite_collision:
                    sprite.destroy()
        
        # enemies -> player
        # if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
        #     self.running = False
        
    # def display_count(self, display_surface, font):
    #     # global COUNT
    #     count_surface = font.render(f"Score: {COUNT}", True, (255, 255, 255))  # White color
    #     display_surface.blit(count_surface, (10, 10))
        
    def display_count(self, display_surface, font):
        count_surface = font.render(f"Score: {self.score}", True, (255, 255, 255))  # White color
        display_surface.blit(count_surface, (10, 10))
        
    def run(self):
        while self.running:
            dt = self.clock.tick(FRAMERATE) / 1000 

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False 
            
            # update
            self.bat_timer.update()
            self.all_sprites.update(dt)
            self.collision()

            # draw 
            # self.display_surface.fill(BG_COLOR)
            self.display_surface.blit(self.background_image, (0, 0))
            self.all_sprites.draw(self.player.rect.center)
            self.display_count(self.display_surface, self.font)
            
            
            if self.score >= 25:
                # win_surface = self.font.render("You Win!", True, (255, 255, 255))  # White color
                # win_rect = win_surface.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
                # self.display_surface.blit(win_surface, win_rect)
                # pygame.display.update()
                # pygame.time.wait(2000)  # Display the message for 2 seconds
                self.display_win_popup()
                self.running = False  # Stop the game
            pygame.display.update()
        
        pygame.quit()
 
if __name__ == '__main__':
    game = Game()
    game.run() 