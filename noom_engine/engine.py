from .player import *
from .map_generator import *
from .exceptions import *
from .colors import *
from math import tan, pi, cos, sin


class NoomEngine:
    def __init__(self,
                 screen_width=1800, screen_height=1200,
                 fps=1000, tile_size=100, fov=pi / 2,
                 rays_count=900, view_distance=5000,
                 text_map=None, player=None,
                 window_caption="Noom"
                 ):
        self.WIDTH = screen_width
        self.HEIGHT = screen_height
        self.FPS = fps
        self.TILE_SIZE = tile_size
        self.FOV = fov
        self.RAYS_COUNT = rays_count
        self.VIEW_DEPTH = view_distance
        self.WINDOW_CAPTION = window_caption

        #  Создание более оптимизированной карты из списка. Фактически указываются лишь стены.
        #  Скорее всего придётся заменить, когда будем добавлять врагов и всякое такое
        self.MAP = Map(self.TILE_SIZE, text_map).create_map()

        if player is None:
            x = self.WIDTH // 2 - self.TILE_SIZE
            y = self.HEIGHT // 2 - self.TILE_SIZE
            self.PLAYER = Player(start_x=x, start_y=y)
        else:
            self.PLAYER = player

        #  Параметры для трассировки лучей, которые зависят от поля зрения и разрешения
        self.ANGLE_DELTA = self.FOV / self.RAYS_COUNT
        self.DIST = self.RAYS_COUNT / (2 * tan(self.FOV / 2))
        self.RATIO = self.DIST * self.TILE_SIZE
        self.GRAPHICS_SCALE = self.WIDTH / self.RAYS_COUNT

        self.screen = None
        self.clock = pygame.time.Clock()

    #  Функция инициализации. Обязательна для запуска игры
    def init(self):
        pygame.init()
        pygame.mouse.set_visible(False)
        pygame.display.set_caption(self.WINDOW_CAPTION)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

    #  Функция, которая проверяет, являются ли координаты стеной
    def mapping(self, a, b) -> tuple:
        return (a // self.TILE_SIZE) * self.TILE_SIZE, (b // self.TILE_SIZE) * self.TILE_SIZE

    def ray_cast(self) -> list:
        x0, y0 = self.PLAYER.pos
        x_max, y_max = self.mapping(x0, y0)
        current_angle = self.PLAYER.angle - self.FOV / 2
        rects = []
        #  Перебор каждого луча
        for ray in range(self.RAYS_COUNT):
            sin_a = sin(current_angle)
            cos_a = cos(current_angle)

            #  Тут уже начинается трассировка, пока что мне лень её полностью описывать =)
            if cos_a >= 0:
                x = x_max + self.TILE_SIZE
                x_d = 1
            else:
                x = x_max
                x_d = -1

            depth_v = None

            for i in range(0, self.WIDTH, self.TILE_SIZE):
                depth_v = (x - x0) / cos_a
                y = y0 + depth_v * sin_a
                if self.mapping(x + x_d, y) in self.MAP:
                    break
                x += x_d * self.TILE_SIZE

            if sin_a >= 0:
                y = y_max + self.TILE_SIZE
                y_d = 1
            else:
                y = y_max
                y_d = -1

            depth_h = None

            for i in range(0, self.HEIGHT, self.TILE_SIZE):
                depth_h = (y - y0) / sin_a
                x = x0 + depth_h * cos_a
                if self.mapping(x, y + y_d) in self.MAP:
                    break
                y += y_d * self.TILE_SIZE

            depth = min(depth_v, depth_h)
            depth *= cos(self.PLAYER.angle - current_angle)

            if not depth:
                depth = 1

            height = self.RATIO / depth

            #  Тут формируется цвет в зависимости от расстояния для стены (дальше - темнее).
            #  Можно попробовать поиграться с цветами
            color_multiplier = 0.00001
            color_ = 200 / (1 + (depth ** 2) * color_multiplier)
            color = (color_, color_, color_)

            #  Запоминаем параметры прямоугольника, который потом будем рисовать. Каждый rect в rects - часть стен
            rects.append(
                ((ray * self.GRAPHICS_SCALE, self.HEIGHT / 2 - height // 2, self.GRAPHICS_SCALE, height), color)
            )
            current_angle += self.ANGLE_DELTA
        return rects

    #  Функция для отрисовки ФПС, ничего необычного
    def render_fps_counter(self, x, y, font_size=26):
        font = pygame.font.Font(None, font_size)
        text_surface = font.render(str(round(self.clock.get_fps(), 2)), True, RED)
        self.screen.blit(text_surface, (x, y))

    #  Основной игровой цикл
    def mainloop(self):
        #  Если не была проведеня инициализация, то вылетит ошибка
        if self.screen is None:
            raise EngineNotInitialized("Engine was not initialized")

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

            #  Заливаем экран чёрным и запускаем функцию передвижения игрока
            self.screen.fill(BLACK)
            self.PLAYER.movement(self.MAP)

            #  Рисуем небо и пол
            self.screen.fill(BLUE, (0, 0, self.WIDTH, self.HEIGHT // 2))
            self.screen.fill(BLACK, (0, self.HEIGHT // 2, self.WIDTH, self.HEIGHT))

            #  Тут получаем все стены и рисуем каждую из них
            walls = self.ray_cast()
            for wall in walls:
                pygame.draw.rect(self.screen, wall[1], wall[0])

            #  Это закоментированная отрисовка двумерной проекции.
            #  Может в будущем послужить основной для миникарты
            # pygame.draw.circle(self.screen, GREEN, self.PLAYER.pos, 15)
            # pygame.draw.line(self.screen, WHITE, self.PLAYER.pos, (self.PLAYER.x * self.WIDTH * cos(self.PLAYER.angle),
            #                                                        self.PLAYER.y * self.WIDTH * sin(self.PLAYER.angle)))
            #
            # for x, y in self.MAP:
            #     pygame.draw.rect(self.screen, GREEN, (x, y, self.TILE_SIZE, self.TILE_SIZE), 1)

            #  Отрисовываем счётчик ФПС
            self.render_fps_counter(self.WIDTH - 50, self.HEIGHT - 30)

            pygame.display.flip()
            self.clock.tick(self.FPS)
