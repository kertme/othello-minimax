import pygame
import time
import numpy


class OthelloBoard:

    def __init__(self):
        self.width = 60
        self.row = self.col = 8
        self.margin = 100
        # tüm taşların bulunduğu matris
        self.tiles = numpy.zeros([self.col, self.row])
        # stabil taşların bulundugu matris
        self.stable = numpy.zeros([self.col, self.row])
        # hamle sırasına sahip oyuncu
        self.player = 2
        # beyaz taşlar
        self.tiles[self.row // 2 - 1][self.col // 2 - 1] = 1
        self.tiles[self.row // 2][self.col // 2] = 1
        # siyah taşlar
        self.tiles[self.row // 2][self.col // 2 - 1] = 2
        self.tiles[self.row // 2 - 1][self.col // 2] = 2
        # mevcut tahtanın genel bilgileri
        self.count_black = self.count_white = 2
        self.count_available = 4
        self.count_stable_black = 0
        self.count_stable_white = 0
        self.count_total_stable_direct_black = 0
        self.count_total_stable_direct_white = 0
        # yapay zekanın son hamlesi
        self.ai_last_move = None
        # müsait hamleler
        self.available = []
        self.updateAvailable()

    # müsait hamleleri bulan fonksiyon
    def updateAvailable(self):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0),
                      (1, 1), (-1, -1), (1, -1), (-1, 1)]
        color = self.player
        color_reverse = 3 - color
        # clear available pos
        self.available = []
        for i in range(self.row):
            for j in range(self.col):
                if self.tiles[i][j] == -1:
                    self.tiles[i][j] = 0
        # find available pos
        for i in range(self.row):
            for j in range(self.col):
                if self.tiles[i][j] == self.player:
                    for dx, dy in directions:
                        checking_i = i + dy
                        checking_j = j + dx
                        find_one_reverse_color = False
                        while 0 <= checking_i < self.row and 0 <= checking_j < self.col:
                            tile = self.tiles[checking_i][checking_j]
                            if tile == color_reverse:
                                checking_i += dy
                                checking_j += dx
                                find_one_reverse_color = True
                            elif tile == 0 and find_one_reverse_color:
                                self.tiles[checking_i][checking_j] = -1
                                # find available pos, add it into self.available
                                self.available.append((checking_i, checking_j))
                                break
                            else:
                                break

    # rengi degismesi gereken tas varsa degistiren fonksiyon
    def reverse(self, set_i, set_j):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0),
                      (1, 1), (-1, -1), (1, -1), (-1, 1)]
        color_reverse = self.player
        color = 3 - color_reverse
        for dx, dy in directions:
            checking_i = set_i + dy
            checking_j = set_j + dx
            while 0 <= checking_i < self.row and 0 <= checking_j < self.col:
                tile = self.tiles[checking_i][checking_j]
                if tile == color_reverse:
                    checking_i += dy
                    checking_j += dx
                elif tile == color:
                    reversing_i = set_i + dy
                    reversing_j = set_j + dx
                    while (reversing_i, reversing_j) != (checking_i, checking_j):
                        self.tiles[reversing_i][reversing_j] = color
                        reversing_i += dy
                        reversing_j += dx
                    break
                else:
                    break

    # stabil taşları günceller
    def updateStable(self):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        find_new_stable_tile = True
        while find_new_stable_tile:
            find_new_stable_tile = False
            self.count_total_stable_direct_black = 0
            self.count_total_stable_direct_white = 0
            for i in range(self.row):
                for j in range(self.col):
                    if (self.tiles[i][j] == 1 or self.tiles[i][j] == 2) and not self.stable[i][j]:
                        count_stable_direction = 0
                        for direction in directions:
                            if self.checkDirectionStable(i, j, direction):
                                count_stable_direction += 1
                        if count_stable_direction == 4:
                            find_new_stable_tile = True
                            self.stable[i][j] = 1
                        else:
                            if self.tiles[i][j] == 1:
                                self.count_total_stable_direct_white += count_stable_direction
                            elif self.tiles[i][j] == 2:
                                self.count_total_stable_direct_black += count_stable_direction

    #Yön stabil mi degil mi bakan fonksiyon
    def checkDirectionStable(self, i, j, direction):
        directions = [direction, (-direction[0], -direction[1])]
        color = self.tiles[i][j]
        color_reverse = 3 - color
        count_tmp = 0
        for dx, dy in directions:
            find_unstable_tile = False
            checking_i = i + dy
            checking_j = j + dx
            while True:
                if not (0 <= checking_i < self.row and 0 <= checking_j < self.col):
                    if find_unstable_tile:
                        count_tmp += 1
                        break
                    else:
                        return True
                if self.tiles[checking_i][checking_j] == color:
                    if self.stable[checking_i][checking_j]:
                        return True
                    else:
                        checking_i += dy
                        checking_j += dx
                        find_unstable_tile = True
                elif self.tiles[checking_i][checking_j] == color_reverse:
                    if self.stable[checking_i][checking_j]:
                        count_tmp += 1
                        break
                    else:
                        checking_i += dy
                        checking_j += dx
                        find_unstable_tile = True
                else:
                    break
        if count_tmp == 2:
            return True
        else:
            return False

    # Tahtanın mevcut degerlerini sayan fonksiyon
    def updateCount(self):
        self.count_black = self.count_white = 0
        self.count_available = 0
        self.count_stable_white = self.count_stable_black = 0
        for i in range(self.row):
            for j in range(self.col):
                tile = self.tiles[i][j]
                if tile == 1:
                    self.count_white += 1
                elif tile == 2:
                    self.count_black += 1
                elif tile == -1:
                    self.count_available += 1
                if self.stable[i][j] == 1:
                    if self.tiles[i][j] == 1:
                        self.count_stable_white += 1
                    elif self.tiles[i][j] == 2:
                        self.count_stable_black += 1
    # tahtayi kopyalar
    def copy(self):
        othelloBoard_new = OthelloBoard()
        othelloBoard_new.player = self.player
        othelloBoard_new.available = [item for item in self.available]
        for i in range(self.row):
            for j in range(self.col):
                othelloBoard_new.tiles[i][j] = self.tiles[i][j]
                othelloBoard_new.stable[i][j] = self.stable[i][j]
        othelloBoard_new.count_black = self.count_black
        othelloBoard_new.count_white = self.count_white
        othelloBoard_new.count_available = self.count_available
        othelloBoard_new.count_stable_black = self.count_stable_black
        othelloBoard_new.count_stable_white = self.count_stable_white
        othelloBoard_new.count_total_stable_direct_black = self.count_total_stable_direct_black
        othelloBoard_new.count_total_stable_direct_white = self.count_total_stable_direct_white
        return othelloBoard_new
    #kazanani dondurur
    def getWinner(self):
        if self.count_white > self.count_black:
            return "White"
        elif self.count_black > self.count_white:
            return "Black"
        else:
            return "Tie"

