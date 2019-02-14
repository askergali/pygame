import os
import pygame
import random
import sys
from itertools import cycle
from pygame.locals import *

pygame.init()
f = open("score.txt", "r+")
FPS = 30
clock = pygame.time.Clock()
size = WIDTH, HEIGHT = 288, 512
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Flappy Bird')
running = True
rule_group = pygame.sprite.Group()
lose_group = pygame.sprite.Group()
play_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
records_group = pygame.sprite.Group()
pygame.display.flip()
all_sprites = pygame.sprite.Group()
PIPEGAPSIZE = 100
GROUND = 404.48
IMAGES, SOUNDS, HITMASKS = {}, {}, {}

PLAYERS = (
    (
        'data/redbird-upflap.png',
        'data/redbird-midflap.png',
        'data/redbird-downflap.png',
    ))

BACKGROUNDS = (
    'data/background-day.png'
)

PIPES = (
    'data/pipe-green.png'
)


def main():
    global SCREEN, FPSCLOCK
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode(size)

    IMAGES['start_screen'] = pygame.image.load('data/start_screen.png').convert_alpha()

    IMAGES['ground'] = pygame.image.load('data/ground.png').convert_alpha()

    # sounds
    if 'win' in sys.platform:
        soundExt = '.wav'
    else:
        soundExt = '.ogg'

    SOUNDS['die'] = pygame.mixer.Sound('data/die' + soundExt)
    SOUNDS['hit'] = pygame.mixer.Sound('data/hit' + soundExt)
    SOUNDS['point'] = pygame.mixer.Sound('data/point' + soundExt)
    SOUNDS['swoosh'] = pygame.mixer.Sound('data/swoosh' + soundExt)
    SOUNDS['wing'] = pygame.mixer.Sound('data/wing' + soundExt)

    while True:
        IMAGES['background'] = pygame.image.load(BACKGROUNDS).convert()

        IMAGES['player'] = (
            pygame.image.load(PLAYERS[0]),
            pygame.image.load(PLAYERS[1]),
            pygame.image.load(PLAYERS[2])
        )

        IMAGES['pipe'] = (
            pygame.transform.rotate(
                pygame.image.load(PIPES).convert_alpha(), 180),
            pygame.image.load(PIPES).convert_alpha(),
        )

        HITMASKS['pipe'] = (
            getHitmask(IMAGES['pipe'][0]),
            getHitmask(IMAGES['pipe'][1]),
        )

        HITMASKS['player'] = (
            getHitmask(IMAGES['player'][0]),
            getHitmask(IMAGES['player'][1]),
            getHitmask(IMAGES['player'][2]),
        )

        movementInfo = showWelcomeAnimation()
        crashInfo = mainGame(movementInfo)
        showGameOverScreen(crashInfo)


