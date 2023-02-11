import logging
import typing

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty, NumericProperty, ListProperty
from kivy.core.window import Window
import asyncio
from interfaces.i_gui_controller import IGuiController
from interfaces.i_gui_subject import IGuiSubject
from interfaces.i_gui_observer import IGuiObserver
from custom_types import Vector
from typing import List

class SplitBar(Widget):
    pass


class CustomButton(Button):
    _active = BooleanProperty(False)
    _highlighted = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_press(self):
        if self._active:
            self.background_color = self._highlighted_background_color

    def on_release(self):
        if self._highlighted:
            self.background_color = self._highlighted_background_color
        elif self._active:
            self.background_color = self._active_background_color


class GuiLayout(BoxLayout):

    def __init__(self, **kwargs):
        super(GuiLayout, self).__init__(**kwargs)


class GuiApp(App):

    def __init__(self) -> None:
        super().__init__()
        Window.size = (800, 600)
        # Window.maximize()
        Window.minimum_width, Window.minimum_height = (800, 600)
        self._root_layout = None
        self._start_event = asyncio.Event()

    def build(self) -> GuiLayout:
        self._root_layout = GuiLayout()
        return self._root_layout

    def on_start(self):
        self._start_event.set()

    async def wait_until_started(self) -> None:
        await self._start_event.wait()

    @property
    def root_layout(self) -> GuiLayout:
        return self._root_layout


class Gui(IGuiController, IGuiSubject):

    def __init__(self) -> None:
        self._gui_app = GuiApp()
        self._gui_task = asyncio.create_task(self._run())

    async def _run(self):
        await self._gui_app.async_run(async_lib='asyncio')

    async def wait_until_initialized(self) -> None:
        await self._gui_app.wait_until_started()

    def update_measurement_text_fields(self, measurement: Vector) -> None:
        pass

    def update_graph(self, measurements: List[Vector]) -> None:
        pass

    def set_waiting_for_connection_message(self, shown: bool) -> None:
        pass

    def set_start_button(self, active: bool) -> None:
        pass

    def set_stop_button(self, active: bool) -> None:
        pass

    def attach_observer(self, observer: IGuiObserver) -> None:
        pass

    def set_preset_text(self, text: str) -> None:
        self._gui_app.root_layout.ids.preset_selection_panel.value_string_prop = text

    def set_modulation_mode_text(self, text: str) -> None:
        self._gui_app.root_layout.ids.modulation_mode_selection_panel.value_string_prop = text

    def set_modulation_mode_panel_active(self, active: bool) -> None:
        self._gui_app.root_layout.ids.modulation_mode_selection_panel.active_prop = active

    def set_squeeze_response_text(self, text: str) -> None:
        self._gui_app.root_layout.ids.squeeze_response_selection_panel.value_string_prop = text

    def set_fixed_rate_text(self, text: str) -> None:
        self._gui_app.root_layout.ids.fixed_rate_panel.value_string_prop = text

    def set_fixed_rate_panel_active(self, active: bool) -> None:
        self._gui_app.root_layout.ids.fixed_rate_panel.active_prop = active

    def set_minimum_rate_text(self, text: str) -> None:
        self._gui_app.root_layout.ids.minimum_rate_panel.value_string_prop = text

    def set_minimum_rate_panel_active(self, active: bool) -> None:
        self._gui_app.root_layout.ids.minimum_rate_panel.active_prop = active

    def set_maximum_rate_text(self, text: str) -> None:
        self._gui_app.root_layout.ids.maximum_rate_panel.value_string_prop = text

    def set_maximum_rate_panel_active(self, active: bool) -> None:
        self._gui_app.root_layout.ids.maximum_rate_panel.active_prop = active

    def set_squeeze_force_text(self, text: str) -> None:
        self._gui_app.root_layout.ids.squeeze_force_panel.value_string_prop = text

    def set_next_preset_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.preset_selection_panel.ids.right_arrow.touch_callback = handler

    def set_previous_preset_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.preset_selection_panel.ids.left_arrow.touch_callback = handler

    def set_next_modulation_mode_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.modulation_mode_selection_panel.ids.right_arrow.touch_callback = handler

    def set_previous_modulation_mode_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.modulation_mode_selection_panel.ids.left_arrow.touch_callback = handler

    def set_next_squeeze_response_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.squeeze_response_selection_panel.ids.right_arrow.touch_callback = handler

    def set_previous_squeeze_response_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.squeeze_response_selection_panel.ids.left_arrow.touch_callback = handler

    def set_increase_fixed_rate_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.fixed_rate_panel.ids.plus_sign.touch_callback = handler

    def set_decrease_fixed_rate_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.fixed_rate_panel.ids.minus_sign.touch_callback = handler

    def set_increase_minimum_rate_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.minimum_rate_panel.ids.plus_sign.touch_callback = handler

    def set_decrease_minimum_rate_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.minimum_rate_panel.ids.minus_sign.touch_callback = handler

    def set_increase_maximum_rate_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.maximum_rate_panel.ids.plus_sign.touch_callback = handler

    def set_decrease_maximum_rate_button_handler(self, handler: typing.Callable) -> None:
        self._gui_app.root_layout.ids.maximum_rate_panel.ids.minus_sign.touch_callback = handler
