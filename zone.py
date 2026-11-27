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
    """Object containing information about the car at a moment during the lap in the .ghost file.

    A transform matrix is 4x4 matrix stored in a list of 16 floats (row-major order). The matrix contains the following information:
    ::
        | M_00 , M_01 , M_02 , 0 |
        | M_04 , M_05 , M_06 , 0 |
        | M_08 , M_09 , M_10 , 0 |
        | Pos_X, Pos_Y, Pos_Z, 1 |

    Positions are in the same coordinate system as the 3D vector returned by ``ac.getCarState(...,acsys.CS.WorldPosition)``.

    Attributes:

    - ``car_center_transform_matrix``: Matrix containing information about the center of the car.
    - ``front_left_wheel_transform_matrix``: Matrix containing information about the front left wheel.
    - ``front_right_wheel_transform_matrix``: Matrix containing information about the front right wheel.
    - ``rear_left_wheel_transform_matrix``: Matrix containing information about the rear left wheel.
    - ``rear_right_wheel_transform_matrix``: Matrix containing information about the rear right wheel.
    """

    def __init__(self, car_center_transform_matrix, front_left_wheel_transform_matrix, front_right_wheel_transform_matrix, rear_left_wheel_transform_matrix, rear_right_wheel_transform_matrix):
        self.car_center_transform_matrix = car_center_transform_matrix

        self.front_left_wheel_transform_matrix = front_left_wheel_transform_matrix
        self.front_right_wheel_transform_matrix = front_right_wheel_transform_matrix
        self.rear_left_wheel_transform_matrix = rear_left_wheel_transform_matrix
        self.rear_right_wheel_transform_matrix = rear_right_wheel_transform_matrix

    @property
    def car_center_position(self):
        """:return: The position of the car's center."""
        return [self.car_center_transform_matrix[X_COORDINATE], self.car_center_transform_matrix[Y_COORDINATE], self.car_center_transform_matrix[Z_COORDINATE]]

    @property
    def front_left_wheel_position(self):
        """:return: The position of the car's front left wheel."""
        return [self.front_left_wheel_transform_matrix[X_COORDINATE], self.front_left_wheel_transform_matrix[Y_COORDINATE], self.front_left_wheel_transform_matrix[Z_COORDINATE]]

    @property
    def front_right_wheel_position(self):
        """:return: The position of the car's front right wheel."""
        return [self.front_right_wheel_transform_matrix[X_COORDINATE], self.front_right_wheel_transform_matrix[Y_COORDINATE], self.front_right_wheel_transform_matrix[Z_COORDINATE]]

    @property
    def rear_left_wheel_position(self):
        """:return: The position of the car's rear left wheel."""
        return [self.rear_left_wheel_transform_matrix[X_COORDINATE], self.rear_left_wheel_transform_matrix[Y_COORDINATE], self.rear_left_wheel_transform_matrix[Z_COORDINATE]]

    @property
    def rear_right_wheel_position(self):
        """:return: The position of the car's rear right wheel."""
        return [self.rear_right_wheel_transform_matrix[X_COORDINATE], self.rear_right_wheel_transform_matrix[Y_COORDINATE], self.rear_right_wheel_transform_matrix[Z_COORDINATE]]

    @property
    def direction(self):
        """The returned vector is approximate and is not a unit vector.
        :return: The 3D vector representing where the car is going.
        """
        return minus_component_wise(self.front_left_wheel_position, self.rear_left_wheel_position)


class GhostFrameFinder:
    """Object exposing methods to find a frame based on some information."""

    def __init__(self, frames):
        self._frames = frames
        self._last_nearest_frame_index = 0

    def frame_index_near(self, x, y, z):
        """Find the frame where the car's center is the nearest to the given position.

        The implementation relies on a linear search and stores the latest frame found.
        So if between two calls the given positions are close then finding the frame is cheap.

        :param x: Coordinate of the position on the X axis.
        :param y: Coordinate of the position on the Y axis.
        :param z: Coordinate of the position on the Z axis.
        :return: The index of the frame.
        """
        position = [x, y, z]

        distance_with_previous_frame = norm(
            minus_component_wise(self._frames[self._last_nearest_frame_index - 1].car_center_position, position)) if 0 <= self._last_nearest_frame_index - 1 < len(self._frames) else float("inf")
        distance_with_next_frame = norm(
            minus_component_wise(self._frames[self._last_nearest_frame_index + 1].car_center_position, position)) if 0 <= self._last_nearest_frame_index + 1 < len(self._frames) else float("inf")

        if distance_with_previous_frame < distance_with_next_frame:
            step = -1
            stop = 0
        else:
            step = 1
            stop = len(self._frames)

        minimal_distance_with_position = norm(minus_component_wise(self._frames[self._last_nearest_frame_index].car_center_position, position))
        for frame_index in range(self._last_nearest_frame_index + step, stop, step):
            distance_with_position = norm(minus_component_wise(self._frames[frame_index].car_center_position, position))

            if distance_with_position >= minimal_distance_with_position:
                break

            self._last_nearest_frame_index = frame_index
            minimal_distance_with_position = distance_with_position

        return self._last_nearest_frame_index


