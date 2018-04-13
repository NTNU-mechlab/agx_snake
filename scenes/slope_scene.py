
import app
from app.snake_with_intermediates import Snake
from app.snake_with_intermediates import ExampleSineMotion

import agx
import agxCollide
import agxRender
import agxSDK

import math


class Obstacle(agxSDK.Assembly):

    def __init__(self, length: float=0.5, angle: float=20):
        super().__init__()

        self._slope_angle = math.radians(angle)

        self.material = agx.Material("obstacle_material_{}".format(self.getUuid().__str__))

        def add_floor():
            h = 0.1
            floor = agxCollide.Geometry(agxCollide.Box(2.5, 0.5, h), agx.AffineMatrix4x4.translate(0, 0, -h))
            app.create_visual(floor, diffuse_color=agxRender.Color.Green())
            # body = agx.RigidBody(floor)
            # body.setMotionControl(agx.RigidBody.STATIC)
            self.add(floor)

        add_floor()

        def add_slope():
            half_extents = agx.Vec3(length, 0.1, 0.005)
            slope = agxCollide.Geometry(agxCollide.Box(half_extents),
                                        agx.AffineMatrix4x4.translate(half_extents.x(), 0, -half_extents.z()))
            slope.setRotation(agx.EulerAngles(0, -self._slope_angle, 0))
            app.create_visual(slope, diffuse_color=agxRender.Color.Red())

            slope.setMaterial(self.material)
            self.add(slope)
            return slope

        self.slope = add_slope()

        def add_box():
            height = math.sin(self._slope_angle) * length
            half_extents = agx.Vec3(0.5, 0.1, height)
            box = agxCollide.Geometry(agxCollide.Box(half_extents), agx.AffineMatrix4x4.translate(0, 0, half_extents.z()))
            box.setParentFrame(self.slope.getParentFrame())
            box.setLocalPosition(0.5 + math.cos(self._slope_angle), 0, 0)
            app.create_visual(box, diffuse_color=agxRender.Color.Yellow())

            box.setMaterial(self.material)
            self.add(box)

        add_box()


def build_scene():

    app.register_additional_scenes('build_scene2')

    angle = 0
    for y in [-1, 0, 1]:

        angle += 10
        obstacle = Obstacle(0.5, angle)
        obstacle.setLocalPosition(0, y, 0)
        app.add(obstacle)

        snake = Snake(5)
        snake.setLocalPosition(-0.1, y, 0.05)
        snake.setLocalRotation(agx.EulerAngles(math.pi / 2, 0, math.pi))
        app.add(snake)

        snake_obstacle_cm = app.sim().getMaterialManager() \
            .getOrCreateContactMaterial(snake.material, obstacle.material)  # type: agx.ContactMaterial

        snake_obstacle_cm.setFrictionCoefficient(2)  # a lower makes contacts more slippery

        snake_obstacle_cm.setUseContactAreaApproach(True)
        snake_obstacle_cm.setYoungsModulus(3E9)

        fm = agx.IterativeProjectedConeFriction(agx.FrictionModel.DIRECT)
        snake_obstacle_cm.setFrictionModel(fm)

        for i in range(0, snake.num_servos):
            sm = ExampleSineMotion(snake, i)
            sm.amplitude = math.radians(45)
            app.add_event_listener(sm)

        import agxSDK

        class ReadSensor(agxSDK.StepEventListener):
            def __init__(self):
                super().__init__(agxSDK.StepEventListener.POST_STEP)

            def post(self, time):
                for i in range(0, snake.num_sensors):
                    print("Sensor{} force={}".format(i, snake.get_force_magnitude_at(i)))
                print()

        app.add_event_listener(ReadSensor())


def build_scene2():

    angle = 0
    for y in [-1, 0, 1]:

        angle += 10
        obstacle = Obstacle(0.5, angle)
        obstacle.setLocalPosition(0, y, 0)
        app.add(obstacle)

        snake = Snake(5)
        snake.setParentFrame(obstacle.slope.getFrame())
        snake.setLocalPosition(snake.len, 0, 0.05)
        snake.setLocalRotation(agx.EulerAngles(math.pi / 2, 0, math.pi))
        app.add(snake)

        snake_obstacle_cm = app.sim().getMaterialManager() \
            .getOrCreateContactMaterial(snake.material, obstacle.material)  # type: agx.ContactMaterial

        snake_obstacle_cm.setFrictionCoefficient(2)  # a lower makes contacts more slippery

        snake_obstacle_cm.setUseContactAreaApproach(True)
        snake_obstacle_cm.setYoungsModulus(3E9)

        fm = agx.IterativeProjectedConeFriction(agx.FrictionModel.DIRECT)
        snake_obstacle_cm.setFrictionModel(fm)

        for i in range(0, snake.num_servos):
            sm = ExampleSineMotion(snake, i)
            sm.amplitude = math.radians(45)
            app.add_event_listener(sm)
