
import snakeapp
from snakeapp.snake_module_new import Snake
from snakeapp.snake_control import *

import agx
import agxRender
import agxCollide

import math

NUM_SNAKE_MODULES = 5


def setup_scene(i: int):

    snake = Snake(NUM_SNAKE_MODULES, pitch_only=False, with_camera=True)  # type: Snake
    snake.setPosition(agx.Vec3(0, 0, 0.1))
    snakeapp.add(snake)

    plane_body = agx.RigidBody(
        agxCollide.Geometry(agxCollide.Box(2, 2, 0.1), agx.AffineMatrix4x4.translate(0, 0, -0.1 / 2)))

    plane_body.setMotionControl(agx.RigidBody.STATIC)
    snakeapp.create_visual(plane_body, diffuse_color=agxRender.Color.Green())
    snakeapp.add(plane_body)

    snake_controller = SnakeControl(snake)

    if i == FLAPPING:
        snake_controller.init_flapping(math.pi / 9.0, math.pi / 9.0, 16.0, -math.pi * 5.0 / 180.0)
    elif i == TURNING:
        snake_controller.init_turning(math.pi / 9.0, math.pi * 2.0 / 3.0, 8.0, 0.0, math.pi * 20.0 / 180.0)
    elif i == SIDEWINDING:
        snake_controller.init_sidewinding(math.pi / 9.0, math.pi * 2.0 / 3.0, 16.0)
    elif i == ROLLING:
        snake_controller.init_rolling(math.pi / 6.0, math.pi / 6.0, 16.0)
    elif i == ROTATING:
        snake_controller.init_rotating(math.pi / 6.0, math.pi / 6.0, 16.0)

    snakeapp.add_event_listener(snake_controller)

    snakeapp.init_camera(eye=agx.Vec3(-1, -1, 0.5), center=plane_body.getPosition())


def build_scene():  # application entry point. Do not change method signature
    snakeapp.register_additional_scenes('build_scene_2', 'build_scene_3', 'build_scene_4', 'build_scene_5')
    setup_scene(FLAPPING)


def build_scene_2():  # application entry point. Do not change method signature
    setup_scene(TURNING)


def build_scene_3():  # application entry point. Do not change method signature
    setup_scene(SIDEWINDING)


def build_scene_4():  # application entry point. Do not change method signature
    setup_scene(ROLLING)


def build_scene_5():  # application entry point. Do not change method signature
    setup_scene(ROTATING)