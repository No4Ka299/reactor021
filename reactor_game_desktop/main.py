import pygame
import sys
import random
import math
from enum import Enum

# Initialize pygame
pygame.init()
try:
    pygame.mixer.init()
except:
    print("Audio initialization failed - running without sound")

# Constants
SIZE = 7
TOTAL_MOVES = 14
CELL_SIZE = 60
GRID_MARGIN_X = 50
GRID_MARGIN_Y = 150
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700

# Colors
BACKGROUND = (13, 13, 26)
GRID_BG = (20, 20, 36, 100)
TEXT_COLOR = (255, 255, 255)
PLAYER1_COLOR = (30, 58, 138)  # Blue
PLAYER2_COLOR = (153, 27, 27)   # Red
PLAYER1_HIGHLIGHT = (37, 99, 235)  # Lighter blue
PLAYER2_HIGHLIGHT = (220, 38, 38)  # Lighter red
EMPTY_CELL = (26, 26, 46)
GRID_LINES = (100, 100, 150)
BUTTON_COLOR = (77, 238, 234)
BUTTON_HOVER = (107, 248, 244)
BUTTON_TEXT = (0, 0, 0)
STATUS_BG = (30, 30, 46)

# Game states
class GameState(Enum):
    MENU = 1
    TOSSED = 2
    PLAYING = 3
    GAME_OVER = 4
    RATING = 5

class ReactorGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("REACTOR - Desktop Version")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 48)
        self.button_font = pygame.font.SysFont(None, 32)
        self.status_font = pygame.font.SysFont(None, 32)
        self.score_font = pygame.font.SysFont(None, 28)
        
        self.reset_game()
        self.game_state = GameState.MENU
        self.dice_value = "?"
        self.dice_animation = False
        self.dice_animation_start = 0
        
        # Button rectangles
        self.start_button = pygame.Rect(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2, 200, 50)
        self.toss_button = pygame.Rect(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 80, 200, 50)
        self.rating_button = pygame.Rect(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 + 160, 200, 50)
        self.play_again_button = pygame.Rect(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT - 100, 200, 50)
        self.back_button = pygame.Rect(20, 20, 100, 40)
        
        # Rating division buttons
        self.silver_button = pygame.Rect(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 - 80, 300, 60)
        self.gold_button = pygame.Rect(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 + 40, 300, 60)
        self.platinum_button = pygame.Rect(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2 + 160, 300, 60)
        
        # Audio (simplified - we'll use pygame.mixer for sound effects)
        self.sounds = {}
        self.audio_available = pygame.mixer.get_init() is not None
        
    def reset_game(self):
        self.board = [[0 for _ in range(SIZE)] for _ in range(SIZE)]
        self.reactors = [[False for _ in range(SIZE)] for _ in range(SIZE)]
        self.move_count = 0
        self.game_active = True
        self.current_player = 'human'  # Will be set after toss
        self.winner = None
        self.player_score = 0
        self.bot_score = 0
        
        # Rating system variables
        self.rating_division = None
        self.rating_change = 0
        self.ratings = {'silver': 1000, 'gold': 1300, 'platinum': 1600}
        
    def draw_gradient_rect(self, rect, color1, color2, vertical=True):
        """Draw a rectangle with gradient fill"""
        if vertical:
            for y in range(rect.height):
                ratio = y / rect.height
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                pygame.draw.line(self.screen, (r, g, b), (rect.left, rect.top + y), (rect.right, rect.top + y))
        else:
            for x in range(rect.width):
                ratio = x / rect.width
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                pygame.draw.line(self.screen, (r, g, b), (rect.left + x, rect.top), (rect.left + x, rect.bottom))

    def draw_button(self, rect, text, hover=False):
        color = BUTTON_HOVER if hover else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, rect, border_radius=12)
        pygame.draw.rect(self.screen, (200, 200, 200), rect, 2, border_radius=12)
        
        text_surf = self.button_font.render(text, True, BUTTON_TEXT)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def draw_text(self, text, font, color, x, y, center=True):
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        self.screen.blit(text_surf, text_rect)

    def draw_grid(self):
        for r in range(SIZE):
            for c in range(SIZE):
                x = GRID_MARGIN_X + c * CELL_SIZE
                y = GRID_MARGIN_Y + r * CELL_SIZE
                
                # Draw cell background
                cell_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                
                if self.board[r][c] == 1:  # Player 1
                    color = PLAYER1_HIGHLIGHT if self.reactors[r][c] else PLAYER1_COLOR
                elif self.board[r][c] == 2:  # Player 2 (bot)
                    color = PLAYER2_HIGHLIGHT if self.reactors[r][c] else PLAYER2_COLOR
                else:  # Empty
                    color = EMPTY_CELL
                
                pygame.draw.rect(self.screen, color, cell_rect)
                pygame.draw.rect(self.screen, GRID_LINES, cell_rect, 1)
                
                # Draw reactor symbol if present
                if self.reactors[r][c]:
                    reactor_x = x + CELL_SIZE // 2
                    reactor_y = y + CELL_SIZE // 2
                    pygame.draw.circle(self.screen, (255, 255, 255), (reactor_x, reactor_y), 8)

    def activate_reactor(self, row, col, player):
        self.reactors[row][col] = True
        self.board[row][col] = player
        
        # Activate adjacent cells
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < SIZE and 0 <= nc < SIZE:
                self.board[nr][nc] = player

    def player_move(self, row, col):
        if not self.game_active or self.current_player != 'human' or self.board[row][col] != 0:
            return False
            
        self.activate_reactor(row, col, 1)
        self.move_count += 1
        
        if self.move_count >= TOTAL_MOVES:
            self.end_game()
        else:
            self.current_player = 'bot'
            # Bot will move in the game loop
            
        return True

    def bot_move(self):
        if not self.game_active or self.current_player != 'bot':
            return

        # Bot AI logic (simplified from the web version)
        phase = 'early' if self.move_count < 5 else 'mid' if self.move_count < 10 else 'late'
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for r in range(SIZE):
            for c in range(SIZE):
                if self.board[r][c] != 0:
                    continue

                base_value = 0
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < SIZE and 0 <= nc < SIZE:
                        if self.board[nr][nc] == 1:  # Player cell
                            base_value += 10
                        elif self.board[nr][nc] == 0:  # Empty cell
                            base_value += 4
                        else:  # Bot cell
                            base_value += 1

                # Center preference in early game
                if phase == 'early' and 2 <= r <= 4 and 2 <= c <= 4:
                    base_value += 4

                # Threat evaluation
                threat_value = 0
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < SIZE and 0 <= nc < SIZE and self.board[nr][nc] == 1:
                        future_damage = 0
                        for dr2, dc2 in directions:
                            nnr, nnc = nr + dr2, nc + dc2
                            if 0 <= nnr < SIZE and 0 <= nnc < SIZE:
                                if self.board[nnr][nnc] == 2:
                                    future_damage += 1
                        threat_value = max(threat_value, future_damage * 5)

                total_value = base_value + threat_value
                total_value += (random.random() - 0.5) * 2  # Small randomness

                moves.append((r, c, total_value))

        if moves:
            # Sort by value and pick one of the top moves
            moves.sort(key=lambda x: x[2], reverse=True)
            top_moves = moves[:3] if len(moves) >= 3 else moves
            chosen_r, chosen_c, _ = random.choice(top_moves)
            
            self.activate_reactor(chosen_r, chosen_c, 2)
            self.move_count += 1

            if self.move_count >= TOTAL_MOVES:
                self.end_game()
            else:
                self.current_player = 'human'

    def rating_bot_move(self):
        if not self.game_active or self.current_player != 'bot':
            return

        # Adjust difficulty based on division
        difficulty_factor = 1.0
        if self.rating_division == 'silver':
            difficulty_factor = 0.8
        elif self.rating_division == 'gold':
            difficulty_factor = 1.0
        elif self.rating_division == 'platinum':
            difficulty_factor = 1.3

        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for r in range(SIZE):
            for c in range(SIZE):
                if self.board[r][c] != 0:
                    continue

                base_value = 0
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < SIZE and 0 <= nc < SIZE:
                        if self.board[nr][nc] == 1:
                            base_value += 10
                        elif self.board[nr][nc] == 0:
                            base_value += 4
                        else:
                            base_value += 1

                # Apply difficulty factor
                total_value = base_value * difficulty_factor
                total_value += (random.random() - 0.5) * (2 / difficulty_factor)

                moves.append((r, c, total_value))

        if moves:
            moves.sort(key=lambda x: x[2], reverse=True)
            
            # Choose move based on division difficulty
            if self.rating_division == 'platinum':
                # Platinum bot almost always chooses best move
                chosen_r, chosen_c, _ = moves[0]
            elif self.rating_division == 'gold':
                # Gold bot chooses from top 2
                top_moves = moves[:2]
                chosen_r, chosen_c, _ = random.choice(top_moves)
            else:
                # Silver bot chooses from top 3
                top_moves = moves[:3]
                chosen_r, chosen_c, _ = random.choice(top_moves)
            
            self.activate_reactor(chosen_r, chosen_c, 2)
            self.move_count += 1

            if self.move_count >= TOTAL_MOVES:
                self.end_rating_game()
            else:
                self.current_player = 'human'

    def end_game(self):
        self.game_active = False
        self.calculate_scores()
        
        if self.player_score > self.bot_score:
            self.winner = 'human'
        elif self.bot_score > self.player_score:
            self.winner = 'bot'
        else:
            self.winner = 'draw'

    def end_rating_game(self):
        self.game_active = False
        self.calculate_scores()
        
        rating_change = 0
        if self.player_score > self.bot_score:
            # Win - gain rating
            if self.rating_division == 'silver':
                rating_change = 10
            elif self.rating_division == 'gold':
                rating_change = 15
            else:  # platinum
                rating_change = 20
            self.ratings[self.rating_division] += rating_change
            self.winner = 'human'
        elif self.bot_score > self.player_score:
            # Loss - lose rating
            if self.rating_division == 'silver':
                rating_change = -8
            elif self.rating_division == 'gold':
                rating_change = -12
            else:  # platinum
                rating_change = -15
            self.ratings[self.rating_division] += rating_change
            self.winner = 'bot'
        else:
            self.winner = 'draw'
            
        self.rating_change = rating_change
        self.check_division_change()

    def check_division_change(self):
        current_rating = self.ratings[self.rating_division]
        
        if self.rating_division == 'silver' and current_rating >= 1200:
            self.rating_division = 'gold'
        elif self.rating_division == 'gold' and current_rating >= 1500:
            self.rating_division = 'platinum'
        elif self.rating_division == 'gold' and current_rating < 1100:
            self.rating_division = 'silver'
        elif self.rating_division == 'platinum' and current_rating < 1400:
            self.rating_division = 'gold'

    def calculate_scores(self):
        self.player_score = sum(row.count(1) for row in self.board)
        self.bot_score = sum(row.count(2) for row in self.board)

    def start_toss(self):
        self.dice_animation = True
        self.dice_animation_start = pygame.time.get_ticks()
        
        # Randomly decide who goes first after animation
        def complete_toss():
            first_player = random.choice(['human', 'bot'])
            self.current_player = first_player
            self.game_state = GameState.PLAYING

    def draw_menu(self):
        # Draw background
        self.screen.fill(BACKGROUND)
        
        # Draw title
        title = self.title_font.render("REACTOR", True, BUTTON_COLOR)
        self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 80))
        
        subtitle = self.font.render("Стратегическая игра, где каждый ход решает исход битвы за контроль!", True, (200, 200, 200))
        self.screen.blit(subtitle, (WINDOW_WIDTH//2 - subtitle.get_width()//2, 140))
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        start_hover = self.start_button.collidepoint(mouse_pos)
        toss_hover = self.toss_button.collidepoint(mouse_pos)
        rating_hover = self.rating_button.collidepoint(mouse_pos)
        
        self.draw_button(self.start_button, "Новая Игра", start_hover)
        self.draw_button(self.toss_button, "Подбросить Кубик", toss_hover)
        self.draw_button(self.rating_button, "Рейтинговый Режим", rating_hover)
        
        # Draw game info
        info_y = WINDOW_HEIGHT - 100
        info1 = self.font.render("Каждый реактор (●) перекрашивает соседние клетки.", True, (180, 180, 180))
        info2 = self.font.render("После 14 ходов побеждает контролирующий больше.", True, (180, 180, 180))
        self.screen.blit(info1, (WINDOW_WIDTH//2 - info1.get_width()//2, info_y))
        self.screen.blit(info2, (WINDOW_WIDTH//2 - info2.get_width()//2, info_y + 30))

    def draw_toss_screen(self):
        self.screen.fill(BACKGROUND)
        
        title = self.title_font.render("REACTOR", True, BUTTON_COLOR)
        self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 80))
        
        subtitle = self.font.render("Кто начнет первым?", True, (200, 200, 200))
        self.screen.blit(subtitle, (WINDOW_WIDTH//2 - subtitle.get_width()//2, 150))
        
        # Draw dice
        dice_rect = pygame.Rect(WINDOW_WIDTH//2 - 50, 220, 100, 100)
        pygame.draw.rect(self.screen, (30, 30, 46), dice_rect, border_radius=20)
        pygame.draw.rect(self.screen, BUTTON_COLOR, dice_rect, 3, border_radius=20)
        
        # Animate dice if needed
        if self.dice_animation:
            elapsed = pygame.time.get_ticks() - self.dice_animation_start
            if elapsed < 2200:
                # Animate with random values
                frame = (elapsed // 200) % 10
                self.dice_value = random.choice(['?', '🎲', '👤', '🤖'])
            else:
                # Set final value and complete toss
                self.dice_value = '👤' if self.current_player == 'human' else '🤖'
                self.dice_animation = False
                self.game_state = GameState.PLAYING
        else:
            # Show the final result
            self.dice_value = '👤' if self.current_player == 'human' else '🤖'
        
        dice_text = self.title_font.render(str(self.dice_value), True, 
                                          PLAYER1_HIGHLIGHT if self.current_player == 'human' else PLAYER2_HIGHLIGHT)
        self.screen.blit(dice_text, (dice_rect.centerx - dice_text.get_width()//2, 
                                    dice_rect.centery - dice_text.get_height()//2))
        
        # Back button
        mouse_pos = pygame.mouse.get_pos()
        back_hover = self.back_button.collidepoint(mouse_pos)
        self.draw_button(self.back_button, "Назад", back_hover)

    def draw_rating_screen(self):
        self.screen.fill(BACKGROUND)
        
        title = self.title_font.render("РЕЙТИНГОВЫЙ РЕЖИМ", True, BUTTON_COLOR)
        self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 50))
        
        subtitle = self.font.render("Выберите дивизион для игры с ботом", True, (200, 200, 200))
        self.screen.blit(subtitle, (WINDOW_WIDTH//2 - subtitle.get_width()//2, 120))
        
        # Draw division cards
        mouse_pos = pygame.mouse.get_pos()
        
        # Silver division
        silver_hover = self.silver_button.collidepoint(mouse_pos)
        color1, color2 = (192, 192, 192), (160, 160, 160)  # Silver colors
        pygame.draw.rect(self.screen, EMPTY_CELL, self.silver_button, border_radius=15)
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.silver_button, 2, border_radius=15)
        if silver_hover:
            pygame.draw.rect(self.screen, (100, 100, 120), self.silver_button, 2, border_radius=15)
        
        silver_title = self.button_font.render("СЕРЕБРО", True, 
                                              (color1[0], color1[1], color1[2]) if not silver_hover else (200, 200, 200))
        self.screen.blit(silver_title, (self.silver_button.centerx - silver_title.get_width()//2, 
                                       self.silver_button.top + 15))
        
        rating_text = self.font.render(f"Рейтинг: {self.ratings['silver']}", True, (200, 200, 200))
        self.screen.blit(rating_text, (self.silver_button.centerx - rating_text.get_width()//2, 
                                      self.silver_button.top + 50))
        
        info_text = self.font.render("Уровень бота: Средний", True, (150, 150, 150))
        self.screen.blit(info_text, (self.silver_button.centerx - info_text.get_width()//2, 
                                    self.silver_button.top + 75))
        
        # Gold division
        gold_hover = self.gold_button.collidepoint(mouse_pos)
        color1, color2 = (255, 215, 0), (218, 165, 32)  # Gold colors
        pygame.draw.rect(self.screen, EMPTY_CELL, self.gold_button, border_radius=15)
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.gold_button, 2, border_radius=15)
        if gold_hover:
            pygame.draw.rect(self.screen, (150, 130, 50), self.gold_button, 2, border_radius=15)
        
        gold_title = self.button_font.render("ЗОЛОТО", True, 
                                            (color1[0], color1[1], color1[2]) if not gold_hover else (255, 255, 200))
        self.screen.blit(gold_title, (self.gold_button.centerx - gold_title.get_width()//2, 
                                     self.gold_button.top + 15))
        
        rating_text = self.font.render(f"Рейтинг: {self.ratings['gold']}", True, (200, 200, 200))
        self.screen.blit(rating_text, (self.gold_button.centerx - rating_text.get_width()//2, 
                                      self.gold_button.top + 50))
        
        info_text = self.font.render("Уровень бота: Высокий", True, (150, 150, 150))
        self.screen.blit(info_text, (self.gold_button.centerx - info_text.get_width()//2, 
                                    self.gold_button.top + 75))
        
        # Platinum division
        platinum_hover = self.platinum_button.collidepoint(mouse_pos)
        color1, color2 = (229, 228, 226), (201, 201, 201)  # Platinum colors
        pygame.draw.rect(self.screen, EMPTY_CELL, self.platinum_button, border_radius=15)
        pygame.draw.rect(self.screen, BUTTON_COLOR, self.platinum_button, 2, border_radius=15)
        if platinum_hover:
            pygame.draw.rect(self.screen, (150, 150, 160), self.platinum_button, 2, border_radius=15)
        
        platinum_title = self.button_font.render("ПЛАТИНА", True, 
                                                (color1[0], color1[1], color1[2]) if not platinum_hover else (230, 230, 240))
        self.screen.blit(platinum_title, (self.platinum_button.centerx - platinum_title.get_width()//2, 
                                         self.platinum_button.top + 15))
        
        rating_text = self.font.render(f"Рейтинг: {self.ratings['platinum']}", True, (200, 200, 200))
        self.screen.blit(rating_text, (self.platinum_button.centerx - rating_text.get_width()//2, 
                                      self.platinum_button.top + 50))
        
        info_text = self.font.render("Уровень бота: Эксперт", True, (150, 150, 150))
        self.screen.blit(info_text, (self.platinum_button.centerx - info_text.get_width()//2, 
                                    self.platinum_button.top + 75))
        
        # Back button
        back_hover = self.back_button.collidepoint(mouse_pos)
        self.draw_button(self.back_button, "Назад", back_hover)

    def draw_game(self):
        self.screen.fill(BACKGROUND)
        
        # Draw title
        title = self.title_font.render("REACTOR", True, BUTTON_COLOR)
        self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 20))
        
        # Draw scores
        score_bg = pygame.Rect(50, 80, 200, 50)
        pygame.draw.rect(self.screen, STATUS_BG, score_bg, border_radius=12)
        pygame.draw.rect(self.screen, BUTTON_COLOR, score_bg, 2, border_radius=12)
        
        player_score_text = self.score_font.render(f"Ты: {self.player_score}", True, PLAYER1_HIGHLIGHT)
        self.screen.blit(player_score_text, (score_bg.centerx - 60, score_bg.centery - player_score_text.get_height()//2))
        
        bot_score_text = self.score_font.render(f"Бот: {self.bot_score}", True, PLAYER2_HIGHLIGHT)
        self.screen.blit(bot_score_text, (score_bg.centerx + 60, score_bg.centery - bot_score_text.get_height()//2))
        
        # Draw status
        status_bg = pygame.Rect(WINDOW_WIDTH//2 - 200, 80, 400, 50)
        pygame.draw.rect(self.screen, STATUS_BG, status_bg, border_radius=12)
        pygame.draw.rect(self.screen, BUTTON_COLOR, status_bg, 2, border_radius=12)
        
        if self.game_active:
            if self.current_player == 'human':
                status_text = self.status_font.render("Твой ход — поставь реактор", True, PLAYER1_HIGHLIGHT)
            else:
                status_text = self.status_font.render("Ход бота...", True, PLAYER2_HIGHLIGHT)
        else:
            if self.winner == 'human':
                status_text = self.status_font.render("🏆 Победа!", True, PLAYER1_HIGHLIGHT)
            elif self.winner == 'bot':
                status_text = self.status_font.render("💔 Поражение.", True, PLAYER2_HIGHLIGHT)
            else:
                status_text = self.status_font.render("🤝 Ничья!", True, (200, 200, 100))
        
        self.screen.blit(status_text, (status_bg.centerx - status_text.get_width()//2, 
                                      status_bg.centery - status_text.get_height()//2))
        
        # Draw grid
        self.draw_grid()
        
        # Draw game info
        info_y = GRID_MARGIN_Y + SIZE * CELL_SIZE + 20
        info1 = self.font.render("Каждый реактор (●) перекрашивает соседние клетки.", True, (180, 180, 180))
        info2 = self.font.render("После 14 ходов побеждает контролирующий больше.", True, (180, 180, 180))
        self.screen.blit(info1, (WINDOW_WIDTH//2 - info1.get_width()//2, info_y))
        self.screen.blit(info2, (WINDOW_WIDTH//2 - info2.get_width()//2, info_y + 30))
        
        # Draw play again button if game is over
        if not self.game_active:
            mouse_pos = pygame.mouse.get_pos()
            play_again_hover = self.play_again_button.collidepoint(mouse_pos)
            self.draw_button(self.play_again_button, "Новая Игра", play_again_hover)

    def draw_rating_game(self):
        self.screen.fill(BACKGROUND)
        
        # Draw title with division
        title_text = f"REACTOR - {self.rating_division.upper()}"
        title = self.title_font.render(title_text, True, BUTTON_COLOR)
        self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 20))
        
        # Draw division info
        division_info = self.font.render(f"Дивизион: {self.rating_division.capitalize()}", True, (200, 200, 200))
        self.screen.blit(division_info, (WINDOW_WIDTH//2 - division_info.get_width()//2, 70))
        
        # Draw scores
        score_bg = pygame.Rect(50, 100, 200, 50)
        pygame.draw.rect(self.screen, STATUS_BG, score_bg, border_radius=12)
        pygame.draw.rect(self.screen, BUTTON_COLOR, score_bg, 2, border_radius=12)
        
        player_score_text = self.score_font.render(f"Ты: {self.player_score}", True, PLAYER1_HIGHLIGHT)
        self.screen.blit(player_score_text, (score_bg.centerx - 60, score_bg.centery - player_score_text.get_height()//2))
        
        bot_score_text = self.score_font.render(f"Бот: {self.bot_score}", True, PLAYER2_HIGHLIGHT)
        self.screen.blit(bot_score_text, (score_bg.centerx + 60, score_bg.centery - bot_score_text.get_height()//2))
        
        # Draw rating
        rating_bg = pygame.Rect(WINDOW_WIDTH//2 - 150, 100, 300, 50)
        pygame.draw.rect(self.screen, STATUS_BG, rating_bg, border_radius=12)
        pygame.draw.rect(self.screen, BUTTON_COLOR, rating_bg, 2, border_radius=12)
        
        rating_text = self.score_font.render(f"Рейтинг: {self.ratings[self.rating_division]}", True, (200, 200, 200))
        self.screen.blit(rating_text, (rating_bg.centerx - rating_text.get_width()//2, 
                                      rating_bg.centery - rating_text.get_height()//2))
        
        # Draw status
        status_bg = pygame.Rect(WINDOW_WIDTH//2 - 200, 160, 400, 50)
        pygame.draw.rect(self.screen, STATUS_BG, status_bg, border_radius=12)
        pygame.draw.rect(self.screen, BUTTON_COLOR, status_bg, 2, border_radius=12)
        
        if self.game_active:
            if self.current_player == 'human':
                status_text = self.status_font.render("Твой ход — поставь реактор", True, PLAYER1_HIGHLIGHT)
            else:
                status_text = self.status_font.render("Ход бота...", True, PLAYER2_HIGHLIGHT)
        else:
            if self.winner == 'human':
                status_text = self.status_font.render("🏆 Победа!", True, PLAYER1_HIGHLIGHT)
                if self.rating_change > 0:
                    change_text = f"(+{self.rating_change})"
                else:
                    change_text = f"({self.rating_change})"
                change_surf = self.status_font.render(change_text, True, (100, 255, 100))
                self.screen.blit(change_surf, (status_bg.right - 80, status_bg.centery - change_surf.get_height()//2))
            elif self.winner == 'bot':
                status_text = self.status_font.render("💔 Поражение.", True, PLAYER2_HIGHLIGHT)
                if self.rating_change < 0:
                    change_text = f"({self.rating_change})"
                    change_surf = self.status_font.render(change_text, True, (255, 100, 100))
                    self.screen.blit(change_surf, (status_bg.right - 80, status_bg.centery - change_surf.get_height()//2))
            else:
                status_text = self.status_font.render("🤝 Ничья!", True, (200, 200, 100))
        
        self.screen.blit(status_text, (status_bg.centerx - status_text.get_width()//2, 
                                      status_bg.centery - status_text.get_height()//2))
        
        # Draw grid
        self.draw_grid()
        
        # Draw game info
        info_y = GRID_MARGIN_Y + SIZE * CELL_SIZE + 20
        info1 = self.font.render("Каждый реактор (●) перекрашивает соседние клетки.", True, (180, 180, 180))
        info2 = self.font.render("После 14 ходов побеждает контролирующий больше.", True, (180, 180, 180))
        self.screen.blit(info1, (WINDOW_WIDTH//2 - info1.get_width()//2, info_y))
        self.screen.blit(info2, (WINDOW_WIDTH//2 - info2.get_width()//2, info_y + 30))
        
        # Draw play again button if game is over
        if not self.game_active:
            mouse_pos = pygame.mouse.get_pos()
            play_again_hover = self.play_again_button.collidepoint(mouse_pos)
            self.draw_button(self.play_again_button, "Новая Игра", play_again_hover)

    def run(self):
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if self.game_state == GameState.MENU:
                            if self.start_button.collidepoint(event.pos):
                                # Start game with human going first
                                self.current_player = 'human'
                                self.game_state = GameState.PLAYING
                                self.reset_game()
                            elif self.toss_button.collidepoint(event.pos):
                                self.game_state = GameState.TOSSED
                                self.reset_game()
                                self.start_toss()
                            elif self.rating_button.collidepoint(event.pos):
                                self.game_state = GameState.RATING
                        elif self.game_state == GameState.TOSSED:
                            if self.back_button.collidepoint(event.pos):
                                self.game_state = GameState.MENU
                        elif self.game_state == GameState.RATING:
                            if self.silver_button.collidepoint(event.pos):
                                self.rating_division = 'silver'
                                self.game_state = GameState.PLAYING
                                self.reset_game()
                                self.current_player = 'human'
                            elif self.gold_button.collidepoint(event.pos):
                                self.rating_division = 'gold'
                                self.game_state = GameState.PLAYING
                                self.reset_game()
                                self.current_player = 'human'
                            elif self.platinum_button.collidepoint(event.pos):
                                self.rating_division = 'platinum'
                                self.game_state = GameState.PLAYING
                                self.reset_game()
                                self.current_player = 'human'
                            elif self.back_button.collidepoint(event.pos):
                                self.game_state = GameState.MENU
                        elif self.game_state == GameState.PLAYING:
                            if not self.game_active and self.play_again_button.collidepoint(event.pos):
                                if self.rating_division:
                                    self.game_state = GameState.RATING
                                else:
                                    self.game_state = GameState.MENU
                            elif self.game_active and self.current_player == 'human':
                                # Check if click is on grid
                                grid_x = event.pos[0] - GRID_MARGIN_X
                                grid_y = event.pos[1] - GRID_MARGIN_Y
                                
                                if 0 <= grid_x < SIZE * CELL_SIZE and 0 <= grid_y < SIZE * CELL_SIZE:
                                    col = grid_x // CELL_SIZE
                                    row = grid_y // CELL_SIZE
                                    
                                    if 0 <= row < SIZE and 0 <= col < SIZE:
                                        self.player_move(row, col)
                        elif self.game_state == GameState.GAME_OVER:
                            if self.play_again_button.collidepoint(event.pos):
                                self.game_state = GameState.MENU
                            elif self.back_button.collidepoint(event.pos):
                                self.game_state = GameState.MENU
            
            # Update game state
            if self.game_state == GameState.PLAYING and self.game_active and self.current_player == 'bot':
                pygame.time.wait(800)  # Delay for bot move
                if self.rating_division:
                    self.rating_bot_move()
                else:
                    self.bot_move()
            
            # Draw everything based on game state
            if self.game_state == GameState.MENU:
                self.draw_menu()
            elif self.game_state == GameState.TOSSED:
                self.draw_toss_screen()
            elif self.game_state == GameState.RATING:
                self.draw_rating_screen()
            elif self.game_state == GameState.PLAYING:
                if self.rating_division:
                    self.calculate_scores()
                    self.draw_rating_game()
                else:
                    self.calculate_scores()
                    self.draw_game()
            
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ReactorGame()
    game.run()