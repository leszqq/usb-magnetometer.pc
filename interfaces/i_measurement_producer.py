from abc import ABC, abstractmethod
from interfaces.i_measurement_consumer import IMeasurementConsumer


class IMeasurementProducer(ABC):

    @abstractmethod
    def attach_consumer(self, consumer: IMeasurementConsumer):
        pass
