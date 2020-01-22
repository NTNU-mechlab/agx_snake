
import snakeapp
from snakeapp import load_shape
from snakeapp import create_constraint

import agx
import agxSDK
import agxCollide
import agxRender

import math

module_len = 0.085
servo_shape = load_shape('assets/76mm_new/servo.obj')
bottom_shape = load_shape('assets/76mm_new/bottom.obj')
upper_shape = load_shape('assets/76mm_new/upper.obj')
camera_shape = load_shape('assets/76mm_new/camera.obj')


class Snake(agxSDK.Assembly):

    def __init__(self, num_modules: int, pitch_only=False, with_camera=False):
        super().__init__()

        self.modules = []

        for i in range(0, num_modules):
            module = SnakeModule(with_camera)
            module.setPosition(module_len*i, 0, 0)
            module.setRotation(agx.EulerAngles(math.pi / 2, 0, 0))

            if not pitch_only:
                if i % 2 != 0:
                    module.setRotation(agx.EulerAngles(0, 0, 0))

            if i > 0:
                merged_body = agx.MergedBody()
                merged_body.add(agx.MergedBodyEmptyEdgeInteraction(self.modules[i - 1].upper, module.bottom))
                snakeapp.add(merged_body)

            self.modules.append(module)
            self.add(module)


class SnakeModule(agxSDK.Assembly):

    def __init__(self, with_camera):
        super().__init__()

        servo = agxCollide.Geometry(servo_shape.deepCopy())
        servo.setEnableCollisions(False)
        snakeapp.create_visual(servo, diffuse_color=agxRender.Color.Black())

        self.bottom = agx.RigidBody(agxCollide.Geometry(bottom_shape.deepCopy()))
        self.bottom.add(servo)
        snakeapp.create_visual(self.bottom, agxRender.Color.Orange())

        if with_camera:
            self.upper = agx.RigidBody(agxCollide.Geometry(camera_shape.deepCopy()))
        else:
            self.upper = agx.RigidBody(agxCollide.Geometry(upper_shape.deepCopy()))
        snakeapp.create_visual(self.upper, agxRender.Color.Orange())

        self.hinge = create_constraint(
            pos=agx.Vec3(0.005, 0.0, 0), axis=agx.agx.Vec3(0, 0, -1),
            rb1=self.bottom, rb2=self.upper, c=agx.Hinge)  # type: agx.Hinge

        self.hinge.setCompliance(1E-12)
        self.hinge.getMotor1D().setCompliance(1E-10)
        self.hinge.getMotor1D().setEnable(True)
        self.hinge.getLock1D().setEnable(False)
        self.hinge.getRange1D().setRange(-math.pi/2, math.pi/2)

        self.add(self.bottom)
        self.add(self.hinge)
        self.add(self.upper)

