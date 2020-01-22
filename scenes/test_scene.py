
import snakeapp
from snakeapp.snake_module import Snake
from snakeapp.snake_module_new import Snake as Snake2

import agx
import agxCollide
import agxRender


def build_scene():  # application entry point. Do not change method signature

    snake1 = Snake(num_modules=5, pitch_only=True)
    snake1.setLocalPosition(0, -0.1, 0)
    snakeapp.add(snake1)

    snake2 = Snake(num_modules=5, pitch_only=False)
    snake2.setLocalPosition(0, 0.1, 0)
    snakeapp.add(snake2)

    snake3 = Snake2(num_modules=5, pitch_only=False, with_camera=True)
    snake3.setLocalPosition(0, 0.4, 0)
    snakeapp.add(snake3)

    plane = agxCollide.Geometry(agxCollide.Box(2, 2, 0.1), agx.AffineMatrix4x4.translate(0, 0, -0.1 / 2))
    snakeapp.create_visual(plane, diffuse_color=agxRender.Color.Green())
    snakeapp.add(plane)

