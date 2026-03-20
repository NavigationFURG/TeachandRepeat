Follow Path
===========

Before starting, ensure the coordinates are stored in `teach_and_repeat/data/teleop_data.txt`. Start from the same point used in the demonstration.

1. Navigate to the root of your workspace and source it:

.. code-block:: bash

   cd ~/lognav_ws
   source /opt/ros/humble/setup.bash
   source ./install/setup.bash

2. Launch the navigation system:

.. code-block:: bash

   ros2 launch lognav_navigation navigation.launch.py

3. Open another terminal, source the workspace, and run the repeat node:

.. code-block:: bash

   ros2 run teach_and_repeat repeat_bezier_path.py

4. After starting, set a pose using '2DPoseEstimate'. The robot will immediately begin following the path.