class Ghost:
    """Object containing information stored in the .ghost file.

    Attributes:

    - ``driver_name``: The driver's name.
    - ``track_id``: The track's identifier.
    - ``track_configuration_id``: The identifier of the track's configuration.
    - ``car_id``: The car's identifier.
    - ``lap_time_ms``: Lap time in milliseconds.
    - ``frames``: A list of evenly recorded moments during the lap.
    """
    def __init__(self, driver_name, track_id, track_configuration_id, car_id, lap_time_ms, frames):
        self.driver_name = driver_name
        self.track_id = track_id
        self.track_configuration_id = track_configuration_id
        self.car_id = car_id
        self.lap_time_ms = lap_time_ms
        self.frames = frames

        self._car_center_distance_from_start_by_frame = []

    @property
    def frame_time_ms(self):
        """ :return: The time in milliseconds between two frames."""
        return self.lap_time_ms / float(len(self.frames) - 1)

    def car_center_distance_from_start_at(self, frame_index):
        """Return the distance between the car's center at the given frame and the car's center at the start.

        :param frame_index: The index of the frame.
        :return: The driving distance (not the straight-line distance).
        """
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
        """Create a new ``GhostFrameFinder`` searching in this ghost's frames."""
        return GhostFrameFinder(self.frames)


def unpack_unsigned_int(reader):
    (integer,) = struct.unpack("<I", reader.read(4))
    return integer


def unpack_string(reader):
    size = unpack_unsigned_int(reader)
    return reader.read(size).decode(encoding="utf-8", errors="replace")


def unpack_4x4_matrix(reader):
    return struct.unpack("<16f", reader.read(16 * 4))


class _GhostParser4:
    def __init__(self, reader, driver_name, track_id, track_configuration_id, car_id, lap_time_ms):
        self._reader = reader
        self.driver_name = driver_name
        self.track_id = track_id
        self.track_configuration_id = track_configuration_id
        self.car_id = car_id
        self.lap_time_ms = lap_time_ms

    def parse(self):
        """Parse the frames.

        :return: All the parsed information.
        """
        reader = self._reader
        self._reader = None

        frames_count = unpack_unsigned_int(reader)
        frames = []
        for i in range(frames_count):
            car_center_transform_matrix = unpack_4x4_matrix(reader)

            front_left_wheel_transform_matrix = unpack_4x4_matrix(reader)
            front_right_wheel_transform_matrix = unpack_4x4_matrix(reader)
            rear_left_wheel_transform_matrix = unpack_4x4_matrix(reader)
            rear_right_wheel_transform_matrix = unpack_4x4_matrix(reader)

            unknown0_transform_matrix = unpack_4x4_matrix(reader)
            unknown1_transform_matrix = unpack_4x4_matrix(reader)
            unknown2_transform_matrix = unpack_4x4_matrix(reader)
            unknown3_transform_matrix = unpack_4x4_matrix(reader)

            frames.append(
                GhostFrame(car_center_transform_matrix, front_left_wheel_transform_matrix, front_right_wheel_transform_matrix, rear_left_wheel_transform_matrix, rear_right_wheel_transform_matrix))

        return Ghost(self.driver_name, self.track_id, self.track_configuration_id, self.car_id, self.lap_time_ms, frames)


class _GhostParser3:
    def __init__(self, reader, driver_name, track_id, track_configuration_id, car_id):
        self.reader = reader
        self.driver_name = driver_name
        self.track_id = track_id
        self.track_configuration_id = track_configuration_id
        self.car_id = car_id

    def parse(self):
        """Parse the lap time.

        :return: The lap time in milliseconds and the parser to continue parsing.
        """
        reader = self.reader
        self._reader = None

        lap_time_ms = unpack_unsigned_int(reader)

        return lap_time_ms, _GhostParser4(reader, self.driver_name, self.track_id, self.track_configuration_id, self.car_id, lap_time_ms)


class _GhostParser2:
    def __init__(self, reader, driver_name, track_id, track_configuration_id):
        self._reader = reader
        self.driver_name = driver_name
        self.track_id = track_id
        self.track_configuration_id = track_configuration_id

    def parse(self):
        """Parse the car's identifier.

        :return: The car's identifier and the parser to continue parsing.
        """
        reader = self._reader
        self._reader = None

        car_id = unpack_string(reader)

        return car_id, _GhostParser3(reader, self.driver_name, self.track_id, self.track_configuration_id, car_id)


class _GhostParser1:
    def __init__(self, reader, driver_name, track_id):
        self._reader = reader
        self.driver_name = driver_name
        self.track_id = track_id

    def parse(self):
        """Parse the identifier of the track's configuration.

        :return: The identifier of the track's configuration and the parser to continue parsing.
        """
        reader = self._reader
        self._reader = None

        track_configuration_id = unpack_string(reader)

        return track_configuration_id, _GhostParser2(reader, self.driver_name, self.track_id, track_configuration_id)


class _GhostParser0:
    def __init__(self, reader, driver_name):
        self._reader = reader
        self.driver_name = driver_name

    def parse(self):
        """Parse the track's identifier.

        :return: The track's identifier and the parser to continue parsing.
        """
        reader = self._reader
        self._reader = None

        track_id = unpack_string(reader)

        return track_id, _GhostParser1(reader, self.driver_name, track_id)


class GhostParser:
    """A parser of .ghost file from a reader.

    Do not call ``parse`` more than once on the same parser object and use the returned one.
    """
    def __init__(self, reader):
        self._reader = reader

    def parse(self):
        """Parse the driver's name.

        :return: The driver's name and the parser to continue parsing.
        """
        reader = self._reader
        self._reader = None

        unknown0 = unpack_unsigned_int(reader)
        unknown1 = unpack_unsigned_int(reader)

        driver_name = unpack_string(reader)

        return driver_name, _GhostParser0(reader, driver_name)


def parse(reader):
    """Parse the given reader.

    :param reader: Reader containing a .ghost file's data.
    :return: The parsed information stored in the reader.
    """
    return GhostParser(reader).parse()[1].parse()[1].parse()[1].parse()[1].parse()[1].parse()
