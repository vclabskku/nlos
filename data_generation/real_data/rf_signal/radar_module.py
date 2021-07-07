import numpy as np
from pathlib import Path
from typing import Union


class RadarModule:
    def __init__(self, radar_lib_path: str):
        # noinspection PyUnresolvedReferences
        import clr
        clr.AddReference(str(Path(radar_lib_path).resolve()))
        # noinspection PyUnresolvedReferences
        from NoveldaAPI.Radarlib3Wrapper import RadarWrapper
        self._radar = RadarWrapper()
        module_name = self._radar.ConnectedModules[0]
        self._radar.Open(module_name)
        self._sample_distance = np.empty(0)
        self._sample_spacing = 0
        self._sample_time = np.empty(0)
        self._num_sample = 0

    @property
    def num_sample(self):
        return self._num_sample

    def set_timing_variables(self, sample_delay_to_reference: float, offset_distance_from_reference: float,
                             frame_stitch: int):
        self.set_frame_stitch(frame_stitch)
        self.execute_timing_measurement()
        self.set_sample_delay_to_reference(sample_delay_to_reference/(10 ** 9))
        self.set_offset_distance_from_reference(offset_distance_from_reference)
        self._num_sample = self.get_samplers_per_frame()
        samples_per_second = self.get_samples_per_second()
        speed_of_light = 299792458.0  # speed of light in m/s
        distance_between_samples = 0.5 * speed_of_light / samples_per_second
        self._sample_distance = offset_distance_from_reference + np.arange(self._num_sample) * distance_between_samples

        #   샘플당 시간간격을 ns 단위로
        #   약 0.027
        self._sample_spacing = (10 ** 9) / samples_per_second
        self._sample_time = (2*offset_distance_from_reference/ speed_of_light) * (10 ** 9) \
                            + np.arange(self._num_sample) * self._sample_spacing

    def get_sample_distance(self):
        return self._sample_distance

    def get_sample_spacing(self):
        return self._sample_spacing

    def get_sample_time(self):
        return self._sample_time

    def _set_variable(self, name: str, value: Union[float, int, str]):
        self._radar.TryUpdateChip(name, value)

    def _get_variable(self, name: str):
        return self._radar[name]

    def _execute_action(self, action: str):
        return self._radar.ExcecuteAction(action)

    def execute_timing_measurement(self):
        self._execute_action('MeasureAll')

    def get_samples_per_second(self):
        return self._get_variable('SamplesPerSecond').Value.ToDouble()

    def set_offset_distance_from_reference(self, distance: float):
        self._set_variable('OffsetDistanceFromReference', distance)

    def get_offset_distance_from_reference(self):
        return self._get_variable('OffsetDistanceFromReference').Value.ToDouble()

    def set_sample_delay_from_reference(self, delay: float):
        self._set_variable('SampleDelayFromReference', delay)

    def get_sample_delay_from_reference(self):
        return self._get_variable('SampleDelayFromReference')

    def set_sample_delay_to_reference(self, delay: float):
        self._set_variable('SampleDelayToReference', delay)

    def get_sample_delay_to_reference(self):
        return self._get_variable('SampleDelayToReference')

    def set_frame_stitch(self, frame_stitch: int):
        self._set_variable('FrameStitch', frame_stitch)

    def get_frame_stitch(self):
        return self._get_variable('FrameStitch').Value.ToInt()

    def set_iterations(self, iterations: int):
        self._set_variable('Iterations', iterations)

    def get_iterations(self):
        return self._get_variable('Iterations').Value.ToInt()

    def set_gain(self, gain: int):
        self._set_variable('Gain', gain)

    def get_gain(self):
        return self._get_variable('Gain').Value.ToInt()

    def set_zoom(self, zoom_min: int, zoom_max: int):
        self._set_variable('ZoomMin', zoom_min)
        self._set_variable('ZoomMax', zoom_max)

    def set_to_low_band(self):
        self._set_variable('PulseGen', '1.5GHz')

    def set_to_medium_band(self):
        self._set_variable('PulseGen', '4.3GHz')

    def set_averaging_factor(self, averaging_factor):
        self._set_variable('AveragingFactor', averaging_factor)

    def get_samplers_per_frame(self):
        return self._get_variable('SamplersPerFrame').Value.ToInt()

    def get_frame_normalized_double(self):
        return np.array(list(self._radar.GetFrameNormalizedDouble()))

    def get_frame_raw(self):
        return np.array(list(self._radar.GetFrameRaw()))
