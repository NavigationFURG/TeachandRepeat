Demonstrate Path
================

Grant permissions:

.. code-block:: bash

   sudo chmod 666 /dev/ttyUSB0

Navigate and source:

.. code-block:: bash

   cd ~/lognav_ws
   source /opt/ros/humble/setup.bash
   source ./install/setup.bash

Launch navigation:

.. code-block:: bash

   ros2 launch lognav_navigation navigation.launch.py

Use "Pose2DEstimation" to define the initial position.

Start teleoperation:

.. code-block:: bash

   ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=hoverboard_base_controller/cmd_vel_unstamped

Start teach node:

.. code-block:: bash

   ros2 run teach_and_repeat teach_path_coords.py

Press ENTER to start recording.

Save path:

.. code-block:: bash

   ros2 service call /save_path teach_and_repeat/srv/SavePath