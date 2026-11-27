# Zone

A single file library parsing `.ghost` files of Assetto Corsa. `zone.py` is compatible with Python 3.3.5 (used by Assetto Corsa).

## Usage

### Python

```python
import zone

if __name__ == '__main__':
    with open("ghosts/ks_mazda_mx5_nd_SM_267690.ghost", "rb") as stream:
        ghost = zone.parse(stream)

        print(f"Driver: {ghost.driver_name}")
        print(f"Track: {ghost.track_id}/{ghost.track_configuration_id}")
        print(f"Car: {ghost.car_id}")
        print(f"Lap time: {ghost.lap_time_ms}ms")
        print(f"Frames count: {len(ghost.frames)}, frame time: {ghost.frame_time_ms}ms")
        print(f"Frame 0:")
        print(f"\tcenter: {ghost.frames[0].car_center_position}")
        print(f"\tdirection: {ghost.frames[0].direction}")
```
```
Driver: Thurst
Track: ek_myogi/downhill_real
Car: ks_mazda_mx5_nd
Lap time: 267690ms
Frames count: 2076, frame time: 129.00722891566264ms
Frame 0:
	center: [-2179.383544921875, 4.336601734161377, 27.93623161315918]
	direction: [1.96337890625, -0.00831747055053711, -1.2283210754394531]
```

## `.ghost` format

The reverse-engineering was done by Gemini so non-verified data may not be true.

The byte order is little-endian and the file has the following layout:

| Size (in bytes) | Type | Verified | Description | Example |
|:-:|:-:|:-:|---|---|
| `4` | `uint`  | ❌ | Format version | `4`  |
| `4` |  `uint`   |    ❌    | Lap / record flag     | `1`|
|   `4`   |     `uint`      |      ✅      | Size in bytes of the next type| `12`   |
|    |   `byte[]`   |       ✅       | UTF-8 encoded string representing the driver's name               | エウレカ (`0xe3, 0x82, 0xa8, 0xe3, 0x82, 0xa6, 0xe3, 0x83, 0xac, 0xe3, 0x82, 0xab`)       |
|     `4`     |       `uint`       |       ✅       | Size in bytes of the next type                                                                   | `14`                                                                                          |
|             |               `byte[]`               |                | UTF-8 encoded string representing the track's identifier                                                                                                 | ek_happogahara (`0x65, 0x6b, 0x5f, 0x68, 0x61, 0x70, 0x70, 0x6f, 0x67, 0x61, 0x68, 0x61, 0x72, 0x61`)                                                                                              |
|     `4`     |       `uint`       |       ✅      | Size in bytes of the next type                                                                   | `13`                                                                                          |
|             |          `byte[]`          |        ✅       | UTF-8 encoded string representing the identifier of the track's configuration            | outbound_real (`0x6f, 0x75, 0x74, 0x62, 0x6f, 0x75, 0x6e, 0x64, 0x5f, 0x72, 0x65, 0x61, 0x6c`)                                                                                              |
|      `4`       |               `uint`               |         ✅        | Size in bytes of the next type                                                                                                                                                                              | `19`                                                                                                                                                                                            |
|                |                  `byte[]`                  |         ✅        | UTF-8 encoded string representing the car's identifier                                                                                                                                                                                                            | ddm_honda_s2000_ap1 (`0x64, 0x64, 0x6d, 0x5f, 0x68, 0x6f, 0x6e, 0x64, 0x61, 0x5f, 0x73, 0x32, 0x30, 0x30, 0x30, 0x5f, 0x61, 0x70, 0x31`)                                                                                                                                                                                                |
|       `4`         |                     `uint`                       |          ✅         | Lap time in milliseconds                                                                                                                                                                                                                                                                  | `294 197` (4m54.197s)                                                                                                                                                                                                                                                                                                                                               |
|        `4`           |                      `uint`                        |          ✅           | Number of evenly recorded frames                                                                                                                                                                                                                                                                                          | `2 281`                                                                                                                                                                                                                                                                                                                                                                    |
|                      |                            `Frame[]`                               |           ✅            | Array of frames containing information about the car at a moment                                                                                                                                                                                                                                                                                                                   |                                                                                                                                                                                                                                                                                                                                                                            |

`Frame` has the following layout:

| Size (in bytes) | Type | Verified | Description |
|:-:|:-:|:-:|---|
|   `64`   | `Matrix`  |✅   | Car's center matrix  |
|   `64`   | `Matrix`  |✅   | Car's front left wheel matrix  |
|   `64`   | `Matrix`  |✅   | Car's front right wheel matrix  |
|   `64`   | `Matrix`  |✅   | Car's rear left wheel matrix  |
|   `64`   | `Matrix`  |✅   | Car's rear right wheel matrix  |
|   `64`   | `Matrix`  |❌   | Car's front left wheel suspension/steer matrix  |
|   `64`   | `Matrix`  |❌   | Car's front right wheel suspension/steer matrix  |
|   `64`   | `Matrix`  |❌   | Car's rear left wheel suspension/steer matrix  |
|   `64`   | `Matrix`  |❌   | Car's rear right wheel suspension/steer matrix  |

`Matrix` is 4x4 "world transform matrix" and has the following layout:

| Size (in bytes) | Type | Verified | Description |
|:-:|:-:|:-:|---|
| `4`  | `float`  |❌   | Rotation matrix's element at row 0 and column 0   |
| `4`  | `float`  |❌   | Rotation matrix's element at row 0 and column 1  |
| `4`  | `float`  |❌   | Rotation matrix's element at row 0 and column 2  |
| `4`  | `0`  |❌   | Constant  |
| `4`  | `float`  |❌   | Rotation matrix's element at row 1 and column 0  |
| `4`  | `float`  |❌   | Rotation matrix's element at row 1 and column 1  |
| `4`  | `float`  |❌   | Rotation matrix's element at row 1 and column 2  |
| `4`  | `0`  |❌   | Constant  |
| `4`  | `float`  |❌   | Rotation matrix's element at row 2 and column 0  |
| `4`  | `float`  |❌   | Rotation matrix's element at row 2 and column 1  |
| `4`  | `float`  |❌   | Rotation matrix's element at row 2 and column 2  |
| `4`  | `0`  |❌   | Constant  |
| `4`  | `float`  |✅   | Position on the X axis in the Assetto Corsa world coordinate system  |
| `4`  | `float`  |✅   | Position on the Y axis in the Assetto Corsa world coordinate system  |
| `4`  | `float`  |✅   | Position on the Z axis in the Assetto Corsa world coordinate system  |
| `4`  | `1`   |❌   | Constant   |