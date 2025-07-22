import sys
import random
import time
import threading
import pygame

import csv
import os

def update_scoreboard(filename: str, players: list[str], score: list[int]):
    import csv
    import os

    players = list(players)
    score = list(score)

    if not os.path.exists(filename):
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([""] + players)
            for p in players:
                writer.writerow([p] + [""] * len(players))

    with open(filename, 'r', newline='') as f:
        reader = list(csv.reader(f))

    if not reader or not reader[0]:
        raise ValueError("CSV file is malformed or empty")

    headers = reader[0]
    rows_dict = {row[0]: row for row in reader[1:]}

    for player in players:
        if player not in headers:
            headers.append(player)
            for row in rows_dict.values():
                row.append("")
            new_row = [player] + [""] * (len(headers) - 1)
            rows_dict[player] = new_row

    full_rows = [headers]
    for row_name in headers[1:]:
        if row_name not in rows_dict:
            rows_dict[row_name] = [row_name] + [""] * (len(headers) - 1)
        else:
            row = rows_dict[row_name]
            if len(row) < len(headers):
                row += [""] * (len(headers) - len(row))
            rows_dict[row_name] = row
        full_rows.append(rows_dict[row_name])

    p1, p2 = players
    i = headers.index(p1)
    j = headers.index(p2)

    cell_val = rows_dict[p1][j]
    if cell_val:
        try:
            existing = eval(cell_val)
            new_score = [int(existing[0]) + int(score[0]), int(existing[1]) + int(score[1])]
        except Exception:
            new_score = score
    else:
        new_score = score

    rows_dict[p1][j] = str(new_score)

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row_name in headers[1:]:
            writer.writerow(rows_dict[row_name])




def point_inside_polygon(polygon, pos, surface_size, flip=False):
    """
    Checks if the mouse is inside a polygon drawn onto a surface.

    Args:
        polygon: List of points relative to surface.
        pos: Position on screen where the surface is rendered.
        surface_size: (width, height) of the surface.
        flip: Whether the surface was rotated 180° before rendering.

    Returns:
        True if mouse is inside polygon, False otherwise.
    """
    try:
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Create a temporary surface
        surf = pygame.Surface(surface_size, pygame.SRCALPHA)
        pygame.draw.polygon(surf, (255, 255, 255), polygon)

        # Apply flip if needed
        if flip:
            surf = pygame.transform.rotate(surf, 180)

            # Adjust mouse position to rotated local coordinates
            local_x = mouse_x - pos[0]
            local_y = mouse_y - pos[1]
            local_x = surface_size[0] - local_x
            local_y = surface_size[1] - local_y
        else:
            local_x = mouse_x - pos[0]
            local_y = mouse_y - pos[1]

        # Quick bounds check
        if not (0 <= local_x < surface_size[0] and 0 <= local_y < surface_size[1]):
            return False

        # Create mask and test
        mask = pygame.mask.from_surface(surf)
        return mask.get_at((int(local_x), int(local_y))) == 1

    except Exception:
        return False



def draw_text_with_outline(surface, text, font, pos, text_color, outline_color, outline_thickness=1):
    x, y = pos
    base = font.render(text, True, text_color)
    outline = font.render(text, True, outline_color)

    for dx in range(-outline_thickness, outline_thickness + 1):
        for dy in range(-outline_thickness, outline_thickness + 1):
            if dx != 0 or dy != 0:
                surface.blit(outline, (x + dx, y + dy))

    surface.blit(base, (x, y))

class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.dur = len(self.images) * img_dur / 60
        self.frame = 0
    
    def remainin_dur(self):
        return self.dur - (self.frame*self.img_duration/60)

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)

    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True

    def img(self):
        return self.images[int(self.frame / self.img_duration)]


