import agx
import agxCollide
from agxRender import Color

import math
import snakeapp
from snakeapp.snake_module import Snake

slope_angle = 20


def create_slope() -> agx.RigidBody:
    slope_body = agx.RigidBody(agxCollide.Geometry(agxCollide.Box(1, 1, 0.05)))
    snakeapp.create_visual(slope_body, diffuse_color=Color.Red())
    # slope_body.setPosition(agx.Vec3(0, 0, 0))
    slope_body.setRotation(agx.EulerAngles(0, -math.radians(slope_angle), 0))  # Rotate 30 deg around Y.
    slope_body.setMotionControl(agx.RigidBody.STATIC)
    material = agx.Material("slopeMaterial")
    slope_body.getGeometries()[0].setMaterial(material)
    return slope_body


def build_scene():
    snakeapp.register_additional_scenes('build_scene2')

    slope = create_slope()
    snakeapp.add(slope)

    snake = Snake(5)
    snake.setPosition(0, 0, 0.1)
    snake.setRotation(agx.EulerAngles(0, -math.radians(slope_angle), 0.2))
    snakeapp.add(snake)


def build_scene2():
    slope = create_slope()
    snakeapp.add(slope)

    snake = Snake(5)
    snake.setPosition(0, 0, 0.1)
    snake.setRotation(agx.EulerAngles(0, -math.radians(slope_angle), 0.2))
    snakeapp.add(snake)

    snake_obstacle_cm = snakeapp.sim().getMaterialManager() \
        .getOrCreateContactMaterial(snake.material, slope.getGeometries()[0].getMaterial())  # type: agx.ContactMaterial

    snake_obstacle_cm.setFrictionCoefficient(10)
    snake_obstacle_cm.setYoungsModulus(3E4)
