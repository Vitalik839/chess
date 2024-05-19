import pygame as game
import Engine as engine
from tkinter import messagebox as msg
import tkinter as tk
from ctypes import cdll, c_bool, c_char_p


auth_dll = cdll.LoadLibrary(r"C:\Users\Користувач\Desktop\Chess\Autentification.dll")

# Оголошення прототипів функцій з DLL-файлу
register_user = auth_dll.RegisterUser
register_user.argtypes = [c_char_p, c_char_p]
register_user.restype = c_bool

login_user = auth_dll.login
login_user.argtypes = [c_char_p, c_char_p]
login_user.restype = c_bool

DIMENSION = 8
HEIGHT = WIDTH = 512
SQUARE_SIZE = HEIGHT // DIMENSION
MAX_FPS = 20
IMAGES = {}
IMAGES2 = {}
LOGIN = False
root = tk.Tk()
root.title("Авторизація")
root.geometry('550x300')
root['bg'] = 'black'


def upload_images():
    figures = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for f in figures:
        IMAGES[f] = game.transform.scale(game.image.load("images/" + f + ".png"), (SQUARE_SIZE, SQUARE_SIZE))

def main():
    game.init()

    sound_castle = game.mixer.Sound('sounds/castle.wav')
    sound_move = game.mixer.Sound('sounds/premove.wav')
    sound_capture = game.mixer.Sound('sounds/capture.wav')
    sound_check = game.mixer.Sound('sounds/move-check.wav')
    sound_end = game.mixer.Sound('sounds/game-end.wav')

    screen = game.display.set_mode((WIDTH, HEIGHT))
    clock = game.time.Clock()
    screen.fill(game.Color("white"))

    gs = engine.GameState()
    valid_moves = gs.validation_move()
    move_made = False
    upload_images()
    square_selected = ()
    player_clicks = [] #first and second position of squares
    flag = True
    animate = False
    game_over = False

    while flag:
        for event in game.event.get():
            if event.type == game.QUIT:
                flag = False
            elif event.type == game.MOUSEBUTTONDOWN:
                if not game_over:
                    location = game.mouse.get_pos()
                    col = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE
                    if square_selected == (row, col):
                        square_selected = ()
                        player_clicks = []
                    else:
                        square_selected = (row, col)
                        player_clicks.append(square_selected)
                    if len(player_clicks) == 2:
                        move = engine.Move(player_clicks[0], player_clicks[1], gs.board)
                        print(move.get_notation())
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                player_clicks = []
                                square_selected = () #reset user clicks
                        if not move_made:
                            player_clicks = [square_selected]
            elif event.type == game.KEYDOWN:
                if event.key == game.K_z:
                    animate_move(gs.move_log[-1], screen, gs.board, clock, 1)
                    gs.cancel_move()
                    move_made = True
                    animate = False
                if event.key == game.K_r:
                    gs = engine.GameState()
                    valid_moves = gs.validation_move()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False

        if move_made:
            if gs.check():
                sound_check.play()
            elif move.castle_move:
                sound_castle.play()
            elif (move.figure_captured != '--') or move.enpassant:
                sound_capture.play()
            else:
                sound_move.play()
            if animate:
                animate_move(gs.move_log[-1], screen, gs.board, clock, 0)
            valid_moves = gs.validation_move()
            move_made = False

        draw_game_state(screen, gs, valid_moves, square_selected)
        if gs.checkmate:
            game_over = True
            if gs.white_move:
                draw_text(screen, "Чорні перемогли через мат")
            else:
                draw_text(screen, "Білі перемогли через мат")
        elif gs.stalemate:
            game_over = True
            draw_text(screen, "Пат")
        clock.tick(MAX_FPS)
        game.display.flip()

def draw_game_state(screen, gs, valid_moves, square_selected):
    draw_board(screen)
    draw_pieces(screen, gs.board)
    highlight_squares(screen, gs, valid_moves, square_selected)

