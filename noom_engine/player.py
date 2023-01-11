import pygame
from math import sin, cos, radians


class Player:
    def __init__(self, start_x=3, start_y=3, tile_size=100, start_angle=0, movement_speed=2, jump_force=2, gravity=0.1,
                 mouse_sensitive=0.01):
        self.x = start_x
        self.y = start_y
        self.angle = start_angle

        self.speed = movement_speed
        self.jump_force = jump_force
        self.gravity = gravity
        self.height = 0
        self.vel = [0, 0]

        self.mouse_sensitive = mouse_sensitive

        self.tile_size = tile_size

    #  Два свойста для получения позиции. Сделал, потому что могу =)
    @property
    def pos(self):
        return self.x, self.y

    @property
    def position(self):
        return self.x, self.y

    #  Копия функции из engine.py. Потом надо будет их объединить
    def mapping(self, a, b) -> tuple:
        return (a // self.tile_size) * self.tile_size, (b // self.tile_size) * self.tile_size

    #  Просчёт направления движения с учётом поворота камеры
    #  Не уверен, что она идеальна, но лучше я ничего не придумал
    @staticmethod
    def calculate_direction(raw_direction, angle, axis) -> list:
        direction = [0, 0]
        if axis == "z":
            direction[0] += cos(angle) * raw_direction[0]
            direction[1] += sin(angle) * raw_direction[1]
        elif axis == "x":
            direction[0] += sin(angle) * raw_direction[0]
            direction[1] += cos(angle) * raw_direction[1]
        return direction

    #  Основная функция передвижения игрока
    def movement(self, map_):
        keys = pygame.key.get_pressed()

        direction = [0, 0]
        velocity = [0, 0]

        axis = set()

        if self.height > 0:# and not self.vel[1]:
            self.vel[1] -= self.gravity
        elif self.height < 0:
            self.height = 0
            self.vel[1] = 0

        if keys[pygame.K_SPACE] and self.height == 0:
            self.vel[1] = self.jump_force

        if self.vel[1]:
            self.height += self.vel[1] // self.gravity
            self.vel[1] -= self.gravity

        if keys[pygame.K_w]:
            #  Если кратко, то принцип следующий:
            #  в зависимости от нажатых кнопок устанавливаем "сырое" направление,
            #  затем изменяем его в зависимости от поворота камеры.
            #  В целом, тут несложно разобраться
            axis.add("z")

            direction[0] = 1
            direction[1] = 1

            dir_ = self.calculate_direction(direction, self.angle, "z")

            velocity[0] += dir_[0]
            velocity[1] += dir_[1]

        if keys[pygame.K_s]:
            axis.add("z")

            direction[0] = -1
            direction[1] = -1

            dir_ = self.calculate_direction(direction, self.angle, "z")

            velocity[0] += dir_[0]
            velocity[1] += dir_[1]

        if keys[pygame.K_d]:
            axis.add("x")

            direction[0] = -1
            direction[1] = 1

            dir_ = self.calculate_direction(direction, self.angle, "x")

            velocity[0] += dir_[0]
            velocity[1] += dir_[1]

        if keys[pygame.K_a]:
            axis.add("x")

            direction[0] = 1
            direction[1] = -1

            dir_ = self.calculate_direction(direction, self.angle, "x")

            velocity[0] += dir_[0]
            velocity[1] += dir_[1]

        if velocity:
            x_ = velocity[0] * self.speed
            y_ = velocity[1] * self.speed

            #  Если не стена, то идти можно
            if self.mapping(self.x + x_, self.y + y_) not in map_:
                self.x += x_
                self.y += y_
            #  Тут я попытался реализовать скольжение у стены. Т.е. если ты прижат к стене, то можно попытаться чуть
            #  повернуть камеру и пойти вдоль стены. Работает, но пока что камера дёргается.
            else:
                for deg in range(-15, 16):
                    angle = radians(deg)
                    velocity = [0, 0]

                    for axis_ in axis:
                        dir_ = self.calculate_direction(direction, self.angle + angle, axis_)
                        velocity[0] += dir_[0]
                        velocity[1] += dir_[1]

                    x_ = velocity[0] * self.speed
                    y_ = velocity[1] * self.speed

                    if self.mapping(self.x + x_, self.y + y_) not in map_:
                        self.x += x_
                        self.y += y_
                        break

        #  Ну а тут мышкой кручу камеру по горизонтали. Всё ещё не уверен, хорошая ли идея поворочиваться мышкой
        mouse_pos_relative = pygame.mouse.get_rel()
        if mouse_pos_relative:
            self.angle += mouse_pos_relative[0] * self.mouse_sensitive