class Dice:
    def __init__(self, game, color, pos):
        self.game = game
        self.color = color
        self.pos = pos
        self.rolled = False
        self.value = 1
        self.state = 0
        self.doubled = False
        self.set_anim(1)
        self.size = self.anim.img().get_size()
    
    def set_anim(self, anim):
        if anim != self.state:
            self.state = anim
            self.anim = self.game.assets[f"dice_{self.color}_{self.state}"].copy()

    def roll(self):
        if not self.rolled:
            self.value = random.randint(1, 6)
            self.rolled = True
            self.set_anim('roll')
            if self.game.audio_on:
                self.game.dice_sound.play()
            threading.Timer(self.anim.dur, lambda: self.set_anim(self.value)).start()
    
    def reset(self):
        self.rolled = False
        self.doubled = False

    def rect(self):
        return pygame.Rect(*self.pos, *self.size)
    
    def render(self, screen):
        self.anim.update()
        screen.blit(self.anim.img(), self.pos)
        if self.value not in self.game.moves_left and self.game.current_player:
            s = pygame.Surface([self.size[0] - 12, self.size[1] - 12])
            s.set_alpha(125)
            screen.blit(s, [self.pos[0] + 5, self.pos[1] + 5])
        if self.doubled:
            screen.blit(self.anim.img(), (self.pos[0] + (self.size[0] + 10) * (-1 if self.color == 'white' else 1), self.pos[1]))