# ai icin hamleyi tahtada gerceklestiren fonksiyon
def setMoveAI(othelloBoard, set_i, set_j):
    othelloBoard_new = None

    if 0 <= set_i < othelloBoard.row and 0 <= set_j < othelloBoard.col and \
            othelloBoard.tiles[set_i][set_j] == -1:
        # deep copy to new othelloBoard
        othelloBoard_new = othelloBoard.copy()
        # set tile
        othelloBoard_new.tiles[set_i][set_j] = othelloBoard.player
        othelloBoard_new.player = 3 - othelloBoard.player
        # update
        othelloBoard_new.reverse(set_i, set_j)
        othelloBoard_new.updateAvailable()
        # othelloBoard_new.updateStable()
        othelloBoard_new.updateCount()

        if othelloBoard_new.count_available == 0:
            othelloBoard_new.player = 3 - othelloBoard_new.player
            othelloBoard_new.updateAvailable()
            # othelloBoard_new.updateCount()

    return othelloBoard_new

# resimlerin tutuldugu yapi
class Images:

    def __init__(self):
        self.width = 50
        self.background = pygame.image.load('images/background.gif')
        self.black = pygame.image.load('images/black.gif')
        self.white = pygame.image.load('images/white.gif')
        self.available = pygame.image.load('images/available.gif')
        self.blank = pygame.image.load('images/blank.gif')
        self.indicator = pygame.image.load('images/indicator.png')