def showWelcomeAnimation():
    playerIndex = 0
    playerIndexGen = cycle([0, 1, 2, 1])
    loopIter = 0

    playerx = int(WIDTH * 0.2)
    playery = int((HEIGHT - IMAGES['player'][0].get_height()) / 2)

    messagex = int((WIDTH - IMAGES['start_screen'].get_width()) / 2)
    messagey = int(HEIGHT * 0.12)

    basex = 0
    baseShift = IMAGES['ground'].get_width() - IMAGES['background'].get_width()

    playerShmVals = {'val': 0, 'dir': 1}

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                SOUNDS['wing'].play()
                return {
                    'playery': playery + playerShmVals['val'],
                    'basex': basex,
                    'playerIndexGen': playerIndexGen,
                }

        if (loopIter + 1) % 5 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 4) % baseShift)
        playerShm(playerShmVals)

        SCREEN.blit(IMAGES['background'], (0, 0))
        SCREEN.blit(IMAGES['player'][playerIndex],
                    (playerx, playery + playerShmVals['val']))
        SCREEN.blit(IMAGES['start_screen'], (messagex, messagey))
        SCREEN.blit(IMAGES['ground'], (basex, GROUND))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def mainGame(movementInfo):
    score = playerIndex = loopIter = 0
    playerIndexGen = movementInfo['playerIndexGen']
    playerx, playery = int(WIDTH * 0.2), movementInfo['playery']

    basex = movementInfo['basex']
    baseShift = IMAGES['ground'].get_width() - IMAGES['background'].get_width()

    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    upperPipes = [
        {'x': WIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': WIDTH + 200 + (WIDTH / 2), 'y': newPipe2[0]['y']},
    ]

    lowerPipes = [
        {'x': WIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': WIDTH + 200 + (WIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    pipeVelX = -4

    playerVelY = -9
    playerMaxVelY = 10
    playerAccY = 1
    playerRot = 45
    playerVelRot = 3
    playerRotThr = 20
    playerFlapAcc = -9
    playerFlapped = False

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > -2 * IMAGES['player'][0].get_height():
                    playerVelY = playerFlapAcc
                    playerFlapped = True
                    SOUNDS['wing'].play()

        crashTest = checkCrash({'x': playerx, 'y': playery, 'index': playerIndex},
                               upperPipes, lowerPipes)
        if crashTest[0]:
            return {
                'y': playery,
                'groundCrash': crashTest[1],
                'basex': basex,
                'upperPipes': upperPipes,
                'lowerPipes': lowerPipes,
                'score': score,
                'playerVelY': playerVelY,
                'playerRot': playerRot
            }

        playerMidPos = playerx + IMAGES['player'][0].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
                SOUNDS['point'].play()

        if (loopIter + 1) % 3 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 100) % baseShift)

        if playerRot > -90:
            playerRot -= playerVelRot

        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
        if playerFlapped:
            playerFlapped = False

            playerRot = 45

        playerHeight = IMAGES['player'][playerIndex].get_height()
        playery += min(playerVelY, GROUND - playery - playerHeight)

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipe['x'] += pipeVelX
            lPipe['x'] += pipeVelX

        if 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        if upperPipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        SCREEN.blit(IMAGES['background'], (0, 0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['ground'], (basex, GROUND))

        visibleRot = playerRotThr
        if playerRot <= playerRotThr:
            visibleRot = playerRot

        playerSurface = pygame.transform.rotate(IMAGES['player'][playerIndex], visibleRot)
        SCREEN.blit(playerSurface, (playerx, playery))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def showGameOverScreen(crashInfo):
    score = crashInfo['score']

    SOUNDS['hit'].play()
    if not crashInfo['groundCrash']:
        SOUNDS['die'].play()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

        lose_screen(score)
        f.write(str(score) + " ")

        FPSCLOCK.tick(FPS)
        pygame.display.update()


def playerShm(playerShm):
    if abs(playerShm['val']) == 8:
        playerShm['dir'] *= -1

    if playerShm['dir'] == 1:
        playerShm['val'] += 1
    else:
        playerShm['val'] -= 1


def getRandomPipe():
    gapY = random.randrange(0, int(GROUND * 0.6 - PIPEGAPSIZE))
    gapY += int(GROUND * 0.2)
    pipeHeight = IMAGES['pipe'][0].get_height()
    pipeX = WIDTH + 10

    return [
        {'x': pipeX, 'y': gapY - pipeHeight},
        {'x': pipeX, 'y': gapY + PIPEGAPSIZE},
    ]


def checkCrash(player, upperPipes, lowerPipes):
    pi = player['index']
    player['w'] = IMAGES['player'][0].get_width()
    player['h'] = IMAGES['player'][0].get_height()

    if player['y'] + player['h'] >= GROUND - 1:
        return [True, True]
    else:

        playerRect = pygame.Rect(player['x'], player['y'],
                                 player['w'], player['h'])
        pipeW = IMAGES['pipe'][0].get_width()
        pipeH = IMAGES['pipe'][0].get_height()

        for uPipe, lPipe in zip(upperPipes, lowerPipes):

            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

            pHitMask = HITMASKS['player'][pi]
            uHitmask = HITMASKS['pipe'][0]
            lHitmask = HITMASKS['pipe'][1]

            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

            if uCollide or lCollide:
                return [True, False]

    return [False, False]


def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in range(rect.width):
        for y in range(rect.height):
            if hitmask1[x1 + x][y1 + y] and hitmask2[x2 + x][y2 + y]:
                return True
    return False


def getHitmask(image):
    mask = []
    for x in range(image.get_width()):
        mask.append([])
        for y in range(image.get_height()):
            mask[x].append(bool(image.get_at((x, y))[3]))
    return mask


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
        return image
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)


def terminate():
    pygame.quit()
    sys.exit()


class BackButton(pygame.sprite.Sprite):
    def __init__(self, width, height, title, x, y):
        super().__init__(rule_group, lose_group, records_group, play_group, all_sprites)
        self.image = pygame.Surface([width, height])
        self.image.fill((0, 200, 50))
        font = pygame.font.Font(None, 30)
        text = font.render(title, 1, (255, 255, 255))
        text_x = width // 2 - text.get_width() // 2
        text_y = height // 2 - text.get_height() // 2
        self.image.blit(text, (text_x, text_y))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def check_click(self, mouse):
        if self.rect.collidepoint(mouse):
            return True


class EasyButton(pygame.sprite.Sprite):
    def __init__(self, width, height, title, x, y):
        super().__init__(play_group, all_sprites)
        self.image = pygame.Surface([width, height])
        self.image.fill((0, 200, 50))
        font = pygame.font.Font(None, 30)
        text = font.render(title, 1, (255, 255, 255))
        text_x = width // 2 - text.get_width() // 2
        text_y = height // 2 - text.get_height() // 2
        self.image.blit(text, (text_x, text_y))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def check_click(self, mouse):
        if self.rect.collidepoint(mouse):
            return True


class HardButton(pygame.sprite.Sprite):
    def __init__(self, width, height, title, x, y):
        super().__init__(play_group, all_sprites)
        self.image = pygame.Surface([width, height])
        self.image.fill((0, 200, 50))
        font = pygame.font.Font(None, 30)
        text = font.render(title, 1, (255, 255, 255))
        text_x = width // 2 - text.get_width() // 2
        text_y = height // 2 - text.get_height() // 2
        self.image.blit(text, (text_x, text_y))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def check_click(self, mouse):
        if self.rect.collidepoint(mouse):
            return True


class AgainButton(pygame.sprite.Sprite):
    def __init__(self, width, height, title, x, y):
        super().__init__(lose_group, all_sprites)
        self.image = pygame.Surface([width, height])
        self.image.fill((0, 200, 50))
        font = pygame.font.Font(None, 30)
        text = font.render(title, 1, (255, 255, 255))
        text_x = width // 2 - text.get_width() // 2
        text_y = height // 2 - text.get_height() // 2
        self.image.blit(text, (text_x, text_y))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def check_click(self, mouse):
        if self.rect.collidepoint(mouse):
            return True


class RecordsButton(pygame.sprite.Sprite):
    def __init__(self, width, height, title, x, y):
        super().__init__(records_group, all_sprites)
        self.image = pygame.Surface([width, height])
        self.image.fill((0, 200, 50))
        font = pygame.font.Font(None, 30)
        text = font.render(title, 1, (255, 255, 255))
        text_x = width // 2 - text.get_width() // 2
        text_y = height // 2 - text.get_height() // 2
        self.image.blit(text, (text_x, text_y))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def check_click(self, mouse):
        if self.rect.collidepoint(mouse):
            return True


class RuleButton(pygame.sprite.Sprite):
    def __init__(self, width, height, title, x, y):
        super().__init__(rule_group, all_sprites)
        self.image = pygame.Surface([width, height])
        self.image.fill((0, 200, 50))
        font = pygame.font.Font(None, 30)
        text = font.render(title, 1, (255, 255, 255))
        text_x = width // 2 - text.get_width() // 2
        text_y = height // 2 - text.get_height() // 2
        self.image.blit(text, (text_x, text_y))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def check_click(self, mouse):
        if self.rect.collidepoint(mouse):
            return True


class PlayButton(pygame.sprite.Sprite):
    def __init__(self, width, height, title, x, y):
        super().__init__(play_group, lose_group, all_sprites)
        self.image = pygame.Surface([width, height])
        self.image.fill((0, 200, 50))
        font = pygame.font.Font(None, 30)
        text = font.render(title, 1, (255, 255, 255))
        text_x = width // 2 - text.get_width() // 2
        text_y = height // 2 - text.get_height() // 2
        self.image.blit(text, (text_x, text_y))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def check_click(self, mouse):
        if self.rect.collidepoint(mouse):
            return True


class ExitButton(pygame.sprite.Sprite):
    def __init__(self, width, height, title, x, y):
        super().__init__(play_group, all_sprites)
        self.image = pygame.Surface([width, height])
        self.image.fill((0, 200, 50))
        font = pygame.font.Font(None, 30)
        text = font.render(title, 1, (255, 255, 255))
        text_x = width // 2 - text.get_width() // 2
        text_y = height // 2 - text.get_height() // 2
        self.image.blit(text, (text_x, text_y))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def check_click(self, mouse):
        if self.rect.collidepoint(mouse):
            return True


def game_screen():
    screen = pygame.display.set_mode(size)
    running = True
    intro_text = ["Easy", "Hard", "Back"]
    screen.fill((0, 0, 0))
    background = pygame.transform.scale(load_image('fon.jpeg'), (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    back_button = BackButton(250, 50, intro_text[2], 19, 340)
    easy_button = EasyButton(250, 50, intro_text[0], 19, 180)
    hard_button = HardButton(250, 50, intro_text[1], 19, 250)
    play_group.draw(screen)
    pygame.display.flip()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.check_click(event.pos):
                    print("clicked")
                    back_button.kill()
                    easy_button.kill()
                    hard_button.kill()
                    start_screen()
                elif easy_button.check_click(event.pos):
                    print("clicked")
                    back_button.kill()
                    easy_button.kill()
                    hard_button.kill()
                    main()
                elif hard_button.check_click(event.pos):
                    print("clicked")
                    back_button.kill()
                    easy_button.kill()
                    hard_button.kill()
                    main()

        all_sprites.update()
        pygame.display.flip()
        clock.tick(30)
    pygame.quit()


def rule_screen():
    screen = pygame.display.set_mode(size)
    running = True
    intro_text = ["Rules", "Back"]
    screen.fill((0, 0, 0))
    background = pygame.transform.scale(load_image('fon.jpeg'), (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    font = pygame.font.Font(None, 30)
    text = font.render("Enjoy!", 1, (255, 255, 255))
    screen.blit(text, (115, 180))
    back_button = BackButton(250, 50, intro_text[1], 19, 340)
    rule_group.draw(screen)
    pygame.display.flip()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.check_click(event.pos):
                    print("clicked")
                    back_button.kill()
                    start_screen()
                else:
                    pass
        pygame.display.flip()
        clock.tick(30)


def lose_screen(score):
    screen = pygame.display.set_mode(size)
    running = True
    intro_text = ["Back", "Again"]
    screen.fill((0, 0, 0))
    background = pygame.transform.scale(load_image('fon.jpeg'), (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    font = pygame.font.Font(None, 50)
    text = font.render(str(score), 1, (255, 255, 255))

    screen.blit(text, (130, 100))
    back_button = BackButton(120, 50, intro_text[0], 16, 215)
    again_button = AgainButton(120, 50, intro_text[1], 152, 215)
    lose_group.draw(screen)
    pygame.display.flip()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.check_click(event.pos):
                    print("clicked")
                    back_button.kill()
                    again_button.kill()
                    start_screen()
                elif again_button.check_click(event.pos):
                    print("clicked")
                    back_button.kill()
                    again_button.kill()
                    game_screen()
                else:
                    pass
        pygame.display.flip()
        clock.tick(30)


def records():
    scores_read = f.read()
    SCORES = scores_read.split()

    if len(SCORES) == 0:
        high_score = 0
    else:
        high_scores = sorted(SCORES, key=int, reverse=True)
        high_score = high_scores[0]

    records_screen(high_score)


def records_screen(high_score):
    screen = pygame.display.set_mode(size)
    running = True
    intro_text = ["Records", "Back"]
    screen.fill((0, 0, 0))
    background = pygame.transform.scale(load_image('fon.jpeg'), (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    font = pygame.font.Font(None, 30)
    text = font.render("Highest Score:", 1, (255, 255, 255))
    screen.blit(text, (20, 100))
    text1 = font.render(str(high_score), 1, (255, 255, 255))
    screen.blit(text1, (180, 100))
    back_button = BackButton(250, 50, intro_text[1], 19, 340)
    records_group.draw(screen)
    pygame.display.flip()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.check_click(event.pos):
                    print("clicked")
                    back_button.kill()
                    start_screen()
                else:
                    pass
        pygame.display.flip()
        clock.tick(30)


def start_screen():
    intro_text = ["Flappy Bird",
                  "Rules",
                  "Play", "Exit",
                  "Records"]

    background = pygame.transform.scale(load_image('fon.jpeg'), (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    font = pygame.font.Font(None, 50)
    text = font.render(intro_text[0], 1, (176, 226, 255))
    text_x = 50
    text_y = 50
    screen.blit(text, (text_x, text_y))
    rule_button = RuleButton(120, 50, intro_text[1], 16, 180)
    play_button = PlayButton(120, 50, intro_text[2], 152, 180)
    exit_button = ExitButton(120, 50, intro_text[3], 16, 250)
    records_button = RecordsButton(120, 50, intro_text[4], 152, 250)
    exit_group.draw(screen)
    rule_group.draw(screen)
    play_group.draw(screen)
    records_group.draw(screen)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if rule_button.check_click(event.pos):
                    print("clicked")
                    rule_button.kill()
                    play_button.kill()
                    records_button.kill()
                    exit_button.kill()
                    rule_screen()
                else:
                    pass

                if play_button.check_click(event.pos):
                    print("clicked")
                    rule_button.kill()
                    play_button.kill()
                    records_button.kill()
                    exit_button.kill()
                    game_screen()
                else:
                    pass

                if exit_button.check_click(event.pos):
                    print("clicked")
                    pygame.quit()
                else:
                    pass

                if records_button.check_click(event.pos):
                    print("clicked")
                    rule_button.kill()
                    play_button.kill()
                    records_button.kill()
                    exit_button.kill()
                    records()
                else:
                    pass

        pygame.display.flip()
        clock.tick(30)

start_screen()

f.close()
