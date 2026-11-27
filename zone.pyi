# Copyright 2026-2026 Zone contributors
# Licensed under Apache License 2.0 or any later version
# Refer to the LICENSE file included.

from io import BufferedIOBase

Vector3 = list[float]
VectorN = list[float]


def norm(v: VectorN) -> float: ...


def minus_component_wise(a: VectorN, b: VectorN) -> VectorN: ...


Matrix4x4 = list[float]


class GhostFrame:
    car_center_transform_matrix: Matrix4x4
    front_left_wheel_transform_matrix: Matrix4x4
    front_right_wheel_transform_matrix: Matrix4x4
    rear_left_wheel_transform_matrix: Matrix4x4
    rear_right_wheel_transform_matrix: Matrix4x4

    def __init__(self, car_center_transform_matrix: Matrix4x4, front_left_wheel_transform_matrix: Matrix4x4, front_right_wheel_transform_matrix: Matrix4x4,
                 rear_left_wheel_transform_matrix: Matrix4x4, rear_right_wheel_transform_matrix: Matrix4x4) -> None: ...

    @property
    def car_center_position(self) -> Vector3: ...

    @property
    def front_left_wheel_position(self) -> Vector3: ...

    @property
    def front_right_wheel_position(self) -> Vector3: ...

    @property
    def rear_left_wheel_position(self) -> Vector3: ...

    @property
    def rear_right_wheel_position(self) -> Vector3: ...

    @property
    def direction(self) -> Vector3: ...


DriverName = str
TrackId = str
TrackConfigurationId = str
CarId = str
LapTimeMs = int


class GhostFrameFinder:
    _frames: list[GhostFrame]

    _last_nearest_frame_index: int

    def __init__(self, frames: list[GhostFrame]) -> None: ...

    def frame_index_near(self, x: float, y: float, z: float) -> int: ...


class Ghost:
    driver_name: DriverName
    track_id: TrackId
    track_configuration_id: TrackConfigurationId
    car_id: CarId
    lap_time_ms: LapTimeMs
    frames: list[GhostFrame]

    _car_center_distance_from_start_by_frame: list[float]

    def __init__(self, driver_name: DriverName, track_id: TrackId, track_configuration_id: TrackConfigurationId, car_id: CarId, lap_time_ms: LapTimeMs, frames: list[GhostFrame]) -> None: ...

    @property
    def frame_time_ms(self) -> float: ...

    def car_center_distance_from_start_at(self, frame_index: int) -> float: ...

    def frame_finder(self) -> GhostFrameFinder: ...


def unpack_unsigned_int(reader: BufferedIOBase) -> int: ...


def unpack_string(reader: BufferedIOBase) -> str: ...


def unpack_4x4_matrix(reader: BufferedIOBase) -> Matrix4x4: ...


class _GhostParser4:
    driver_name: DriverName
    track_id: TrackId
    track_configuration_id: TrackConfigurationId
    car_id: CarId
    lap_time_ms: LapTimeMs

    _reader: BufferedIOBase

    def __init__(self, reader: BufferedIOBase, driver_name: DriverName, track_id: TrackId, track_configuration_id: TrackConfigurationId, car_id: CarId, lap_time_ms: LapTimeMs) -> None: ...

    def parse(self) -> Ghost: ...


class _GhostParser3:
    driver_name: DriverName
    track_id: TrackId
    track_configuration_id: TrackConfigurationId
    car_id: CarId

    reader: BufferedIOBase

    def __init__(self, reader: BufferedIOBase, driver_name: DriverName, track_id: TrackId, track_configuration_id: TrackConfigurationId, car_id: CarId) -> None: ...

    def parse(self) -> tuple[LapTimeMs, _GhostParser4]: ...


class _GhostParser2:
    driver_name: DriverName
    track_id: TrackId
    track_configuration_id: TrackConfigurationId

    _reader: BufferedIOBase

    def __init__(self, reader: BufferedIOBase, driver_name: DriverName, track_id: TrackId, track_configuration_id: TrackConfigurationId) -> None: ...

    def parse(self) -> tuple[CarId, _GhostParser3]: ...


class _GhostParser1:
    driver_name: DriverName
    track_id: TrackId

    _reader: BufferedIOBase

    def __init__(self, reader: BufferedIOBase, driver_name: DriverName, track_id: TrackId) -> None: ...

    def parse(self) -> tuple[TrackConfigurationId, _GhostParser2]: ...


class _GhostParser0:
    driver_name: DriverName

    _reader: BufferedIOBase

    def __init__(self, reader: BufferedIOBase, driver_name: DriverName) -> None: ...

    def parse(self) -> tuple[TrackId, _GhostParser1]: ...


class GhostParser:
    _reader: BufferedIOBase

    def __init__(self, reader: BufferedIOBase) -> None: ...

    def parse(self) -> tuple[DriverName, _GhostParser0]: ...


def parse(reader: BufferedIOBase) -> Ghost: ...