class Game:
    def __init__(self, menu, player_names, points=5, score=[0,0], audio_on=True):
        # Initialize Pygame
        pygame.init()

        # Screen dimensions
        self.SCREEN_WIDTH = 600
        self.SCREEN_HEIGHT = 600
        self.POLYGON_COLOR = (0,0,125)
        self.menu = menu
        self.game_over = False
        self.winner_decided = False

        # Colors
        self.GREEN = (0, 128, 0)
        self.BROWN = (139, 69, 19)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.BLACK = (0, 0, 0)
        self.pieces = [0 for i in range(24)]
        self.piece_rects = [0 for i in range(24)]
        self.pos_value = {0: 2, 11: 5, 16: 3, 18: 5}
        self.turn = 0
        self.last_rolled = 0
        self.score = score

        # Board dimensions
        self.BOARD_WIDTH = 600
        self.BOARD_HEIGHT = 600

        # Triangle dimensions
        self.TRIANGLE_SIZE = 50
        self.TRIANGLE_SPACING = 45.6
        self.player_names = player_names
    
        self.PIECE_SIZE = 28
        self.audio_on = audio_on
        self.click_sound = pygame.mixer.Sound('assets/button.wav')
        self.dice_sound = pygame.mixer.Sound('assets/dice.wav')

        # Dice dimensions
        self.DICE_SIZE = 50

        # Initialize Pygame window
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Backgammon")

        # Game settings
        self.points_to_win = points

        # Assets dictionary (placeholders for now)
        self.assets = {
            "board": pygame.transform.scale(pygame.image.load("assets/board.webp").convert(), self.screen.get_size()),
            "triangle": pygame.Surface((self.TRIANGLE_SIZE, self.TRIANGLE_SIZE)),
            "pawn_white": pygame.image.load("assets/Stone_White.png").convert_alpha(),
            "pawn_black": pygame.image.load("assets/Stone_Black.png").convert_alpha(),
            "dice": pygame.Surface((self.DICE_SIZE, self.DICE_SIZE)),
            'dice_white_1' : Animation([pygame.image.load('assets/digit-1-white.png').convert_alpha()]),
            'dice_white_2' : Animation([pygame.image.load('assets/digit-2-white.png').convert_alpha()]),
            'dice_white_3' : Animation([pygame.image.load('assets/digit-3-white.png').convert_alpha()]),
            'dice_white_4' : Animation([pygame.image.load('assets/digit-4-white.png').convert_alpha()]),
            'dice_white_5' : Animation([pygame.image.load('assets/digit-5-white.png').convert_alpha()]),
            'dice_white_6' : Animation([pygame.image.load('assets/digit-6-white.png').convert_alpha()]),
            'dice_black_1' : Animation([pygame.image.load('assets/digit-1-black.png').convert_alpha()]),
            'dice_black_2' : Animation([pygame.image.load('assets/digit-2-black.png').convert_alpha()]),
            'dice_black_3' : Animation([pygame.image.load('assets/digit-3-black.png').convert_alpha()]),
            'dice_black_4' : Animation([pygame.image.load('assets/digit-4-black.png').convert_alpha()]),
            'dice_black_5' : Animation([pygame.image.load('assets/digit-5-black.png').convert_alpha()]),
            'dice_black_6' : Animation([pygame.image.load('assets/digit-6-black.png').convert_alpha()]),
            'dice_black_roll' : Animation([pygame.image.load('assets/digit-6-black.png').convert_alpha(),pygame.image.load('assets/digit-5-black.png').convert_alpha(),pygame.image.load('assets/digit-4-black.png').convert_alpha(),pygame.image.load('assets/digit-3-black.png').convert_alpha(),pygame.image.load('assets/digit-2-black.png').convert_alpha(),pygame.image.load('assets/digit-1-black.png').convert_alpha()], img_dur=1),
            'dice_white_roll' : Animation([pygame.image.load('assets/digit-6-white.png').convert_alpha(),pygame.image.load('assets/digit-5-white.png').convert_alpha(),pygame.image.load('assets/digit-4-white.png').convert_alpha(),pygame.image.load('assets/digit-3-white.png').convert_alpha(),pygame.image.load('assets/digit-2-white.png').convert_alpha(),pygame.image.load('assets/digit-1-white.png').convert_alpha()], img_dur=1),
        }
        self.dices = [
            Dice(self, 'black', (360 - 60, 270)),
            Dice(self, 'white', (300 - 60, 270)),
            ]
        
        self.current_text = ''
        self.polygon = [(0, 350), (33, 0),(66, 350)]
        self.polygons = [0 for i in range(24)]
        self.polygon_surface_size = (66, 252)
        self.set_polygons()
        self.moves_left = [0 for i in range(4)]
        self.pieces_removed = [0,0]
        
        
        # Game state
        self.current_player = 0
        self.rolled = False
        self.piece_chosen = None
        self.initialize_board()

        # UI elements
        self.font = pygame.font.Font('assets/font.otf', 26)

    def initialize_board(self):
        """
        Initialize the board state.
        Each point on the board is represented by a list of pawns.
        """
        # self.pieces = [x+y for x,y in zip([self.pos_value.get(i, 0) for i in range(24)], [-self.pos_value.get(23-i, 0) for i in range(24)])]
        self.pieces = [-2, 0, 0, 0, 0, 5, 0, 3, 0, 0, 0, -5, 5, 0, 0, 0, -3, 0, -5, 0, 0, 0, 0, 2]
        
   
    def reset_game(self):
        self.pieces_removed = [0, 0]
        self.initialize_board()
        for dice in self.dices:
            dice.reset()
        self.turn = 0
        self.rolled = False
        self.winner_decided = False
        self.moves_left = [0, 0, 0, 0]
        self.current_player = 0

 
    def can_remove_pieces(self, player):
        s = 0
        for i in range(*((0,6) if player == 1 else (18,24))):
            if self.pieces[i] * player > 0:
                s += abs(self.pieces[i])
        return s + self.pieces_removed[player == -1] == 15
                
    
    def legal_moves(self, piece):
        # piece_is_dead is False when the piece moving is a piece on the board ow it refers to the player that owns the piece
        piece_is_dead = self.player_has_dead_pieces(self.current_player)
        if piece_is_dead and not piece in [24, -1]:return []
        moves = []
        for val in self.moves_left:
            if val == 0:continue
            val = (val * (1 if self.current_player < 0 else -1))
            ind = piece + val
            if ind < 0 or ind > 23:
                if self.can_remove_pieces(self.current_player):
                    moves.append(val)
                continue
            if (self.current_player * self.pieces[ind] > 0) or self.pieces[ind] == 0:
                moves.append(val)
            elif abs(self.pieces[ind]) == 1:
                moves.append(val)
        # print(self.pieces[piece])
        return moves
    
    def get_player_pieces(self, player):
        """
        Get the pieces of the specified player.
        """
        return abs(sum([piece for piece in (self.pieces) if piece * player > 0]))

    def player_has_dead_pieces(self, player):
        return self.get_player_pieces(player) + self.pieces_removed[self.current_player == -1] != 15
    
    def get_player_piece_positions(self, player):
        return [i for i, piece in enumerate(self.pieces) if piece * player > 0]

    def get_furthest_piece(self, player):
        positions = self.get_player_piece_positions(player)
        if not positions:
            return None
        return max(positions) if player == 1 else min(positions)
    
    def play_move(self, piece, move):
        # lines below used for debugging 
        # print(self.current_player)
        # print(piece, move)
        # print(self.legal_moves(piece))
        if move not in [piece + move for move in self.legal_moves(piece)] and not self.can_remove_pieces(self.current_player):
            return False
        if self.player_has_dead_pieces(self.current_player):
            if self.pieces[move] == 0 or self.pieces[move] * self.current_player < 0:
                self.pieces[move] = self.current_player
                self.moves_left.remove(abs(piece-move))
                return True
            if self.pieces[move] * self.current_player > 0:
                self.pieces[move] += self.current_player
                self.moves_left.remove(abs(piece-move))
                return True
            else:
                return False
        if self.can_remove_pieces(self.current_player):
            if (move == 24 if self.current_player == -1 else move == -1) and move in [piece + move for move in self.legal_moves(piece)]:
                self.pieces_removed[self.current_player == -1] += 1
                self.pieces[piece] -= self.current_player
                self.moves_left.remove(abs(piece-move))
                return True
            else:
                if move <= -1 and sum([-1 in moves for moves in [self.legal_moves(i) for i in self.get_player_piece_positions(self.current_player)]]) == 0 and piece == self.get_furthest_piece(self.current_player):
                    self.pieces_removed[self.current_player == -1] += 1
                    self.pieces[piece] -= self.current_player
                    self.moves_left.remove(min([val for val in self.moves_left if val]))
                    return True
                if move >= 24 and sum([24 in moves for moves in [self.legal_moves(i) for i in self.get_player_piece_positions(self.current_player)]]) == 0 and piece == self.get_furthest_piece(self.current_player):
                    self.pieces_removed[self.current_player == -1] += 1
                    self.moves_left.remove(min([val for val in self.moves_left if val]))
                    self.pieces[piece] -= self.current_player
                    return True
        if self.current_player * self.pieces[move] > 0:
            self.pieces[piece] = self.pieces[piece] - 1 if self.pieces[piece] > 0 else self.pieces[piece] + 1 if self.pieces[piece] < 0 else 0
            self.pieces[move] = self.pieces[move] + 1 if self.pieces[move] > 0 else self.pieces[move] - 1 if self.pieces[move] < 0 else 0
            self.moves_left.remove(abs(piece-move))
            return True
        elif (self.pieces[move] * self.current_player < 0 and abs(self.pieces[move]) == 1):
            self.pieces[move] = 1 if self.pieces[piece] > 0 else -1
            self.pieces[piece] = self.pieces[piece] - 1 if self.pieces[piece] > 0 else self.pieces[piece] + 1 if self.pieces[piece] < 0 else 0
            self.moves_left.remove(abs(piece-move))
            return True
        elif self.pieces[move] == 0:
            self.pieces[move] = 1 if self.pieces[piece] > 0 else -1
            self.pieces[piece] = self.pieces[piece] - 1 if self.pieces[piece] > 0 else self.pieces[piece] + 1 if self.pieces[piece] < 0 else 0
            self.moves_left.remove(abs(piece-move))
            return True
    
    def set_polygons(self):
        for move in range(24):
            if move < 12:
                pos = [((12)-(move%12)) * self.TRIANGLE_SPACING - 30, 450- 128]
            else:
                pos = [45 + (move-12) * self.TRIANGLE_SPACING - 28, 28]
            self.polygons[move] = pos
    
    def get_pos(self, i, y_dis=0):
        if i < 12:pos = [((12)-(i%12)) * self.TRIANGLE_SPACING - 8, 540 + y_dis]
        else:pos = [45 + (i-12) * self.TRIANGLE_SPACING - 8, 30 + y_dis]
        return pos


    def render(self):
        """
        Render the game board, pawns, dice, and UI.
        """
        # Draw the board
        self.screen.blit(self.assets["board"], (0,0))
        highlight = pygame.Surface(self.polygon_surface_size)
        highlight.set_colorkey((0,0,0))
        pygame.draw.polygon(highlight, self.POLYGON_COLOR, self.polygon)        
        highlight.set_alpha(125)

        if isinstance(self.piece_chosen, int):
            for move in [self.piece_chosen+ move for move in self.legal_moves(self.piece_chosen)]:
                try:
                    if 0 <= move < 12:
                        self.screen.blit(highlight, self.polygons[move])
                    elif 12<= move <=23:
                        self.screen.blit(pygame.transform.rotate(highlight, 180), self.polygons[move])
                except IndexError:
                    print(f"Error: move {move} is out of bounds for polygons list.")
                
                

        # Draw triangles and pawn s
        for i, piece in enumerate(self.pieces):
            y_dis = 0
            pos = self.get_pos(i, y_dis)
            self.piece_rects[i] = pygame.Rect(*pos, *self.assets['pawn_white'].get_size())
            if piece != 0:
                for j in range(abs(piece)):
                    if y_dis != 0 :
                        pos = self.get_pos(i, y_dis)
                        self.piece_rects[i] = pygame.Rect(*pos, *self.assets['pawn_white'].get_size())
                    color = self.assets["pawn_white"] if piece > 0 else self.assets["pawn_black"]
                    # debug
                    # pygame.draw.rect(self.screen, (0,255,0), self.piece_rects[i], 2)
                    # self.screen.blit(self.font.render(str(i), True, (self.BLACK)), pos)
                    self.screen.blit(color, pos)
                    if j+1 == abs(piece) and not isinstance(self.piece_chosen, int):
                        if (self.current_player > 0 and piece > 0) or (self.current_player < 0 and piece < 0):
                            if self.legal_moves(i):
                                pygame.draw.circle(self.screen, [102, 255,0], [pos[0] + 12, pos[1] + 12], 5)
                    y_dis += self.PIECE_SIZE * (1 if i > 11 else -1)
        for i in [-1, 1]:
            if self.player_has_dead_pieces(i):
                for j in range(15- self.get_player_pieces(i) - self.pieces_removed[i == -1]):
                    pos = [575, (15 + j * self.PIECE_SIZE) if i > 0 else (560 - j *self.PIECE_SIZE)]
                    self.screen.blit(self.assets["pawn_white"] if i > 0 else self.assets["pawn_black"], pos)
                    if i == self.current_player and j == 15 - self.get_player_pieces(i) - 1 and self.rolled:
                        pygame.draw.circle(self.screen, [102, 255,0], [pos[0] + 12, pos[1] + 12], 5)

        for dice in self.dices:
            dice.render(self.screen)

        if self.can_remove_pieces(self.current_player) and self.rolled and isinstance(self.piece_chosen, int):
            s = pygame.Surface(self.bear_rect().size)
            s.fill(self.POLYGON_COLOR)
            s.set_alpha(125)
            self.screen.blit(s, self.bear_rect().topleft)
        # Draw UI elements
        self.draw_ui()

        pygame.display.flip()
    
    def bear_rect(self):
        return pygame.Rect(570, 330 if self.current_player == 1 else 20, 30, 240)
    
    def get_pip(self, player):
        def calculate_pip(board, player=1):
            pip = 0
            for i, val in enumerate(board):
                if player == 1 and val > 0:
                    pip += abs(val * (i + 1))
                elif player == -1 and val < 0:
                    pip += abs(val) * (24 - i)
            pip += abs(15- self.get_player_pieces(player) - self.pieces_removed[player == -1]) * 24
            return pip
        return calculate_pip(self.pieces, player)
        return sum([abs(piece) * abs((i+1) - 23 if self.current_player == -1 else 0) for i, piece in enumerate(self.pieces) if piece * player > 0])

    def draw_ui(self):
        texts = [*self.player_names[::-1], f"PIP: {self.get_pip(-1)}", f"PIp: {self.get_pip(1)}", f'S:{self.score[1]}/{self.points_to_win}', f'S:{self.score[0]}/{self.points_to_win}']
        positions = [[20, 2], [20, 574], [self.SCREEN_WIDTH - 140, 2], [self.SCREEN_WIDTH - 140, 574], [self.SCREEN_WIDTH - 340, 2], [self.SCREEN_WIDTH - 340, 574]]
        for i, t in enumerate(texts):
            text = self.font.render(t, True, self.WHITE)
            draw_text_with_outline(self.screen, t, self.font, positions[i], self.WHITE, self.BLACK, outline_thickness=2)
        text = self.font.render(self.current_text, True, self.WHITE)
        draw_text_with_outline(self.screen, self.current_text, self.font, (self.SCREEN_WIDTH // 2 - text.get_width() // 2, 220), self.WHITE, self.BLACK, outline_thickness=2)


    def run(self):
        """
        Main game loop.
        """
        clock = pygame.time.Clock()
        running = True
        while not self.game_over and running:
            for player in [-1, 1]:
                if self.get_player_pieces(player) == 0 and self.pieces_removed[player == -1] == 15 and not self.current_text in [f"{self.player_names[player == -1]} wins the game!", f"{self.player_names[player == -1]} wins this round!"]:
                    self.score[player == -1] += 1
                    self.winner_decided = True
                    if self.score[player == -1] >= (self.points_to_win//2 +1):
                        self.current_text = f"{self.player_names[player == -1]} wins the game!"
                        threading.Timer(4, lambda: (setattr(self, 'game_over', True), setattr(self, 'current_text', ''))).start()
                        update_scoreboard('scoreboard.csv', self.player_names, [max(0, score-(max(self.score)-1)) for score in self.score])
                    else:
                        self.current_text = f"{self.player_names[player == -1]} wins this round!"
                        threading.Timer(4, lambda: (setattr(self, 'current_text', ''), self.reset_game())).start()
                        continue

            if self.player_has_dead_pieces(self.current_player) and self.current_player and self.rolled and not self.game_over:
                self.piece_chosen = 24 if self.current_player == 1 else -1
                if not self.legal_moves(self.piece_chosen):
                    self.current_text = "No Legal Moves. Skipping Turn."
                    threading.Timer(4, lambda: setattr(self, 'current_text', '')).start()
                    self.rolled = False
                    self.turn += 1
                    self.current_player *= -1
                    for dice in self.dices:
                        dice.reset()
                    self.moves_left = [0, 0, 0, 0]
            # elif:

            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over and not self.winner_decided:
                    mouse_pos = pygame.mouse.get_pos()
                    # Handle mouse clicks (e.g., rolling dice, moving pawns)
                    for dice in self.dices:
                        if time.time() - self.last_rolled > 0.4 and dice.rect().collidepoint(mouse_pos):
                            if self.turn == 0:
                                if not dice.rolled:
                                    dice.roll()
                            else:
                                self.dices[0].roll()
                                self.dices[1].roll()
                                    
            
                    if self.rolled and isinstance(self.piece_chosen, int):
                        for i in range(24):
                            thing_clicked = False 
                            if self.can_remove_pieces(self.current_player) and self.bear_rect().collidepoint(mouse_pos):
                                if self.play_move(self.piece_chosen, -1 if self.current_player == 1 else 24):
                                    if self.audio_on:
                                        self.click_sound.play()
                                    
                                    self.moves_left.append(0)
                                    if not any(self.moves_left):
                                        for dice in self.dices:
                                            dice.reset()
                                        self.rolled = False
                                        self.turn += 1
                                        self.current_player = -1 if self.current_player == 1 else 1
                                    self.piece_chosen = None
                                    break
                            if point_inside_polygon(self.polygon, self.polygons[i], self.polygon_surface_size, i >= 12):
                                print('Mouse over polygon:', i)
                                if i in [self.piece_chosen + move for move in self.legal_moves(self.piece_chosen)]:
                                    thing_clicked = True
                                    # print('Legal move:', i)
                                    if self.play_move(self.piece_chosen, i):
                                        if self.audio_on:
                                            self.click_sound.play()
                                        # print('Move played:', i)
                                        # print(self.moves_left)
                                        # print(f'removing move {i} - {self.piece_chosen}')
                                        self.moves_left.append(0)
                                        # print(self.moves_left)
                                        if not any(self.moves_left):
                                            for dice in self.dices:
                                                dice.reset()
                                            self.rolled = False
                                            self.turn += 1
                                            self.current_player = -1 if self.current_player == 1 else 1
                                    self.piece_chosen = None
                                    break
                        if not thing_clicked:
                            self.piece_chosen = None

                    if self.rolled and not isinstance(self.piece_chosen, int):
                        for i, rect in enumerate(self.piece_rects):
                            if isinstance(rect, int):
                                continue
                            elif rect.collidepoint(mouse_pos) and (self.current_player * self.pieces[i] > 0):
                                print(f'Piece {i} clicked.')
                                if self.legal_moves(i):
                                    print(f'Piece {i} has legal moves.')
                                    self.piece_chosen = i
                                    if self.audio_on:
                                        self.click_sound.play()

            if self.dices[0].rolled and self.dices[1].rolled and not self.rolled:
                if self.turn == 0:
                    if self.dices[0].value < self.dices[1].value:
                        self.current_text = "White player plays first"
                        threading.Timer(4, lambda: setattr(self, 'current_text', '')).start()
                        self.moves_left = [self.dices[0].value, self.dices[1].value, 0, 0]
                        self.rolled = True
                        self.current_player = 1
                    elif self.dices[0].value > self.dices[1].value:
                        self.current_text = "Black player plays first"
                        threading.Timer(4, lambda: setattr(self, 'current_text', '')).start()
                        self.current_player = -1
                        self.moves_left = [self.dices[0].value, self.dices[1].value, 0, 0]
                        self.rolled = True
                    elif self.dices[0].value == self.dices[1].value:
                        self.dices[0].reset()
                        self.dices[1].reset()
                        self.current_text = "Double rolled! Roll again."
                        threading.Timer(4, lambda: setattr(self, 'current_text', '')).start()
                else:
                    if self.dices[0].value == self.dices[1].value:
                        self.moves_left = [self.dices[0].value for i in range(4)]
                        for dice in self.dices:
                            dice.doubled = True
                    else:
                        self.moves_left = [self.dices[0].value, self.dices[1].value, 0, 0]
                    self.rolled = True
                    self.last_rolled = time.time()
                    legal_moves_exist = False
                    if self.get_player_pieces(self.current_player) == 15:
                        for i in range(24):
                            if self.legal_moves(i):
                                legal_moves_exist = True
                    else:
                        legal_moves_exist = self.legal_moves(24 if self.current_player == 1 else -1)
                    if not legal_moves_exist:
                        self.current_text = "No legal moves available. Switching player."
                        threading.Timer(4, lambda: setattr(self, 'current_text', '')).start()
                        self.rolled = False
                        self.turn += 1
                        self.current_player = -1 if self.current_player == 1 else 1
                        self.piece_chosen = None
                        for dice in self.dices:
                            dice.reset()
                        self.moves_left = [0, 0, 0, 0]
                # self.current_text.replace(' ', '    ')
            
            self.render()
            clock.tick(60)
        pygame.quit()


# Create an instance of the Game class
if __name__ == "__main__":
    game = Game('sdflkj')