def draw_board(screen):
    global colors
    colors = [game.Color(255, 224, 192), game.Color(199, 117, 34)]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            game.draw.rect(screen, color, game.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
def draw_pieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            figure = board[row][col]
            if figure != "--":
                screen.blit(IMAGES[figure], game.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def highlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        row, col = sq_selected
        if gs.board[row][col][0] == ('w' if gs.white_move else 'b'):
            s = game.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(90)
            s.fill(game.Color("blue"))
            screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    if gs.board[move.end_row][move.end_col] != '--':
                        s2 = game.Surface((SQUARE_SIZE, SQUARE_SIZE))
                        s2.set_alpha(90)
                        s2.fill(game.Color("red"))
                        screen.blit(s2, (move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE))
                    else:
                        game.draw.circle(screen, (180, 180, 180), (move.end_col * SQUARE_SIZE + SQUARE_SIZE/2, move.end_row * SQUARE_SIZE + SQUARE_SIZE/2), SQUARE_SIZE/6)

def animate_move(move, screen, board, clock, rev):
    if rev == 1:
        board[move.start_row][move.start_col] = '--'
        draw_pieces(screen, board)
    coordinates = []
    draw_row = ((-1) ** rev) * move.end_row - ((-1) ** rev) * move.start_row
    draw_col = ((-1) ** rev) * move.end_col - ((-1) ** rev) * move.start_col
    frames = 10
    frames_count = (abs(draw_row) + abs(draw_col)) * frames
    for frame in range(frames_count + 1):
        if rev == 0:
            row, col = ((move.start_row + draw_row * frame / frames_count, move.start_col + draw_col * frame / frames_count))
            draw_board(screen)
            draw_pieces(screen, board)
            color = colors[(move.end_row + move.end_col) % 2]
            end_sq = game.Rect(move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            game.draw.rect(screen, color, end_sq)
        elif rev == 1:
            row, col = ((move.end_row + draw_row * frame / frames_count, move.end_col + draw_col * frame / frames_count))
            draw_board(screen)
            draw_pieces(screen, board)
            color = colors[(move.start_row + move.start_col) % 2]
            end_sq = game.Rect(move.start_col * SQUARE_SIZE, move.start_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            game.draw.rect(screen, color, end_sq)
        if move.figure_captured != '--':
            screen.blit(IMAGES[move.figure_captured], end_sq)
        screen.blit(IMAGES[move.figure_moved], game.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        game.display.flip()
        clock.tick(150)

def draw_text(screen, text):
    font = game.font.SysFont("Times New Roman", 40, True, False)
    text_object = font.render(text, 0, game.Color('Red'))
    text_location = game.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - text_object.get_width()/2, HEIGHT/2 - text_object.get_height()/2)
    screen.blit(text_object, text_location)

def login():
    password_user = password_entry.get()
    login_u = name_entry.get()
    LOGIN = login_user(login_u.encode(), password_user.encode())
    if LOGIN:
        root.destroy()
        main()
    else:
        msg.showinfo('Error', "Неправильний логін або пароль")

def register():
    password_user = password_entry.get()
    login_user = name_entry.get()
    register_user(login_user.encode(), password_user.encode())
    root.destroy()
    main()

if __name__ == "__main__":
    # main_label = tk.Label(root, text="Авторизація", font='Arial 18 bold', bg='black', fg='green')
    # main_label.pack()
    #
    # name_label = tk.Label(root, text="Ім'я користувача", font='Arial 14 bold', bg='black', fg='white', padx=10, pady=8)
    # name_label.pack()
    #
    # name_entry = tk.Entry(root, bg='black', fg='blue', font='Arial 14')
    # name_entry.pack()
    #
    # password_label = tk.Label(root, text="Пароль", font='Arial 14 bold', bg='black', fg='white', padx=10, pady=8)
    # password_label.pack()
    #
    # password_entry = tk.Entry(root, bg='black', fg='blue', font='Arial 15', show = '*')
    # password_entry.pack()
    #
    # myname_label = tk.Label(root, text="Розробив Віталій Новаковський", font='Arial 14 bold', bg='black', fg='white', padx=10, pady=8)
    # myname_label.place(x = 50, y = 250)
    # btn_login = tk.Button(root, text="Ввійти", width=15, command=login)
    # btn_register = tk.Button(root, text="Зареєструватися", width=15, command = register)
    #
    # btn_login.place(x=150, y=200)
    # btn_register.place(x=300, y=200)
    main()
    #root.mainloop()
