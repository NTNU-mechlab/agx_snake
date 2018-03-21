
from snake import SnakeApp
from snake.snake_module import Snake
from snake.snake_module import ExmapleSineMotion

import agx
import agxCollide
import agxRender
import agxSDK

import math


class Obstacle(agxSDK.Assembly):

    def __init__(self, app: SnakeApp):
        super().__init__()

        self.material = agx.Material("obstacle_material_{}".format(self.getUuid().__str__))

        def add_slope():
            half_extents = agx.Vec3(0.005, 0.1, 0.5)
            slope = agxCollide.Geometry(agxCollide.Box(half_extents), agx.AffineMatrix4x4.translate(half_extents.x(), 0, half_extents.z()))
            slope.setRotation(agx.EulerAngles(0, math.radians(60), 0))
            slope.setPosition(agx.Vec3(-1.365, 0, 0))
            app.create_visual(slope, diffuse_color=agxRender.Color.Red())

            slope.setMaterial(self.material)
            self.add(slope)

        def add_box():
            half_extents = agx.Vec3(0.5, 0.1, 0.25)
            box = agxCollide.Geometry(agxCollide.Box(half_extents), agx.AffineMatrix4x4.translate(0, 0, half_extents.z()))
            app.create_visual(box, diffuse_color=agxRender.Color.Yellow())

            box.setMaterial(self.material)
            self.add(box)

        add_slope()
        add_box()


def create_floor(app: SnakeApp, material: agx.Material=None) -> agxCollide.Geometry:
    height = 0.1
    floor = agxCollide.Geometry(agxCollide.Box(2.5, 1, height), agx.AffineMatrix4x4.translate(0, 0, -height))
    app.create_visual(floor, diffuse_color=agxRender.Color.Green())

    if material is not None:
        floor.setMaterial(material)

    return floor


def build_scene():

    app = SnakeApp()
    app.register_additional_scenes('build_scene2')

    floor = create_floor(app)
    app.add(floor)

    obstacle = Obstacle(app)
    app.add(obstacle)

    snake = Snake(app, 5)
    snake.setRotation(agx.EulerAngles(math.pi / 2, 0, math.pi))
    snake.setPosition(agx.Vec3(-1.45, 0, 0.05))
    app.add(snake)

    snake_obstacle_cm = app.sim.getMaterialManager()\
        .getOrCreateContactMaterial(snake.material, obstacle.material)  # type: agx.ContactMaterial

    snake_obstacle_cm.setFrictionCoefficient(2)  # a lower makes contacts more slippery

    snake_obstacle_cm.setUseContactAreaApproach(True)
    snake_obstacle_cm.setYoungsModulus(3E9)

    fm = agx.IterativeProjectedConeFriction(agx.FrictionModel.DIRECT)
    snake_obstacle_cm.setFrictionModel(fm)

    for i in range(0, snake.num_servos):
        sm = ExmapleSineMotion(snake, i)
        sm.period = 1
        sm.amplitude = math.radians(35)
        app.add_event_listener(sm)


def build_scene2():

    app = SnakeApp()

    floor = create_floor(app)
    app.add(floor)

    obstacle = Obstacle(app)
    app.add(obstacle)

    snake = Snake(app, 5)
    snake.setRotation(agx.EulerAngles(math.pi / 2, math.radians(30), math.pi))
    snake.setPosition(agx.Vec3(-1, 0, 0.3))
    app.add(snake)

    snake_obstacle_cm = app.sim.getMaterialManager()\
        .getOrCreateContactMaterial(snake.material, obstacle.material)  # type: agx.ContactMaterial

    snake_obstacle_cm.setFrictionCoefficient(2)  # a lower makes contacts more slippery

    snake_obstacle_cm.setUseContactAreaApproach(True)
    snake_obstacle_cm.setYoungsModulus(3E9)

    fm = agx.IterativeProjectedConeFriction(agx.FrictionModel.DIRECT)
    snake_obstacle_cm.setFrictionModel(fm)

    for i in range(0, snake.num_servos):
        sm = ExmapleSineMotion(snake, i)
        sm.amplitude = math.radians(45)
        app.add_event_listener(sm)


