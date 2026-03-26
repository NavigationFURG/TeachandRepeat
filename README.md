# Teach and Repeat using Bézier Curves
This repository implements a **Teach and Repeat** (T&R) navigation system for mobile robots, allowing them to autonomously follow previously demonstrated paths.
<!-- TODO: Add a better description-->

## Dependencies
- [ROS 2 Humble](https://docs.ros.org/en/humble/Installation.html);
- Ubuntu 22.04;
- Colcon Common Extensions;

## Methods
There are two methods to follow the demonstrated path:

- **Dot-to-dot (nodes/repeat_path_coords.py)**: The robot follows a Pure Pursuit-like approach where it intercepts a look-ahead point. Once it reaches this point, a new point further along the path is set as the next target.
- **Bezier curve based (nodes/repeat_bezier_path.py)**: The robot simulates multiple potential paths ahead using Bézier curves and selects the optimal path based on predefined criteria.

## Run

After setting up the environment, follow these steps to run the LogNav system:

Grant necessary permissions to the USB device:
```bash
sudo chmod 666 /dev/ttyUSB0
```

### Demonstrate Path

To demonstrate a path, follow these steps:

Navigate to the root of your workspace and source it:
```bash
cd ~/lognav_ws
source /opt/ros/humble/setup.bash # Source ROS
source ./install/setup.bash # Source the workspace
```

Launch the navigation system:
```bash
ros2 launch lognav_navigation navigation.launch.py
```
**You must use 'Pose2DEstimation' to define the initial position.**

**Open another terminal**, navigate to the root of your workspace and source it:
```bash
cd ~/lognav_ws
source /opt/ros/humble/setup.bash # Source ROS
source ./install/setup.bash # Source the workspace
```

Start the teleoperation node:
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=hoverboard_base_controller/cmd_vel_unstamped
```

Control the robot using the following keys:
- `I` to move forward
- `K` to move backward
- `J` to turn left
- `L` to turn right
- `Q` to increase speed
- `Z` to decrease speed
- `Space` to stop

**Open another terminal**, navigate to the root of your workspace and source it:
```bash
cd ~/lognav_ws
source /opt/ros/humble/setup.bash # Source ROS
source ./install/setup.bash # Source the workspace
```

To start the teach node:
```bash
ros2 run teach_and_repeat teach_path_coords.py
```
| Parameter         | Default Value | Description                                                                 |
|-------------------|---------------|-----------------------------------------------------------------------------|
| `reference_frame` | `map`         | The reference frame for the path points. If set to `map`, the points are relative to the map frame. If set to `odom`, the points are relative to the robot's odometry frame. |
|`teach_orientation`| `false`       | If orientation is to be recorded, along with (x, y) points. If set to `true`, each point will have (x,y,θ), where θ is the yaw robot pose. Useful for global planners from Nav2 that must have robot's orientation, such as Hybrid A*.|
After that, you have to press `ENTER` to start recording.

If needed, you can start the node customizing flag values:
```bash
ros2 run teach_and_repeat teach_path_coords.py --ros-args -p reference_frame:=map -p teach_orientation:=true
```

To save the current path, you have to open another terminal and use this command:
```bash
ros2 service call /teach_and_repeat/teach/save_path teach_and_repeat/srv/SavePath

```

Using the command above the default path name is `path_coords`. To change it, use the following command:
```bash
ros2 service call /teach_and_repeat/teach/save_path teach_and_repeat/srv/SavePath "{path_name: 'DESIRED_PATH_NAME'}"

```

To end the demonstration press CTRL + C.

### Follow Path

To follow a path, first ensure that the coordinates from the path demonstration are stored in the `teach_and_repeat/data/teleop_data.txt` file. This file is also the default file read during the path following process. Make sure you start from the same point where the demonstration began.

Navigate to the root of your workspace and source it:
```bash
cd ~/lognav_ws
source /opt/ros/humble/setup.bash # Source ROS
source ./install/setup.bash # Source the workspace
```

Launch the navigation system:
```bash
ros2 launch lognav_navigation navigation.launch.py
```

**Open another terminal**, navigate to the root of your workspace and source it:
```bash
cd ~/lognav_ws
source /opt/ros/humble/setup.bash # Source ROS
source ./install/setup.bash # Source the workspace
```

Then, run the path following node:
```bash
ros2 run teach_and_repeat repeat_bezier_path.py
```

**After starting the repeat node, set a pose using '2DPoseEstimate'. The robot will immediately begin following the path.**