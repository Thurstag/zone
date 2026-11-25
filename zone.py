# Copyright 2026-2026 Zone contributors
# Licensed under Apache License 2.0 or any later version
# Refer to the LICENSE file included.

import struct
from math import sqrt


def norm(v):
    result = 0
    for c in v:
        result += c * c
    return sqrt(result)


def minus_component_wise(a, b):
    result = []
    for c0, c1 in zip(a, b):
        result.append(c0 - c1)
    return result


X_COORDINATE = 12
Y_COORDINATE = 13
Z_COORDINATE = 14


class GhostFrame:
    def __init__(self, car_center_transform_matrix, front_left_wheel_transform_matrix, front_right_wheel_transform_matrix, rear_left_wheel_transform_matrix, rear_right_wheel_transform_matrix):
        self.car_center_transform_matrix = car_center_transform_matrix

        self.front_left_wheel_transform_matrix = front_left_wheel_transform_matrix
        self.front_right_wheel_transform_matrix = front_right_wheel_transform_matrix
        self.rear_left_wheel_transform_matrix = rear_left_wheel_transform_matrix
        self.rear_right_wheel_transform_matrix = rear_right_wheel_transform_matrix

    @property
    def car_center_position(self):
        return [self.car_center_transform_matrix[X_COORDINATE], self.car_center_transform_matrix[Y_COORDINATE], self.car_center_transform_matrix[Z_COORDINATE]]

    @property
    def front_left_wheel_position(self):
        return [self.front_left_wheel_transform_matrix[X_COORDINATE], self.front_left_wheel_transform_matrix[Y_COORDINATE], self.front_left_wheel_transform_matrix[Z_COORDINATE]]

    @property
    def front_right_wheel_position(self):
        return [self.front_right_wheel_transform_matrix[X_COORDINATE], self.front_right_wheel_transform_matrix[Y_COORDINATE], self.front_right_wheel_transform_matrix[Z_COORDINATE]]

    @property
    def rear_left_wheel_position(self):
        return [self.rear_left_wheel_transform_matrix[X_COORDINATE], self.rear_left_wheel_transform_matrix[Y_COORDINATE], self.rear_left_wheel_transform_matrix[Z_COORDINATE]]

    @property
    def rear_right_wheel_position(self):
        return [self.rear_right_wheel_transform_matrix[X_COORDINATE], self.rear_right_wheel_transform_matrix[Y_COORDINATE], self.rear_right_wheel_transform_matrix[Z_COORDINATE]]

    @property
    def direction(self):
        return minus_component_wise(self.front_left_wheel_position, self.rear_left_wheel_position)


class GhostFrameFinder:
    def __init__(self, frames):
        self.frames = frames

        self._last_nearest_frame_index = 0

    def frame_index_near(self, x, y, z):
        position = [x, y, z]

        distance_with_previous_frame = norm(
            minus_component_wise(self.frames[self._last_nearest_frame_index - 1].car_center_position, position)) if 0 <= self._last_nearest_frame_index - 1 < len(self.frames) else float("inf")
        distance_with_next_frame = norm(
            minus_component_wise(self.frames[self._last_nearest_frame_index + 1].car_center_position, position)) if 0 <= self._last_nearest_frame_index + 1 < len(self.frames) else float("inf")

        if distance_with_previous_frame < distance_with_next_frame:
            step = -1
            stop = 0
        else:
            step = 1
            stop = len(self.frames)

        minimal_distance_with_position = norm(minus_component_wise(self.frames[self._last_nearest_frame_index].car_center_position, position))
        for frame_index in range(self._last_nearest_frame_index + step, stop, step):
            distance_with_position = norm(minus_component_wise(self.frames[frame_index].car_center_position, position))

            if distance_with_position >= minimal_distance_with_position:
                break

            self._last_nearest_frame_index = frame_index
            minimal_distance_with_position = distance_with_position

        return self._last_nearest_frame_index


