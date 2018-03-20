
import agxSDK


class KeyEvent(agxSDK.GuiEventListener):

    def __init__(self, key, func):
        super().__init__(agxSDK.GuiEventListener.KEYBOARD)
        self.key = key
        self.func = func

    def keyboard(self, key, alt, x, y, down):
        handled = False
        if key == self.key:
            self.func()
            handled = True
        return handled
