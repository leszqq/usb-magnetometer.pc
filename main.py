from sensor.sensor_stub import SensorStub
from sensor.sensor import Sensor
from gui.gui_stub import GuiStub
from gui.gui import Gui
from supervisor.supervisor import Supervisor
import asyncio
import logging


async def main():
    logging.basicConfig(level=logging.INFO)
    gui = Gui()
    await gui.wait_until_initialized()
    sensor = Sensor()
    supervisor = Supervisor(gui_controller=gui, sensor_controller=sensor)
    gui.attach_observer(supervisor)
    sensor.attach_consumer(supervisor)

    # while True:
    #     await asyncio.sleep(1)
    #     tasks = asyncio.all_tasks()
    #     print("")
    #     for t in tasks:
    #         print(t)
    #     try:
    #         await asyncio.wait_for(gui.wait_for_closed(), timeout=1.0)
    #     except TimeoutError:
    #         print('timeout!')

    await gui.wait_for_closed()
    supervisor.on_stop_button()


asyncio.run(main())
