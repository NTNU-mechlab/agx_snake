
import agx_helper

import agx
import agxSDK
import agxRender
import agxCollide

import math

module_len = 0.0725
intermediate_len = 0.025
servo_shape = agx_helper.load_shape('assets/servo.obj')
bottom_shape = agx_helper.load_shape('assets/bottom.obj')
upper_shape = agx_helper.load_shape('assets/upper.obj')
intermediate_shape = agx_helper.load_shape('assets/intermediate.obj')

intermediate_bounds = agx.Vec3(0.0125, 0.0325, 0.0325)


class Intermediate(agx.RigidBody):

    def __init__(self, app):
        super().__init__()

        visual_geometry = agxCollide.Geometry(intermediate_shape.deepCopy())
        visual_geometry.setEnableCollisions(False)
        app.create_visual(visual_geometry, agxRender.Color.Orange())

        x = 0.0125; y = 0.035; z = 0.035
        collision_geometry = agxCollide.Geometry(agxCollide.Box(x, y, z),
                                                 agx.AffineMatrix4x4.translate(-module_len / 2 - x, 0, 0))

        self.add(visual_geometry)
        self.add(collision_geometry)

class BottomPart(agx.RigidBody):

    def __init__(self, app):
        super().__init__()
        g1 = agxCollide.Geometry(bottom_shape.deepCopy())
        g1.setEnableCollisions(False)
        app.create_visual(g1, agxRender.Color.Black())

        t = agx.AffineMatrix4x4.rotate(math.pi/2, 0, 1, 0) \
            * agx.AffineMatrix4x4.translate(-module_len/2 - intermediate_len, 0, 0)

        g2 = agxCollide.Geometry(intermediate_shape.deepCopy(), t)
        g2.setEnableCollisions(False)
        app.create_visual(g2, agxRender.Color.Orange())

        collision_geometry = agxCollide.Geometry(
            agxCollide.Box(intermediate_bounds), agx.AffineMatrix4x4.translate(-module_len/2 - intermediate_bounds.x(), 0, 0))

        servo_geometry = agxCollide.Geometry(servo_shape.deepCopy())
        servo_geometry.setEnableCollisions(False)
        app.create_visual(servo_geometry, diffuse_color=agxRender.Color.Gray())

        self.add(g1)
        self.add(g2)
        self.add(collision_geometry)
        self.add(servo_geometry)


class UpperPart(agx.RigidBody):

    def __init__(self, app, is_end=False):
        super().__init__()

        g = agxCollide.Geometry(upper_shape.deepCopy())
        g.setEnableCollisions(False)
        app.create_visual(g, agxRender.Color.Black())
        self.add(g)

        if is_end:
            t = agx.AffineMatrix4x4.rotate(-math.pi / 2, 0, 1, 0) * agx.AffineMatrix4x4.translate(
                module_len / 2 + intermediate_len, 0, 0)
            g2 = agxCollide.Geometry(intermediate_shape.deepCopy(), t)
            g2.setEnableCollisions(False)
            app.create_visual(g2, agxRender.Color.Orange())
            self.add(g2)

            collision_geometry = agxCollide.Geometry(
                agxCollide.Box(intermediate_bounds), agx.AffineMatrix4x4.translate(module_len / 2 + intermediate_bounds.x(), 0, 0))
            self.add(collision_geometry)


class SnakeModule(agxSDK.Assembly):

    def __init__(self, app, is_end=False):
        super().__init__()

        self.is_end = is_end

        self.bottom = BottomPart(app)
        self.upper = UpperPart(app, is_end)

        self.add(self.bottom)
        self.add(self.upper)

        self.hinge = agx_helper.create_constraint(pos=agx.Vec3(0.0, 0.007, 0), axis=agx.agx.Vec3(0, 0, -1),
                                                  rb1=self.bottom, rb2=self.upper,
                                                  c=agx.Hinge)  # type: agx.Hinge

        self.hinge.setCompliance(1E-12)
        self.hinge.getMotor1D().setCompliance(1E-10)
        self.hinge.getMotor1D().setEnable(True)
        self.hinge.getLock1D().setEnable(False)

        self.add(self.hinge)


class Snake(agxSDK.Assembly):

    def __init__(self, app, num_modules, pitch_only=False):
        super().__init__()

        self.modules = []
        self.intermediates = []

        for i in range(0, num_modules):
            module = SnakeModule(app, i == num_modules-1)
            module.setPosition((module_len+intermediate_len)*i, 0, 0)
            if not pitch_only and i % 2 == 0:
                module.setRotation(agx.EulerAngles(math.pi/2, 0, 0))

            if i > 0:
                merged_body = agx.MergedBody()
                app.add(merged_body)
                merged_body.add(agx.MergedBodyEmptyEdgeInteraction(self.modules[i-1].upper, module.bottom))

            self.modules.append(module)
            self.add(module)

        self.num_modules = len(self.modules)


def build_scene():

    import agxCollide

    app = agx_helper.AgxApp()
    app.register_additional_scenes('build_scene_2')

    module1 = SnakeModule(app, True)
    module1.setPosition(agx.Vec3(0, 0, 0.1))
    app.add(module1)

    plane_body = agx.RigidBody(agxCollide.Geometry(agxCollide.Box(1, 1, 0.1), agx.AffineMatrix4x4.translate(0, 0, -0.1/2)))

    plane_body.setMotionControl(agx.RigidBody.STATIC)
    app.create_visual(plane_body, diffuse_color=agxRender.Color.Green())
    app.add(plane_body)

    app.init_camera(eye=agx.Vec3(-1, -1, 0.5), center=plane_body.getPosition())


def build_scene_2(): #application entry point. Do not change method signature

    import agxCollide

    app = agx_helper.AgxApp()

    snake = Snake(app, 4, True)
    snake.setRotation(agx.EulerAngles(math.pi/2, 0, 0))
    snake.setPosition(agx.Vec3(0, 0, 0.1))
    app.add(snake)

    plane_body = agx.RigidBody(agxCollide.Geometry(agxCollide.Box(1, 1, 0.1), agx.AffineMatrix4x4.translate(0, 0, -0.1/2)))

    plane_body.setMotionControl(agx.RigidBody.STATIC)
    app.create_visual(plane_body, diffuse_color=agxRender.Color.Green())
    app.add(plane_body)

    app.init_camera(eye=agx.Vec3(-1, -1, 0.5), center=plane_body.getPosition())