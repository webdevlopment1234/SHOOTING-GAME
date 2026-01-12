import arcade
import math
import random

SCREEN_WIDTH=900
SCREEN_HEIGHT=600
SCREEN_TITLE="My Python Game"
PLAYER_SCALE=0.5
PLAYER_SPEED=5

BULLET_SPEED=10
BULLET_SCALE=0.2

ENEMY_SPAWN_RATE = 1
ENEMY_SPEED_MIN = 1
ENEMY_SPEED_MAX = 3
ENEMY_SCALE = 0.5

class Enemy:
    def __init__(self):
        side = random.choice(['top', 'bottom', 'left', 'right'])

        if side == 'top':
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = SCREEN_HEIGHT + 20
        elif side == 'right':
            self.x = SCREEN_WIDTH + 20
            self.y = random.randint(0, SCREEN_HEIGHT)
        elif side == 'bottom':
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = -20
        else:
            self.x = -20
            self.y = random.randint(0, SCREEN_HEIGHT)
            
        self.speed = random.uniform(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)
        self.angle = 0
        self.radius = 150 * ENEMY_SCALE
        self.health = 1

    def update(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y
        self.angle = math.degrees(math.atan2(dy, dx))
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed

    
    def draw(self):
        arcade.draw_triangle_filled(
            self.x + math.cos(math.radians(self.angle)) * self.radius,
            self.y + math.sin(math.radians(self.angle)) * self.radius,
            self.x + math.cos(math.radians(self.angle + 150)) * self.radius,
            self.y + math.sin(math.radians(self.angle + 150)) * self.radius,
            self.x + math.cos(math.radians(self.angle - 150)) * self.radius,
            self.y + math.sin(math.radians(self.angle - 150)) * self.radius,
            arcade.color.RED
        )

class Bullet:

    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = BULLET_SPEED
        self.radius = 4 * BULLET_SCALE

    def update(self):
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed
    def draw(self):
        arcade.draw_circle_filled(self.x, self.y, 5, arcade.color.YELLOW)

    def is_off_screen(self):
        return (self.x < 0 or self.x > SCREEN_WIDTH or
                self.y < 0 or self.y > SCREEN_HEIGHT)

class GameWindow(arcade.Window):
    def __init__(self):
      super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
      arcade.set_background_color(arcade.color.BLACK)

      self.player_x = SCREEN_WIDTH // 2
      self.player_y = SCREEN_HEIGHT // 2
      self.player_angle = 0
      self.player_radius = 150 * PLAYER_SCALE

      self.pressed_keys = set()
      self.bullets = []
      self.shoot_cooldown = 0
      self.enemies = []
      self.enemy_spawn_timer = 0
      self.score = 0
      self.game_state = "playing"  # "playing", "won", "lost"

    def on_draw(self):
      self.clear()
      
      if self.game_state == "playing":
          arcade.draw_triangle_filled(
             self.player_x + math.cos(math.radians(self.player_angle)) * self.player_radius*1.5,
             self.player_y + math.sin(math.radians(self.player_angle)) * self.player_radius*1.5,
             self.player_x + math.cos(math.radians(self.player_angle + 150)) * self.player_radius,
             self.player_y + math.sin(math.radians(self.player_angle + 150)) * self.player_radius,
             self.player_x + math.cos(math.radians(self.player_angle - 150)) * self.player_radius,
             self.player_y + math.sin(math.radians(self.player_angle - 150)) * self.player_radius,
             arcade.color.WHITE
          )
          for bullet in self.bullets:
              bullet.draw()
          for enemy in self.enemies:
              enemy.draw()
              
          arcade.draw_text(f"Score: {self.score}", 10, SCREEN_HEIGHT - 30, arcade.color.WHITE, 20)
      
      elif self.game_state == "won":
          arcade.draw_text("YOU WIN!", SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, arcade.color.GREEN, 50)
          arcade.draw_text(f"Final Score: {self.score}", SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 - 60, arcade.color.WHITE, 30)
          arcade.draw_text("Press R to restart", SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 120, arcade.color.WHITE, 20)
      
      elif self.game_state == "lost":
          arcade.draw_text("GAME OVER", SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2, arcade.color.RED, 50)
          arcade.draw_text(f"Final Score: {self.score}", SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 - 60, arcade.color.WHITE, 30)
          arcade.draw_text("Press R to restart", SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 120, arcade.color.WHITE, 20)

    def on_update(self, delta_time):
        if self.game_state != "playing":
            return
            
        self.shoot_cooldown -= delta_time
        self.enemy_spawn_timer += delta_time
        
        if self.enemy_spawn_timer >= ENEMY_SPAWN_RATE:
            self.enemies.append(Enemy())
            self.enemy_spawn_timer = 0
        
        if arcade.key.SPACE in self.pressed_keys:
            self.shoot()
        if arcade.key.W in self.pressed_keys:
            self.player_y += PLAYER_SPEED
        if arcade.key.S in self.pressed_keys:
            self.player_y -= PLAYER_SPEED
        if arcade.key.A in self.pressed_keys:
            self.player_x -= PLAYER_SPEED
        if arcade.key.D in self.pressed_keys:
            self.player_x += PLAYER_SPEED

        self.player_x = max(self.player_radius, min(SCREEN_WIDTH - self.player_radius, self.player_x))
        self.player_y = max(self.player_radius, min(SCREEN_HEIGHT - self.player_radius, self.player_y))
        
        for bullet in self.bullets:
            bullet.update()
        self.bullets = [bullet for bullet in self.bullets if not bullet.is_off_screen()]
        
        for enemy in self.enemies:
            enemy.update(self.player_x, self.player_y)
            
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if math.sqrt((bullet.x - enemy.x)**2 + (bullet.y - enemy.y)**2) < enemy.radius:
                    self.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.score += 10
                    break
        
        for enemy in self.enemies:
            if math.sqrt((enemy.x - self.player_x)**2 + (enemy.y - self.player_y)**2) < self.player_radius + enemy.radius:
                self.game_state = "lost"
                break
        
        if self.score >= 100:
            self.game_state = "won"

    def shoot(self):
        if self.shoot_cooldown <= 0:
            bullet_x = self.player_x + math.cos(math.radians(self.player_angle)) * self.player_radius
            bullet_y = self.player_y + math.sin(math.radians(self.player_angle)) * self.player_radius
            self.bullets.append(Bullet(bullet_x, bullet_y, self.player_angle))
            self.shoot_cooldown = 0.3

    def on_key_press(self, key, modifiers):
        self.pressed_keys.add(key)
        if key == arcade.key.R and self.game_state != "playing":
            self.restart_game()
    
    def restart_game(self):
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT // 2
        self.player_angle = 0
        self.bullets = []
        self.enemies = []
        self.score = 0
        self.shoot_cooldown = 0
        self.enemy_spawn_timer = 0
        self.game_state = "playing"
        
    def on_key_release(self, key, modifiers):
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)
            
    def on_mouse_motion(self, x, y, dx, dy):
        dx = x - self.player_x
        dy = y - self.player_y
        self.player_angle = math.degrees(math.atan2(dy, dx))
        
    def on_mouse_press(self, x, y, button, modifiers):
        dx = x - self.player_x
        dy = y - self.player_y
        self.player_angle = math.degrees(math.atan2(dy, dx))
              



def main():
    window = GameWindow()
    arcade.run()

if __name__ == "__main__":
   main()

        