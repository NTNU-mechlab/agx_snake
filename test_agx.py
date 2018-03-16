
import agx_helper
import snake_module

import agx
import agxSDK
import agxRender
import agxCollide

import math


def create_plane(app):
    plane = agxCollide.Geometry(agxCollide.Box(1, 1, 0.1),
                                     agx.AffineMatrix4x4.translate(0, 0, -0.1 / 2))

    app.create_visual(plane, diffuse_color=agxRender.Color.Green())
    app.add(plane)
    return plane


def build_scene():  # application entry point. Do not change method signature

    app = agx_helper.AgxApp(num_threads=2)
    app.register_additional_scenes('build_scene_2')

    pitch_only = False
    snake = snake_module.Snake(app, 5, pitch_only)
    if pitch_only:
        snake.setRotation(agx.EulerAngles(-math.pi / 2, 0, 0))
    snake.setPosition(agx.Vec3(0, 0, 0.1))
    app.add(snake)

    plane = create_plane(app)

    app.init_camera(eye=agx.Vec3(-1, -1, 0.5), center=plane.getPosition())

    class SineMotion(agxSDK.StepEventListener):

        def __init__(self, module_index, num_modules):
            super().__init__(agxSDK.StepEventListener.PRE_STEP)

            period = 2
            f = 1/period
            self.omega = 2 * math.pi * f
            self.amplitude = math.radians(45)

            t = (1/(num_modules-2))*module_index
            v0 = 0
            v1 = math.pi*2

            self.phase = (1-t) * v0 + t * v1
            print("module{} phase={}".format(module_index, math.degrees(self.phase)))

            self.hinge = snake.modules[module_index].hinge

        def pre(self, time):
            speed = self.amplitude * math.sin(self.omega * time + self.phase)
            self.hinge.getMotor1D().setSpeed(-speed)

    for i in range(0, snake.num_modules):
        if pitch_only:
            app.add_event_listener(SineMotion(i, snake.num_modules))
        elif i % 2 == 0:
            app.add_event_listener(SineMotion(i, snake.num_modules))




# gets invoked when pressing 2 in the agxViewer
def build_scene_2():

    app = agx_helper.AgxApp(num_threads=2)
    app.register_additional_scenes('build_scene_2')

    box_body = agx.RigidBody(agxCollide.Geometry(agxCollide.Box(0.5, 0.5, 0.5)))
    app.create_visual(box_body, diffuse_color=agxRender.Color.Yellow())
    app.add(box_body)

    plane_body = agx.RigidBody(agxCollide.Geometry(agxCollide.Box(10, 10, 0.1)))
    plane_body.setPosition(0, 0, -5)
    plane_body.setMotionControl(agx.RigidBody.STATIC)
    app.create_visual(plane_body)
    app.add(plane_body)
