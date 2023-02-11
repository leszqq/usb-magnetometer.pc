from sensor.sensor_stub import SensorStub
from gui.gui_stub import GuiStub
from gui.gui import Gui
from supervisor.supervisor import Supervisor
import asyncio
import logging


async def main():
    logging.basicConfig(level=logging.DEBUG)
    # gui = GuiStub()
    gui = Gui()
    await gui.wait_until_initialized()
    sensor = SensorStub()
    supervisor = Supervisor(gui_controller=gui, sensor_controller=sensor)
    gui.attach_observer(supervisor)
    sensor.attach_consumer(supervisor)

    while True:
        await asyncio.sleep(1)
    # await gui.run()


asyncio.run(main())
