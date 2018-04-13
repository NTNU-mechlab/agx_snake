
import app
from app.snake_module import Snake
from app.snake_control import *

import agx
import agxSDK
import agxRender
import agxCollide

import math


NUM_SNAKE_MODULES = 5

ANGLE_ERROR = math.pi*4.0/180.0
MAX_SPD = math.pi/3.0/0.23
KP = 12
REACHED = 1
NOT_REACHED = 0


SNAKE_BALL_ANGLE_ERROR = math.pi*5.0/180.0


class MyKeyEvent(agxSDK.GuiEventListener):

    interval = 0.01

    def __init__(self, ball):
        super().__init__(agxSDK.GuiEventListener.KEYBOARD)
        self.ball = ball

    def keyboard(self, key, alt, x, y, down):
        handled = False
        if key == agxSDK.GuiEventListener.KEY_Down:
            self.ball.setPosition(self.ball.getPosition() + agx.Vec3(-self.interval, 0, 0))
            handled = True
        elif key == agxSDK.GuiEventListener.KEY_Up:
            self.ball.setPosition(self.ball.getPosition() + agx.Vec3(self.interval, 0, 0))
            handled = True
        elif key == agxSDK.GuiEventListener.KEY_Left:
            self.ball.setPosition(self.ball.getPosition() + agx.Vec3(0, self.interval, 0))
            handled = True
        elif key == agxSDK.GuiEventListener.KEY_Right:
            self.ball.setPosition(self.ball.getPosition() + agx.Vec3(0, -self.interval, 0))
            handled = True
        return handled


class SnakeBallControl(SnakeControl):

    def __init__(self, snake, ball):
        super().__init__(snake)
        self.ball = ball
        self.snakeFile_ID = open("snake_pos.txt", "w")

    def pre(self, tt):
        super().pre(tt)

        ball_pos = self.ball.getPosition()
        snake_head_pos = self.snake.modules[0].bottom.getPosition()
        snake_center_pos = self.snake.modules[2].bottom.getPosition()
        snake_tail_pos = self.snake.modules[4].bottom.getPosition()

        self.snakeFile_ID.write("{0:.3f}\t".format(tt) +
                                      "{0:.3f}\t".format(snake_center_pos.x()) +
                                      "{0:.3f}\t".format(snake_center_pos.y()) +
                                      "{0:.3f}\n".format(snake_center_pos.z()))
        # print("{0:.3f}\t".format(tt) + "{0:.3f}\t".format(snake_center_pos.x())
        #      + "{0:.3f}\t".format(snake_center_pos.y()) + "{0:.3f}\n".format(snake_center_pos.z()))

        U = agx.Vec2(snake_head_pos.x() - snake_tail_pos.x(),
                     snake_head_pos.y() - snake_tail_pos.y())  # snake_orientation
        V = agx.Vec2(ball_pos.x() - snake_center_pos.x(),
                     ball_pos.y() - snake_center_pos.y())  # snake-ball relative orientation

        snake_ball_relative_angle = math.acos(U * V / (U.length() * V.length()))
        # print("snake_ball_relative_angle:{}".format(math.radians(snake_ball_relative_angle)))
        if snake_ball_relative_angle > SNAKE_BALL_ANGLE_ERROR:  # this means the snake need to rotate
            # U × V cross product: U=u1i+u2j+u3k, V=v1i+v2j+v3k
            # U × V = (u2v3-u3v2)i + (u3v1-u1v3)j + (u1v2-u2v1)k
            # checking (u1v2-u2v1)k can determine clockwise/counterclockwise rotation gait
            if U.x() * V.y() - U.y() * V.x() > 0:  # (u1v2-u2v1)>0 means the cross product direction is along the positive z axis
                # then the snake should make a counterclockwise rotation gait
                if self.prev_gait != CW_ROTATING:
                    # print("should counterclockwise rotation")
                    self.init_counterclockwise_rotating(math.pi / 9.0, math.pi / 9.0, 16.0)
                    self.prev_gait = CW_ROTATING
            else:
                if self.prev_gait != CCW_ROTATING:
                    # print("should clockwise rotation")
                    self.init_clockwise_rotating(math.pi / 9.0, math.pi / 9.0, 16.0)
                    self.prev_gait = CCW_ROTATING
        else:
            # print("should forward motion")
            if self.prev_gait != TURNING:
                self.init_turning(math.pi / 9.0, math.pi * 2.0 / 3.0, 8.0, 0.0, math.pi * 0.0 / 180.0)
                self.prev_gait = TURNING


def build_scene():  # application entry point. Do not change method signature

    app.register_additional_scenes('build_scene_2')

    snake = Snake(NUM_SNAKE_MODULES, pitch_only=False)  # type: snake_module.Snake
    snake.setPosition(agx.Vec3(0, 0, 0.1))
    app.add(snake)

    plane = agxCollide.Geometry(agxCollide.Box(2, 2, 0.1), agx.AffineMatrix4x4.translate(0, 0, -0.1/2))
    app.create_visual(plane, diffuse_color=agxRender.Color.Green())
    app.add(plane)

    ball = agxCollide.Geometry(agxCollide.Sphere(0.035), agx.AffineMatrix4x4.translate(0, 0, 0))
    app.create_visual(ball, diffuse_color=agxRender.Color.YellowGreen())
    ball.setPosition(agx.Vec3(-0.5, 0, 0.1))
    app.add(ball)

    app.add_event_listener(MyKeyEvent(ball))

    app.init_camera(eye=agx.Vec3(-1, -1, 0.5))

    snake_controller = SnakeBallControl(snake, ball)
    snake_controller.init_turning(math.pi / 9.0, math.pi * 2.0 / 3.0, 8.0, 0.0, math.pi * 0.0 / 180.0)
    app.add_event_listener(snake_controller)