# tree'deki nodelar, tahtalari agac yapisinda saklamak icin
class OthelloBoardNode:

    def __init__(self, othelloBoard):
        self.parent = None
        # self.kids: {(i, j): node}
        self.kids = {}
        self.othelloBoard = othelloBoard

    def getScore(self):
        othelloBoard = self.othelloBoard
        return 100 * (othelloBoard.count_stable_white - othelloBoard.count_stable_black) \
               + (othelloBoard.count_total_stable_direct_white
                  - othelloBoard.count_total_stable_direct_black)

# tahtaların tutuldugu agac yapisi
class OthelloBoardTree:

    def __init__(self, node):
        self.root = node
        # self.expandLayer >= 2
        self.expandLayer = 2
    # alt cocuklari layer sayisina gore olusturmak icin gerekli fonksiyon
    def expandTree(self):
        node = self.root
        # ilk katmani olusturuyor
        for i, j in node.othelloBoard.available:
            if (i, j) not in node.kids:
                othelloBoard_new = setMoveAI(node.othelloBoard, i, j)
                node_new = OthelloBoardNode(othelloBoard_new)
                node.kids[(i, j)] = node_new
                node_new.parent = node
    # en iyi hamlelerin bulundugu kisim
    def findBestMove(self, player_color):
        scores = {}
        alpha = -6400
        for key in self.root.kids:
            score = self.Minimax(self.root.kids[key], player_color,
                                self.expandLayer - 1, alpha)
            scores.update({key: score})
            if alpha < score:
                alpha = score
        if not scores:
            return (-1, -1)
        max_key = max(scores, key=scores.get)
        min_key = min(scores, key=scores.get)
        #print(scores[min_key], scores[max_key])
        return max_key
    # Minimax ile o konum icin en uygun hamlenin hesaplandigi yer
    def Minimax(self, node, player_color, layer, pruning_flag):
        if layer and node.othelloBoard.available:
            # min layer
            if node.othelloBoard.player == player_color:
                beta = 6400
                for i, j in node.othelloBoard.available:
                    if (i, j) in node.kids:
                        score = self.Minimax(
                            node.kids[(i, j)], player_color, layer - 1, beta)
                    else:
                        # count += 1
                        othelloBoard_new = setMoveAI(node.othelloBoard, i, j)
                        node_new = OthelloBoardNode(othelloBoard_new)
                        node.kids[(i, j)] = node_new
                        node_new.parent = node
                        score = self.Minimax(
                            node_new, player_color, layer - 1, beta)
                    if score <= pruning_flag:
                        beta = score
                        break
                    if beta > score:
                        beta = score
                # print('layer:', layer, 'min:', beta, 'pruning:', pruning_flag)
                return beta
            # max layer
            else:
                alpha = -6400
                for i, j in node.othelloBoard.available:
                    if (i, j) in node.kids:
                        score = self.Minimax(
                            node.kids[(i, j)], player_color, layer - 1, alpha)
                    else:
                        # count += 1
                        othelloBoard_new = setMoveAI(node.othelloBoard, i, j)
                        node_new = OthelloBoardNode(othelloBoard_new)
                        node.kids[(i, j)] = node_new
                        node_new.parent = node
                        score = self.Minimax(
                            node_new, player_color, layer - 1, alpha)
                    if score >= pruning_flag:
                        alpha = score
                        break
                    if alpha < score:
                        alpha = score
                # print('layer:', layer, 'max:', alpha, 'pruning:', pruning_flag)
                return alpha
        else:
            node.othelloBoard.updateStable()
            node.othelloBoard.updateCount()
            score = node.getScore()
            # print('layer:', layer, 'leaf:', node.score)
            return score

