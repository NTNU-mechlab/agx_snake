
from app.gaits import *

import agxSDK

import math

ERROR = math.pi*4.0/180.0
MAX_SPD = math.pi/3.0/0.23
MAX_TORQUE = 3.17*9.8066*0.01
KP = 12
REACHED = 1
NOT_REACHED = 0


class SnakeControl(agxSDK.StepEventListener):

    def __init__(self, snake):
        super().__init__(agxSDK.StepEventListener.PRE_STEP)

        self.snake = snake
        self.phi = [None] * len(snake.modules)   # list of phase difference
        self.am = [None] * len(snake.modules)  # list of amplitudes, in rad
        self.desire_angle = [None] * len(snake.modules)
        self.offset = [None] * len(snake.modules)
        self.fixed_angle = [False] * len(snake.modules)  # fixed angle is used for the yaw group for the forward or the turning gait

        self.sample_time = 0
        self.period = 0

        self.prev_gait = TURNING

    def control_group_init(self, am_p, am_y, phi_p, phi_y, phi_py, time_period, offset_p, offset_y):
        self.period = time_period

        self.phi[0] = 0.0
        self.phi[1] = phi_py

        self.sample_time = 0

        for i in range(0, len(self.snake.modules)):
            if i % 2 == 0: # pitch group
                self.am[i] = am_p
                self.phi[i] = self.phi[0] + (int(i / 2)) * phi_p
                self.offset[i] = offset_p
            else:
                self.am[i] = am_y
                self.phi[i] = self.phi[1] + (int(i / 2)) * phi_y
                self.offset[i] = offset_y

            self.desire_angle[i] = self.am[i] * math.sin(2*math.pi*self.sample_time/self.period+self.phi[i])+self.offset[i]

    def init_turning(self, amplitude_p, phi_p, period, offset_p, offset_y):
        self.control_group_init(amplitude_p, 0.0, phi_p, 0.0, 0.0, period, offset_p, offset_y)
        for i in range(0, len(self.snake.modules)):
            if i % 2 != 0: # yaw group
                self.fixed_angle[i] = True
                self.snake.modules[i].hinge.getMotor1D().setLockedAtZeroSpeed(True)

    def init_sidewinding(self, amplitude_p, phi_p, period):
        self.control_group_init(amplitude_p, amplitude_p, phi_p, phi_p, -math.pi / 20, period, 0.0, 0.0)
        for i in range(0, len(self.snake.modules)):
            self.fixed_angle[i] = False
            self.snake.modules[i].hinge.getMotor1D().setLockedAtZeroSpeed(False)

    def init_rolling(self, amplitude_p, amplitude_y, period): # phi_y = phi_x = 0, phi_py = pi/2
        self.control_group_init(amplitude_p, amplitude_y, 0.0, 0.0, math.pi / 2, period, 0.0, 0.0)
        for i in range(0, len(self.snake.modules)):
            self.fixed_angle[i] = False
            self.snake.modules[i].hinge.getMotor1D().setLockedAtZeroSpeed(False)

    def init_rotating(self, amplitude_p, amplitude_y, period):
        self.control_group_init(amplitude_p, amplitude_y, 0.0, math.pi, math.pi / 2, period, 0.0, 0.0)
        for i in range(0, len(self.snake.modules)):
            self.fixed_angle[i] = False
            self.snake.modules[i].hinge.getMotor1D().setLockedAtZeroSpeed(False)

    def init_clockwise_rotating(self, amplitude_p, amplitude_y, period):
        self.control_group_init(amplitude_p, amplitude_y, 0.0, math.pi, -math.pi / 2, period, 0.0, 0.0)
        for i in range(0, len(self.snake.modules)):
            self.fixed_angle[i] = False
            self.snake.modules[i].hinge.getMotor1D().setLockedAtZeroSpeed(False)

    def init_counterclockwise_rotating(self, amplitude_p, amplitude_y, period):
        self.control_group_init(amplitude_p, amplitude_y, 0.0, math.pi, math.pi / 2, period, 0.0, 0.0)
        for i in range(0, len(self.snake.modules)):
            self.fixed_angle[i] = False
            self.snake.modules[i].hinge.getMotor1D().setLockedAtZeroSpeed(False)

    def init_flapping(self, amplitude_p, amplitude_y, period, offset_p):
        self.control_group_init(amplitude_p, amplitude_y, 0.0, 0.0, math.pi / 2, period, offset_p, -offset_p)
        for i in range(0, len(self.snake.modules)):
            self.fixed_angle[i] = False
            self.snake.modules[i].hinge.getMotor1D().setLockedAtZeroSpeed(False)

    def set_hinge_angle(self, hinge, ref_angle, is_fixed_angle):
        error_angle = ref_angle - hinge.getAngle()
        if math.fabs(error_angle) > ERROR:
            if KP * error_angle > MAX_SPD:
                hinge.getMotor1D().setSpeed(MAX_SPD)
            elif KP * error_angle < -MAX_SPD:
                hinge.getMotor1D().setSpeed(-MAX_SPD)
            else:
                hinge.getMotor1D().setSpeed(KP * error_angle)
            return NOT_REACHED
        elif is_fixed_angle:
            hinge.getMotor1D().setSpeed(0)
        return REACHED

    def onestep_angle(self, cur_time):
        for i in range(0, len(self.snake.modules)):
            self.desire_angle[i] = self.am[i] * math.sin(2 * math.pi * self.sample_time / self.period + self.phi[i]) + \
                                   self.offset[i]
        self.sample_time += self.period/12.0
        if self.sample_time>self.period:
            self.sample_time -= self.period

    def servo_control(self, cur_time):
        total_stable = 0
        for i in range(0, len(self.snake.modules)):
            total_stable += self.set_hinge_angle(self.snake.modules[i].hinge, self.desire_angle[i], self.fixed_angle[i])

        if total_stable == len(self.snake.modules):
            self.onestep_angle(cur_time)

    def pre(self, tt): # tt is the current time in simulation
        self.servo_control(tt)
