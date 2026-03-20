Follow Path
===========

Ensure the path file exists:

``teach_and_repeat/data/teleop_data.txt``

Navigate and source:

.. code-block:: bash

   cd ~/lognav_ws
   source /opt/ros/humble/setup.bash
   source ./install/setup.bash

Launch navigation:

.. code-block:: bash

   ros2 launch lognav_navigation navigation.launch.py

Run:

.. code-block:: bash

   ros2 run teach_and_repeat repeat_bezier_path.py

Set the pose using "2DPoseEstimate".

The robot will start following the path.