class Ghost:
    def __init__(self, driver_name, track_name, track_configuration_name, car_id, lap_time_ms, frames):
        self.driver_name = driver_name
        self.track_name = track_name
        self.track_configuration_name = track_configuration_name
        self.car_id = car_id
        self.lap_time_ms = lap_time_ms
        self.frames = frames

        self._car_center_distance_from_start_by_frame = []

    @property
    def frame_time_ms(self):
        return self.lap_time_ms / float(len(self.frames))

    def car_center_distance_from_start_at(self, frame_index):
        if len(self._car_center_distance_from_start_by_frame) == 0:
            for (index, frame) in enumerate(self.frames):
                if index == 0:
                    self._car_center_distance_from_start_by_frame.append(0.0)
                    continue

                previous_frame = self.frames[index - 1]
                self._car_center_distance_from_start_by_frame.append(
                    self._car_center_distance_from_start_by_frame[index - 1] + norm(minus_component_wise(frame.car_center_position, previous_frame.car_center_position)))

        return self._car_center_distance_from_start_by_frame[frame_index]

    def frame_finder(self):
        return GhostFrameFinder(self.frames)


def unpack_unsigned_int(file):
    (integer,) = struct.unpack("<I", file.read(4))
    return integer


def unpack_string(file):
    size = unpack_unsigned_int(file)
    return file.read(size).decode(encoding="ascii", errors="replace")


def unpack_4x4_matrix(file):
    return struct.unpack("<16f", file.read(16 * 4))


class _GhostParser4:
    def __init__(self, file, driver_name, track_name, track_configuration_name, car_id, lap_time_ms):
        self._file = file
        self.driver_name = driver_name
        self.track_name = track_name
        self.track_configuration_name = track_configuration_name
        self.car_id = car_id
        self.lap_time_ms = lap_time_ms

    def parse(self):
        frames_count = unpack_unsigned_int(self._file)
        frames = []
        for i in range(frames_count):
            car_center_transform_matrix = unpack_4x4_matrix(self._file)

            front_left_wheel_transform_matrix = unpack_4x4_matrix(self._file)
            front_right_wheel_transform_matrix = unpack_4x4_matrix(self._file)
            rear_left_wheel_transform_matrix = unpack_4x4_matrix(self._file)
            rear_right_wheel_transform_matrix = unpack_4x4_matrix(self._file)

            unknown0_transform_matrix = unpack_4x4_matrix(self._file)
            unknown1_transform_matrix = unpack_4x4_matrix(self._file)
            unknown2_transform_matrix = unpack_4x4_matrix(self._file)
            unknown3_transform_matrix = unpack_4x4_matrix(self._file)

            frames.append(
                GhostFrame(car_center_transform_matrix, front_left_wheel_transform_matrix, front_right_wheel_transform_matrix, rear_left_wheel_transform_matrix, rear_right_wheel_transform_matrix))

        return Ghost(self.driver_name, self.track_name, self.track_configuration_name, self.car_id, self.lap_time_ms, frames)


class _GhostParser3:
    def __init__(self, file, driver_name, track_name, track_configuration_name, car_id):
        self._file = file
        self.driver_name = driver_name
        self.track_name = track_name
        self.track_configuration_name = track_configuration_name
        self.car_id = car_id

    def parse(self):
        lap_time_ms = unpack_unsigned_int(self._file)

        return lap_time_ms, _GhostParser4(self._file, self.driver_name, self.track_name, self.track_configuration_name, self.car_id, lap_time_ms)


class _GhostParser2:
    def __init__(self, file, driver_name, track_name, track_configuration_name):
        self._file = file
        self.driver_name = driver_name
        self.track_name = track_name
        self.track_configuration_name = track_configuration_name

    def parse(self):
        car_id = unpack_string(self._file)

        return car_id, _GhostParser3(self._file, self.driver_name, self.track_name, self.track_configuration_name, car_id)


class _GhostParser1:
    def __init__(self, file, driver_name, track_name):
        self._file = file
        self.driver_name = driver_name
        self.track_name = track_name

    def parse(self):
        track_configuration_name = unpack_string(self._file)

        return track_configuration_name, _GhostParser2(self._file, self.driver_name, self.track_name, track_configuration_name)


class _GhostParser0:
    def __init__(self, file, driver_name):
        self._file = file
        self.driver_name = driver_name

    def parse(self):
        track_name = unpack_string(self._file)

        return track_name, _GhostParser1(self._file, self.driver_name, track_name)


class GhostParser:
    def __init__(self, file):
        self._file = file

    def parse(self):
        unknown0 = unpack_unsigned_int(self._file)
        unknown1 = unpack_unsigned_int(self._file)

        driver_name = unpack_string(self._file)

        return driver_name, _GhostParser0(self._file, driver_name)


def parse(file):
    return GhostParser(file).parse()[1].parse()[1].parse()[1].parse()[1].parse()[1].parse()
