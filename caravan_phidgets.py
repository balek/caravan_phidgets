#!/usr/bin/env python

from Phidgets.Devices.Analog import Analog  # @UnresolvedImport

from twisted.internet.defer import inlineCallbacks, CancelledError
from autobahn.twisted.util import sleep

from caravan.base import VanSession, VanModule, VanDevice, deviceCommand, Decimal, Int



class AnalogOutput(VanDevice):
    list = None
    sleeping = None
    stateType = Decimal(precision=3)

    def __init__(self, parent, output):
        self.output = output
        parent.phidget.setEnabled(output, True)
        super(AnalogOutput, self).__init__(parent, 'output%i' % output)

    @deviceCommand()
    def get(self):
        value = self.parent.phidget.getVoltage(self.output)
        return self.changeState(value)

    @deviceCommand(stateType)
    @inlineCallbacks
    def set(self, value):
        if self.sleeping and not self.sleeping.called:
            yield self.sleeping.cancel()
        self.parent.phidget.setVoltage(self.output, value)
        self.changeState(value)

    @deviceCommand(stateType)
    @inlineCallbacks
    def smoothlySet(self, value):
        if self.sleeping and not self.sleeping.called:
            yield self.sleeping.cancel()
        currentValue = self.parent.phidget.getVoltage(self.output)
        try:
            while currentValue != value: 
                currentValue += 0.1 if currentValue < value else -0.1
                if abs(currentValue - value) < 0.1:
                    currentValue = value
                self.parent.phidget.setVoltage(self.output, currentValue)
                self.sleeping = sleep(0.01)
                yield self.sleeping
        except CancelledError:
            pass
        self.changeState(currentValue)


class AnalogPhidget(VanDevice):
    def __init__(self, parent, name, phidget=-1):
        self.phidget = Analog()
        self.phidget.openPhidget(phidget)
        self.phidget.waitForAttach(0)
        super(AnalogPhidget, self).__init__(parent, name)

    @deviceCommand(Int(0, 3))
    def enableOutput(self, output):
        if 'output%i' % output not in self.children:
            AnalogOutput(self, output)


class AppSession(VanSession):
    def start(self):
        module = VanModule(self, 'phidgets')
        AnalogPhidget(module, 'analog')


if __name__ == '__main__':
    from autobahn.twisted.wamp import ApplicationRunner
    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", "realm1")
    runner.run(AppSession)
