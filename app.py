from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import math
import random
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

class GameState:
    def __init__(self):
        self.player_x = 450
        self.player_y = 300
        self.player_angle = 0
        self.bullets = []
        self.enemies = []
        self.score = 0
        self.game_state = "playing"
        self.shoot_cooldown = 0
        self.enemy_spawn_timer = 0

game = GameState()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('player_move')
def handle_player_move(data):
    if game.game_state == "playing":
        game.player_x = max(37.5, min(862.5, data['x']))
        game.player_y = max(37.5, min(562.5, data['y']))
        game.player_angle = data['angle']

@socketio.on('shoot')
def handle_shoot():
    if game.game_state == "playing" and game.shoot_cooldown <= 0:
        bullet_x = game.player_x + math.cos(math.radians(game.player_angle)) * 75
        bullet_y = game.player_y + math.sin(math.radians(game.player_angle)) * 75
        game.bullets.append({
            'x': bullet_x,
            'y': bullet_y,
            'angle': game.player_angle,
            'id': len(game.bullets)
        })
        game.shoot_cooldown = 0.3

@socketio.on('restart_game')
def handle_restart():
    game.player_x = 450
    game.player_y = 300
    game.player_angle = 0
    game.bullets = []
    game.enemies = []
    game.score = 0
    game.game_state = "playing"
    game.shoot_cooldown = 0
    game.enemy_spawn_timer = 0

def game_loop():
    while True:
        if game.game_state == "playing":
            # Update cooldowns
            game.shoot_cooldown = max(0, game.shoot_cooldown - 0.016)
            game.enemy_spawn_timer += 0.016
            
            # Spawn enemies
            if game.enemy_spawn_timer >= 1:
                side = random.choice(['top', 'bottom', 'left', 'right'])
                if side == 'top':
                    x, y = random.randint(0, 900), 620
                elif side == 'right':
                    x, y = 920, random.randint(0, 600)
                elif side == 'bottom':
                    x, y = random.randint(0, 900), -20
                else:
                    x, y = -20, random.randint(0, 600)
                
                game.enemies.append({
                    'x': x, 'y': y, 'angle': 0,
                    'speed': random.uniform(1, 3),
                    'id': len(game.enemies)
                })
                game.enemy_spawn_timer = 0
            
            # Update bullets
            for bullet in game.bullets[:]:
                bullet['x'] += math.cos(math.radians(bullet['angle'])) * 10
                bullet['y'] += math.sin(math.radians(bullet['angle'])) * 10
                if bullet['x'] < 0 or bullet['x'] > 900 or bullet['y'] < 0 or bullet['y'] > 600:
                    game.bullets.remove(bullet)
            
            # Update enemies
            for enemy in game.enemies:
                dx = game.player_x - enemy['x']
                dy = game.player_y - enemy['y']
                enemy['angle'] = math.degrees(math.atan2(dy, dx))
                enemy['x'] += math.cos(math.radians(enemy['angle'])) * enemy['speed']
                enemy['y'] += math.sin(math.radians(enemy['angle'])) * enemy['speed']
            
            # Check collisions
            for bullet in game.bullets[:]:
                for enemy in game.enemies[:]:
                    if math.sqrt((bullet['x'] - enemy['x'])**2 + (bullet['y'] - enemy['y'])**2) < 75:
                        game.bullets.remove(bullet)
                        game.enemies.remove(enemy)
                        game.score += 10
                        break
            
            # Check player-enemy collision
            for enemy in game.enemies:
                if math.sqrt((enemy['x'] - game.player_x)**2 + (enemy['y'] - game.player_y)**2) < 112.5:
                    game.game_state = "lost"
                    break
            
            # Check win condition
            if game.score >= 100:
                game.game_state = "won"
        
        # Send game state to clients
        socketio.emit('game_update', {
            'player': {'x': game.player_x, 'y': game.player_y, 'angle': game.player_angle},
            'bullets': game.bullets,
            'enemies': game.enemies,
            'score': game.score,
            'game_state': game.game_state
        })
        
        time.sleep(0.016)  # ~60 FPS

if __name__ == '__main__':
    threading.Thread(target=game_loop, daemon=True).start()
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)