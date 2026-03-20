Demonstrate Path
================

To demonstrate a path, follow these steps:

1. Navigate to the root of your workspace and source it:

.. code-block:: bash

   cd ~/lognav_ws
   source /opt/ros/humble/setup.bash
   source ./install/setup.bash

2. Launch the navigation system:

.. code-block:: bash

   ros2 launch lognav_navigation navigation.launch.py

**Note:** Use 'Pose2DEstimation' to define the initial position.

3. Open another terminal, source the workspace, and start the teleoperation node:

.. code-block:: bash

   ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=hoverboard_base_controller/cmd_vel_unstamped

Control keys:

- `I`: move forward
- `K`: move backward
- `J`: turn left
- `L`: turn right
- `Q`: increase speed
- `Z`: decrease speed
- `Space`: stop

4. Open another terminal, source the workspace, and start the teach node:

.. code-block:: bash

   ros2 run teach_and_repeat teach_path_coords.py

Parameters
----------

.. list-table::
   :header-rows: 1

   * - Parameter
     - Default Value
     - Description
   * - `reference_frame`
     - `map`
     - The reference frame for the path points. 'map' is relative to the map frame, 'odom' relative to the robot's odometry frame.

5. Press `ENTER` to start recording.

6. Save the current path:

.. code-block:: bash

   ros2 service call /save_path teach_and_repeat/srv/SavePath

To change the path name:

.. code-block:: bash

   ros2 service call /save_path teach_and_repeat/srv/SavePath "{path_name: 'DESIRED_PATH_NAME'}"

End demonstration: CTRL + C