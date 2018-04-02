
from snake import SnakeApp
from snake.snake_module import Snake

import agx
import agxCollide
import agxRender


def build_scene():  # application entry point. Do not change method signature
    app = SnakeApp()

    snake1 = Snake(app, num_modules=5, pitch_only=True)
    snake1.setLocalPosition(0, -0.1, 0)
    app.add(snake1)

    snake2 = Snake(app, num_modules=5, pitch_only=False)
    snake2.setLocalPosition(0, 0.1, 0)
    app.add(snake2)

    plane = agxCollide.Geometry(agxCollide.Box(2, 2, 0.1), agx.AffineMatrix4x4.translate(0, 0, -0.1 / 2))
    app.create_visual(plane, diffuse_color=agxRender.Color.Green())
    app.add(plane)

