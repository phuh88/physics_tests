import time
import pygame, sys, random
import pygame._sdl2 as sdl2

WIDTH = 288
HEIGHT = 240
TILESIZE = 16
NEIGHBOR_OFFSETS_PLAYER = [(-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (0, 2), (1, -1), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1)]

class PhysicsEntity:
    def __init__(self, pos):
        self.pos = list(pos)
        self.speed = 2
        self.acc = 0.05
        self.dec = .9
        self.vel = [0, 0]
        self.change = [0, 0]
        self.collisions = {'top': False, 'bottom': False, 'right': False, 'left': False}

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], 16, 16)

    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'top': False, 'bottom': False, 'right': False, 'left': False}

        # initiate movement
        if movement[0] > 0:
            self.vel[0] = self.acc
        if movement[0] < 0:
            self.vel[0] = -self.acc
        if movement[1] > 0:
            self.vel[1] = self.acc
        if movement[1] < 0:
            self.vel[1] = -self.acc

        # initiate stopping
        if movement[0] == 0:
            self.vel[0] = 0
        if movement[1] == 0:
            self.vel[1] = 0

        # limit speed
        self.change[0] += self.vel[0]
        if abs(self.change[0]) >= self.speed:
            self.change[0] = self.change[0] / abs(self.change[0]) * self.speed
        self.change[1] += self.vel[1]
        if abs(self.change[1]) >= self.speed:
            self.change[1] = self.change[1] / abs(self.change[1]) * self.speed

        # normalize diagonal speed
        mag = (self.change[0]**2 + self.change[1]**2)**0.5
        if mag >= self.speed:
            self.change[0] = (self.change[0] / mag) * self.speed
            self.change[1] = (self.change[1] / mag) * self.speed
        # print(mag)

        # decelerate
        if self.vel[0] == 0:
            self.change[0] *= self.dec
        if self.vel[1] == 0:
            self.change[1] *= self.dec

        # slowness threshold to zero
        if abs(self.change[0]) < 0.01:
            self.change[0] = 0
        if abs(self.change[1]) < 0.01:
            self.change[1] = 0

        # change position
        self.pos[0] += self.change[0]
        self.pos[1] += self.change[1]

        # collisions
        entity_rect = self.rect()
        for rect in tilemap.rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if self.change[0] > 0:
                    self.change[0] = 0
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if self.change[0] < 0:
                    self.change[0] = 0
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x

        entity_rect = self.rect()
        for rect in tilemap.rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if self.change[1] > 0:
                    self.change[1] = 0
                    entity_rect.bottom = rect.top
                    self.collisions['bottom'] = True
                if self.change[1] < 0:
                    self.change[1] = 0
                    entity_rect.top = rect.bottom
                    self.collisions['top'] = True
                self.pos[1] = entity_rect.y

        print(self.collisions)

    def render(self, surf):
        pygame.draw.rect(surf, (255, 255, 255), (self.pos[0], self.pos[1], TILESIZE, TILESIZE))

class Block:
    def __init__(self, game, size, amt):
        self.game = game
        self.size = size
        self.amt = amt
        self.tilemap = {}
        self.tilemap_proximity = []

        for i in (self.random_pos()):
            self.tilemap[i[0], i[1]] = pygame.Rect(i[0] * TILESIZE, i[1] * TILESIZE, self.size[0], self.size[1])
        print(self.tilemap)

    def random_pos(self):
        random_pos = []
        for i in range(self.amt):
            random_pos.append((random.randrange(int(WIDTH // TILESIZE)), random.randrange(int(HEIGHT // TILESIZE))))
        print(random_pos)
        return random_pos

    def proximity(self, pos):
        tiles = []
        tile_pos = (int(pos[0] // TILESIZE), int(pos[1] // TILESIZE))
        for offset in NEIGHBOR_OFFSETS_PLAYER:
            check_pos = ((tile_pos[0] + offset[0]), (tile_pos[1] + offset[1]))
            if check_pos in self.tilemap.keys():
                tiles.append(self.tilemap[check_pos])
        return tiles

    def rects_around(self, pos):
        rects = []
        for tile in self.proximity(pos):
            if tile not in self.tilemap_proximity:
                self.tilemap_proximity.append(pygame.Rect(tile[0], tile[1], self.size[0], self.size[1]))
                rects.append(pygame.Rect(tile[0], tile[1], self.size[0], self.size[1]))
            print(rects)
        return rects


    def render(self, surf):
        for block in self.tilemap.values():
            pygame.draw.rect(surf, (80, 80, 80), block)
        for block in self.tilemap_proximity:
            pygame.draw.rect(surf, (0, 180, 220), block)
        # print(self.tilemap_proximity)
        self.tilemap_proximity = []

class Game:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), flags=pygame.SCALED | pygame.HIDDEN)
        window =sdl2.Window.from_display_module()
        window.size = (WIDTH * 3, HEIGHT * 3)
        window.position = sdl2.WINDOWPOS_CENTERED
        window.show()

        self.player = PhysicsEntity((50, 50))
        self.movement = [False, False, False, False]
        self.dt = 1
        self.last_time = time.time()
        self.blocks = Block(self, (16, 16), 8)

    def run(self):
        while True:
            self.screen.fill((0, 0, 0))

            self.blocks.render(self.screen)

            self.player.update(self.blocks, [self.movement[1] - self.movement[0], self.movement[3] - self.movement[2]])
            self.player.render(self.screen)

            self.dt = (time.time() - self.last_time)
            self.last_time = time.time()

            # pygame.draw.rect(self.screen, (255, 255, 255), self.player)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_s:
                        self.movement[3] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        self.movement[3] = False


            pygame.display.update()
            self.clock.tick(60)

if __name__ == '__main__':
    Game().run()




