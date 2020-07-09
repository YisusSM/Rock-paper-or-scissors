import pygame
from network import Network
import cv2
import numpy as np
from keras.models import load_model
from game import Game
import random
import os
# from gather_images import Train

pygame.font.init()
width = 700
height = 700
cap = cv2.VideoCapture(0)
model = load_model("rock-paper-scissors-model.h5")
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Client")

REV_CLASS_MAP = {
    0: "Rock",
    1: "Paper",
    2: "Scissors",
    3: "none"
}


def mapper(val):
    return REV_CLASS_MAP[val]


class Timer:
    def __init__(self, goal):
        self.startPoint = 0
        self.goal = goal
        self.count = 0
        self.on = False
        self.over = None

    def start(self):
        if not self.on:
            self.startPoint = pygame.time.get_ticks()
            self.count = 0
            self.on = True
            self.over = False

    def stop(self):
        self.count = 0
        self.on = False
        self.startPoint = pygame.time.get_ticks()
        self.over = False

    def reset(self):
        self.count = 0
        self.on = False
        self.over = False

    def getTime(self):
        if self.isOver():
            return self.goal
        else:
            self.count = round((pygame.time.get_ticks() - self.startPoint) / 1000)
            if self.count >= self.goal:
                self.over = True
                return self.goal
        return self.count

    def isOver(self):
        return self.over


class Button:
    def __init__(self, text, x, y, color, w, h, text_size):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.width = w
        self.height = h
        self.textSize = text_size

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        font = pygame.font.SysFont("comicsans", self.textSize)
        text = font.render(self.text, 1, (255, 255, 255))
        win.blit(text, (self.x + round(self.width / 2) - round(text.get_width() / 2),
                        self.y + round(self.height / 2) - round(text.get_height() / 2)))

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        else:
            return False


class Video:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 300
        self.height = 225
        self.img = None
        self.user_move_name = "Waiting..."
        self.queryTime = pygame.time.get_ticks()

    def show(self, win):
        retval, frame = cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (300, 225))
        self.img = cv2.resize(frame, (227, 227))
        frame = np.rot90(frame)
        frame = pygame.surfarray.make_surface(frame)
        # img = cv2.rectangle(frame, (100, 100), (500, 500), (255, 255, 255), 2)

        # pygame.draw.rect(win, (0,0,0), (self.x, self.y, self.width, self.height))
        win.blit(frame, (self.x, self.y))
        pygame.display.update()

    def capture(self):
        return self.img

    def predict(self):
        time = int((pygame.time.get_ticks() - self.queryTime) / 1000)
        if time > 1:
            self.queryTime = pygame.time.get_ticks()
            pred = model.predict(np.array([self.img]))
            move_code = np.argmax(pred[0])
            self.user_move_name = mapper(move_code)  # Devuelve el valor
        return self.user_move_name


def redrawWindow(win, game, p):
    win.fill((128, 128, 128))

    if not (game.connected()):
        font = pygame.font.SysFont("comicsans", 80)
        text = font.render("Waiting for Player...", 1, (255, 0, 0), True)
        win.blit(text, (width / 2 - text.get_width() / 2, height / 2 - text.get_height() / 2))
    else:
        games_info = game.getGamesPlayedInfo()
        rounds_info = game.getRoundsInfo()
        tim.start()
        time = tim.getTime()
        p1Wins = games_info["0"]
        p2Wins = games_info["1"]
        rounds = rounds_info["total"]
        roundsp1Wins = rounds_info["0"]
        roundsp2Wins = rounds_info["1"]
        roundsties = rounds_info["ties"]

        font = pygame.font.SysFont("comicsans", 60)
        text = font.render("Your Move", 1, (0, 255, 255))
        win.blit(text, (80, 100))

        text = font.render("Opponents", 1, (0, 255, 255))
        win.blit(text, (380, 100))


        if not tim.isOver():
            time = 10 - time
            text = "Remaining time: "
            text = font.render(text + str(time), 1, (0, 255, 255))
            win.blit(text, (width / 2 - text.get_width() / 2, 50))
        else:
            text = font.render("Time!", 1, (0, 255, 255))
            win.blit(text, (width / 2 - text.get_width() / 2, 50))
        vid.show(win)
        move1 = game.get_player_move(0)
        move2 = game.get_player_move(1)
        if game.bothWent():
            if p == 0:
                text1 = font.render(move1, 1, (0, 255, 0))
                text2 = font.render(move2, 1, (0, 0, 0))
            else:
                text1 = font.render(move1, 1, (0, 0, 0))
                text2 = font.render(move2, 1, (0, 255, 0))
        else:
            if game.p1Went and p == 0:
                text1 = font.render(move1, 1, (0, 255, 0))
            elif p == 0:
                if time is not tim.getTime():
                    pred = vid.predict()
                    text1 = font.render(pred, 1, (0, 0, 0))
                else:
                    text1 = font.render("Waiting...", 1, (0, 0, 0))
            elif game.p1Went:
                text1 = font.render("Locked In", 1, (0, 0, 0))
            else:
                text1 = font.render("Waiting...", 1, (0, 0, 0))

            if game.p2Went and p == 1:
                text2 = font.render(move2, 1, (0, 255, 0))
            elif p == 1:
                if time is not tim.getTime():
                    pred = vid.predict()
                    text2 = font.render(pred, 1, (0, 0, 0))
                else:
                    text2 = font.render("Waiting...", 1, (0, 0, 0))
            elif game.p2Went:
                text2 = font.render("Locked In", 1, (0, 0, 0))
            else:
                text2 = font.render("Waiting...", 1, (0, 0, 0))

        font = pygame.font.SysFont("comicsans", 40)
        if p == 1:
            text = font.render("W: " + str(p2Wins) + "    L: " + str(p1Wins), 1, (0, 255, 255))
            win.blit(text, (width / 2 - text.get_width() / 2, 20))
            text = font.render("Round: " + str(rounds) + "    W: " + str(roundsp2Wins) + "    L: " + str(roundsp1Wins) + "    D: " + str(roundsties), 1, (0, 255, 255))
            win.blit(text, (width / 2 - text.get_width() / 2, 630))
            win.blit(text2, (100, 450))
            win.blit(text1, (400, 300))
        else:
            text = font.render("W: " + str(p1Wins) + "    L: " + str(p2Wins), 1, (0, 255, 255))
            win.blit(text, (width / 2 - text.get_width() / 2, 20))
            text = font.render("Round: " + str(rounds) + "    W: " + str(roundsp1Wins) + "    L: " + str(roundsp2Wins) + "    D: " + str(roundsties) , 1, (0, 255, 255))
            win.blit(text, (width / 2 - text.get_width() / 2, 630))
            win.blit(text1, (100, 450))
            win.blit(text2, (400, 300))
        selectBtn.draw(win)

    pygame.display.update()


