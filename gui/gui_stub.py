from interfaces.i_gui_controller import IGuiController
from interfaces.i_gui_subject import IGuiSubject
from interfaces.i_gui_observer import IGuiObserver
import asyncio
from custom_types import Vector
from typing import List, Optional
import logging
from aioconsole import ainput

logger = logging.getLogger(__name__)


class GuiStub(IGuiController, IGuiSubject):

    def __init__(self):
        self._gui_observer: Optional[IGuiObserver] = None

    def update_measurement_text_field(self, measurement: Vector) -> None:
        logger.info(f"Text fields updated with {measurement}")

    def update_graph(self, measurements: List[Vector]) -> None:
        logger.info(f"Graph updated with {measurements}")

    def set_waiting_for_connection_message(self, shown: bool) -> None:
        logger.info(f"Waiting for connection message {'shown' if shown else 'hidden'}")

    def set_start_button_active(self, active: bool) -> None:
        logger.info(f"Start button set {'active' if active else 'inactive'}")

    def set_stop_button_active(self, active: bool) -> None:
        logger.info(f"Stop button set {'active' if active else 'inactive'}")

    def attach_observer(self, observer: IGuiObserver) -> None:
        self._gui_observer = observer

    async def run(self):
        while True:
            # i = await ainput("s: click start, p: click pause, q: click configure 25mt, w: click configure 50mt, "
            #                  "e: click configure 100mt")
            i = await ainput()
            if self._gui_observer:
                if i == 's':
                    self._gui_observer.on_start_button()
                elif i == 'p':
                    self._gui_observer.on_stop_button()
                elif i == 'q':
                    self._gui_observer.on_25_mt_range_button()
                elif i == 'w':
                    self._gui_observer.on_50_mt_range_button()
                elif i == 'e':
                    self._gui_observer.on_100_mt_range_button()
                elif i == 'x':
                    return