# arayuz icin gerekli
def draw(screen, images, othelloBoard):
    # arkaplan
    screen.blit(images.background, (0, 0))

    # tahtanin satir ve sutunlari
    width = othelloBoard.width
    row = othelloBoard.row
    col = othelloBoard.col
    margin = othelloBoard.margin
    for i in range(row + 1):
        for j in range(col + 1):
            pygame.draw.line(screen, (0, 0, 0),
                             (margin + i * width, margin),
                             (margin + i * width, margin + col * width))
            pygame.draw.line(screen, (0, 0, 0),
                             (margin, margin + j * width),
                             (margin + row * width, margin + j * width))

    # taslar icin
    for i in range(row):
        for j in range(col):
            color = images.blank
            tile = othelloBoard.tiles[i][j]
            # if white tile
            if tile == 1:
                color = images.white
            # if black tile
            elif tile == 2:
                color = images.black
            elif tile == -1:
                color = images.available
            screen.blit(color, (margin + j * width + width // 2 - images.width // 2,
                                margin + i * width + width // 2 - images.width // 2))
    if othelloBoard.ai_last_move:
        color = images.indicator
        screen.blit(color, (margin + othelloBoard.ai_last_move[1] * width + width // 2 - images.width // 2,
                            margin + othelloBoard.ai_last_move[0] * width + width // 2 - images.width // 2))

    # yan tarafdaki tas sayilari ve infolar icin gerekli kisim
    pos = margin * 2 + othelloBoard.width * col
    if othelloBoard.player == 1:
        screen.blit(images.black, (pos, pos // 2 - images.width * 2.5))
        screen.blit(images.white, (pos, pos // 2 - images.width * 0.5))
    else:
        screen.blit(images.black, (pos, pos // 2 - images.width * 2.5))
        screen.blit(images.white, (pos, pos // 2 - images.width * 0.5))

    screen.blit(images.indicator, (pos, pos // 2 - images.width * 4.5))

    fontObj = pygame.font.Font(None, images.width)

    textSurfaceObj = fontObj.render("Last Move", True, (0, 0, 0))
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (pos + 50 + images.width * 2, pos // 2 - images.width * 4)
    screen.blit(textSurfaceObj, textRectObj)

    textSurfaceObj = fontObj.render(str(othelloBoard.count_black), True, (0, 0, 0))
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (pos + images.width * 2, pos // 2 - 2*images.width)
    screen.blit(textSurfaceObj, textRectObj)

    textSurfaceObj = fontObj.render(str(othelloBoard.count_white), True, (0, 0, 0))
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (pos + images.width * 2, pos // 2)
    screen.blit(textSurfaceObj, textRectObj)

    # draw text
    textSurfaceObj = fontObj.render("Press 'b' to undo", True, (0, 0, 0))
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (pos + 100, pos // 2 + 2*images.width)
    screen.blit(textSurfaceObj, textRectObj)

    textSurfaceObj = fontObj.render("Press 'r' to restart", True, (0, 0, 0))
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (pos + 100, pos // 2 + 3 * images.width)
    screen.blit(textSurfaceObj, textRectObj)


def main():
    # ilklendirmeler
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 680
    player_color = 2  # 1:white, 2:black

    pygame.init()
    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    pygame.display.set_caption('Othello-vs-AI')

    images = Images()

    othelloBoard = OthelloBoard()

    node = OthelloBoardNode(othelloBoard)
    othelloBoardTree = OthelloBoardTree(node)
    othelloBoardTree.expandTree()

    draw(screen, images, othelloBoard)
    pygame.display.update()

    game_continue = True
    winner = None
    # hamlele surelerinin ortalama hesabi icin gerekli
    avg_time = []
    # main loop
    while True:

        # catch events
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONUP:
                if game_continue:
                    set_i = set_j = -1
                    if othelloBoard.player == player_color:
                        px, py = pygame.mouse.get_pos()
                        set_i = (py - othelloBoard.margin) // othelloBoard.width
                        set_j = (px - othelloBoard.margin) // othelloBoard.width
                    # else:
                    #     set_i, set_j = othelloBoardTree.findBestothello(player_color)
                    if (set_i, set_j) in othelloBoard.available:
                        othelloBoardTree.root = othelloBoardTree.root.kids[(
                            set_i, set_j)]
                        othelloBoard = othelloBoardTree.root.othelloBoard
                        # ekran guncellemesi
                        draw(screen, images, othelloBoard)
                        pygame.display.update()
                        # agacin alt katmani olusturuluyor
                        othelloBoardTree.expandTree()
                        # time.sleep(2)
                    if othelloBoard.player == player_color:
                        if len(othelloBoard.available) == 0:
                            game_continue = False
                            winner = None

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_b:
                    # geri alınabilecek müsait hamle var mı kontrolü
                    if othelloBoardTree.root.parent:
                        if othelloBoardTree.root.parent.othelloBoard:
                            game_continue = True
                            winner = None
                            # oyuncunun son hamlesine gelene kadar aradaki bütün ai hamleleri geri alınıyor
                            while othelloBoardTree.root.parent.othelloBoard.player != player_color:
                                othelloBoardTree.root = othelloBoardTree.root.parent
                                othelloBoard = othelloBoardTree.root.othelloBoard

                            othelloBoardTree.root = othelloBoardTree.root.parent
                            othelloBoard = othelloBoardTree.root.othelloBoard

                # ekran guncelleme
                draw(screen, images, othelloBoard)
                pygame.display.update()

                if event.key == pygame.K_r:
                    othelloBoard = OthelloBoard()

                    # agac sifirlaniyor, oyun ilk konumuna alinacak
                    node = OthelloBoardNode(othelloBoard)
                    othelloBoardTree = OthelloBoardTree(node)
                    othelloBoardTree.expandTree()

                    draw(screen, images, othelloBoard)
                    pygame.display.update()

                    game_continue = True
                    winner = None

        # hamle sirasi ai'da
        if othelloBoard.player != player_color and game_continue:
            col = othelloBoard.col
            margin = othelloBoard.margin
            pos = margin * 2 + othelloBoard.width * col
            fontObj = pygame.font.Font(None, images.width)
            textSurfaceObj = fontObj.render("Computer Thinking..", True, (0, 0, 0))
            textRectObj = textSurfaceObj.get_rect()
            textRectObj.center = (pos + 100, pos // 2 + 5 * images.width)
            screen.blit(textSurfaceObj, textRectObj)
            pygame.display.update()

            start = time.time()
            set_i, set_j = othelloBoardTree.findBestMove(player_color)
            end = time.time()
            avg_time.append(end-start)

            #time.sleep(1)

            draw(screen, images, othelloBoard)
            pygame.display.update()

            if (set_i, set_j) in othelloBoard.available:
                print(f'{set_i, set_j} played by AI')
                othelloBoardTree.root = othelloBoardTree.root.kids[(
                    set_i, set_j)]
                othelloBoard = othelloBoardTree.root.othelloBoard
                othelloBoard.ai_last_move = (set_i, set_j)
                # ekran guncelleme
                draw(screen, images, othelloBoard)
                pygame.display.update()
                # asagi dogru bir katman genisletildi
                othelloBoardTree.expandTree()



            elif set_i == -1 and set_j == -1:
                game_continue = False
                winner = None

        if not game_continue and not winner:
            print (f'average time:{sum(avg_time) / len(avg_time)}')
            winner = othelloBoard.getWinner()
            textColor = (0, 0, 0)
            col = othelloBoard.col
            margin = othelloBoard.margin
            pos = margin * 2 + othelloBoard.width * col
            fontObj = pygame.font.Font(None, images.width)
            if winner == "Tie":
                textSurfaceObj = fontObj.render("Game over with Tie ", True, textColor)
            else:
                if player_color == 2 and winner == "Black":
                    textColor = (0, 255, 0)
                else:
                    textColor = (255, 0, 0)
                textSurfaceObj = fontObj.render("Winner: "+ str(winner), True, textColor)
            textRectObj = textSurfaceObj.get_rect()
            textRectObj.center = (pos + 100, pos // 2 + 5 * images.width)
            screen.blit(textSurfaceObj, textRectObj)
            pygame.display.update()

if __name__ == "__main__":
    main()