# btns = [Button("Rock", 50, 500, (0,0,0)), Button("Scissors", 250, 500, (255,0,0)), Button("Paper", 450, 500, (0,255,0))]
selectBtn = Button("Select", 100, 500, (0, 255, 0), 150, 100, 40)
tim = Timer(10)
vid = Video(40, 200)
vid_train = Video(width/2-150, 200)


def main():
    run = True
    pause = False
    clock = pygame.time.Clock()
    n = Network()
    player = int(n.getP())
    print("You are player", player)
    while run or pause:
        while run:
            clock.tick(60)
            try:
                game = n.send("get")

            except:
                run = False
                pause = False
                print("Couldn't get game")
                break

            if game.bothWent():
                redrawWindow(win, game, player)
                pygame.time.delay(500)

                font = pygame.font.SysFont("comicsans", 90)
                if (game.winner() == 1 and player == 1) or (game.winner() == 0 and player == 0):
                    text = font.render("You Won!", 1, (255, 0, 0))
                elif game.winner() == -1:
                    text = font.render("Tie Game!", 1, (255, 0, 0))
                else:
                    text = font.render("You Lost...", 1, (255, 0, 0))

                win.blit(text, (width / 2 - text.get_width() / 2, height / 2 - text.get_height() / 2))
                win.blit(text, (width / 2 - text.get_width() / 2, height / 2 - text.get_height() / 2))
                pygame.display.update()
                run = False
                pause = True
                tim.stop()
            else:
                redrawWindow(win, game, player)

            if tim.isOver():
                if player == 0:
                    if not game.p1Went:
                        n.send(vid.predict())
                else:
                    if not game.p2Went:
                        n.send(vid.predict())

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pause = False
                    pygame.quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if selectBtn.click(pos) and game.connected():
                        if player == 0:
                            if not game.p1Went:
                                n.send(vid.predict())
                        else:
                            if not game.p2Went:
                                n.send(vid.predict())
        while pause:
            tim.reset()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pause = False
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    try:
                        run = True
                        pause = False
                        game = n.send("reset")
                    except:
                        pause = False
                        run = False
                        print("Couldn't get game")
                        break


def local_main():
    run = True
    pause = False
    game = Game(0)
    game.ready = True
    clock = pygame.time.Clock()
    player = 0
    print("You are player", player)
    while run or pause:
        while run:
            clock.tick(60)

            if game.p1Went:

                p2move = random.randint(0, 2)
                p2move = REV_CLASS_MAP[p2move]
                game.play(1, p2move)

                redrawWindow(win, game, player)
                pygame.time.delay(500)

                font = pygame.font.SysFont("comicsans", 90)
                if game.winner() == 0:
                    text = font.render("You Won!", 1, (255, 0, 0))
                elif game.winner() == -1:
                    text = font.render("Tie Game!", 1, (255, 0, 0))
                else:
                    text = font.render("You Lost...", 1, (255, 0, 0))

                win.blit(text, (width / 2 - text.get_width() / 2, height / 2 - text.get_height() / 2))
                win.blit(text, (width / 2 - text.get_width() / 2, height / 2 - text.get_height() / 2))
                pygame.display.update()
                run = False
                pause = True
                tim.stop()
            else:
                redrawWindow(win, game, player)

            if tim.isOver():
                if player == 0:
                    if not game.p1Went:
                        game.play(player, vid.predict())
                else:
                    if not game.p2Went:
                        game.play(player, vid.predict())

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pause = False
                    pygame.quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if selectBtn.click(pos):
                        game.play(player, vid.predict())
        while pause:
            tim.reset()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pause = False
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    run = True
                    pause = False
                    game.resetWent()


def save_frames(text):
    start = False
    count = 0

    IMG_SAVE_PATH = 'image_data'
    IMG_CLASS_PATH = os.path.join(IMG_SAVE_PATH, text)

    try:
        os.mkdir(IMG_SAVE_PATH)
    except FileExistsError:
        pass
    try:
        os.mkdir(IMG_CLASS_PATH)
    except FileExistsError:
        pass

    while True:
        vid_train.show(win)

        frame = vid_train.capture()

        if count == 200:
            break

        save_path = os.path.join(IMG_CLASS_PATH, '{}.jpg'.format(count + 1))
        cv2.imwrite(save_path, frame)
        count += 1


def show_frames(text):
    buttons = [Button("Back", 50, 520, (255, 0, 0), 200, 100, 40),
               Button("Store", 450, 520, (255, 0, 0), 200, 100, 40)]
    run = True
    saved = False
    clock = pygame.time.Clock()

    while run:

        if saved:
            font = pygame.font.SysFont("comicsans", 80)
            text = font.render("Saved!", 1, (0, 255, 0))
            win.blit(text, (width / 2 - text.get_width() / 2, 310))
            pygame.display.update()
            pygame.time.delay(2000)
            saved = False

        opt = ''
        clock.tick(60)
        win.fill((128, 128, 128))
        # font = pygame.font.SysFont("comicsans", 80)
        # text = font.render("Welcome!", 1, (255, 0, 0))
        # win.blit(text, (width / 2 - text.get_width() / 2, 105))
        vid_train.show(win)

        for btn in buttons:
            btn.draw(win)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for btn in buttons:
                    if btn.click(pos):
                        opt = btn.text.upper()[0]

        if opt == 'B':
            run = False
        elif opt == 'S':
            try:
                save_frames(text)
                saved = True
            except:
                saved = False


def train():
    train_buttons = [Button("Rock Frames", 25, 100, (255, 0, 0), 300, 100, 40),
                     Button("Scissors Frames", 375, 100, (255, 0, 0), 300, 100, 40),
                     Button("Paper Frames", 25, 250, (255, 0, 0), 300, 100, 40),
                     Button("None Frames", 375, 250, (255, 0, 0), 300, 100, 40),
                     Button("Train", width / 2 - 300 / 2, 400, (255, 0, 0), 300, 100, 40),
                     Button("Back", 50, 600, (255, 0, 0), 120, 60, 30)]
    run = True
    trained = False
    clock = pygame.time.Clock()

    while run:
        if trained:
            font = pygame.font.SysFont("comicsans", 80)
            text = font.render("Trained!", 1, (0, 255, 0))
            win.blit(text, (width / 2 - text.get_width() / 2, 310))
            pygame.display.update()
            pygame.time.delay(2000)
            trained = False


        opt = ''
        clock.tick(60)
        win.fill((128, 128, 128))
        # font = pygame.font.SysFont("comicsans", 80)
        # text = font.render("Welcome!", 1, (255, 0, 0))
        # win.blit(text, (width / 2 - text.get_width() / 2, 105))
        # vid_train.show(win)

        for btn in train_buttons:
            btn.draw(win)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for btn in train_buttons:
                    if btn.click(pos):
                        opt = btn.text.upper()[0]
            if opt == 'R':
                show_frames("rock")
            elif opt == 'P':
                show_frames("paper")
            elif opt == 'S':
                show_frames("scissors")
            elif opt == 'N':
                show_frames("none")
            elif opt == 'T':
                os.system('python train.py')
                trained = True
            elif opt == 'B':
                run = False


def menu_screen():
    menu_buttons = [Button("Training Mode", width / 2 - 300 / 2, 200, (255, 0, 0), 300, 100, 40),
                    Button("Local Game", width / 2 - 300 / 2, 350, (255, 0, 0), 300, 100, 40),
                    Button("Online Game", width / 2 - 300 / 2, 500, (255, 0, 0), 300, 100, 40)]
    run = True
    clock = pygame.time.Clock()
    opt = ''
    while run:
        clock.tick(60)
        win.fill((128, 128, 128))
        font = pygame.font.SysFont("comicsans", 80)
        text = font.render("Welcome!", 1, (255, 0, 0))
        win.blit(text, (width / 2 - text.get_width() / 2, 105))

        for btn in menu_buttons:
            btn.draw(win)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for btn in menu_buttons:
                    if btn.click(pos):
                        opt = btn.text.upper()[0]

                run = False
    if opt == 'O':
        main()
    elif opt == 'L':
        local_main()
    elif opt == 'T':
        train()
        pass


while True:
    menu_screen()
