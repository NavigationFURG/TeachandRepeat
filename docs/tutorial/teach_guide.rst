2. Teach Guide
================

To first-time users of the teach module from T&R package, follow the instructions below, It is expected that you already have followed the installation steps in the :ref:`getting_started` guide.:

1. Navigate to the root of your workspace and source it:

.. code-block:: bash

   cd ~/teach_repeat_ws
   source /opt/ros/humble/setup.bash
   source ./install/setup.bash

2. Export the turtlebot3 models, if using Gazebo Classic.

.. code-block:: bash
 
   export TURTLEBOT3_MODEL=burger  # Iron and older only with Gazebo Classic  
   export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/opt/ros/humble/share/turtlebot3_gazebo/models # Iron and older only with Gazebo Classic


3. Launch the turtlebot simulation and navigation system:

.. code-block:: bash

   ros2 launch nav2_bringup tb3_simulation_launch.py headless:=False

**Note:** Do not forget to use `Pose2DEstimation` to define the robots initial position!

Your interface should look like this:

.. image:: ../images/simulation.png
   :align: center

4. Open another terminal, source the workspace, and start the teach node from T&R:

.. code-block:: bash

   ros2 run teach_and_repeat teach_path_coords.py

After that, press `ENTER` to start recording.

5. In another terminal, source the workspace, and install the teleoperation node (if not already installed):

.. code-block:: bash

   sudo apt install ros-humble-teleop-twist-keyboard

6. In another terminal, source the workspace, and start the teleoperation node:

   .. code-block:: bash

      ros2 run teleop_twist_keyboard teleop_twist_keyboard

      #or

      ros2 run teach_and_repeat turtle_teleop.py

**Note:** Now, you can control the robot, it's recommended to create a short, linear path just for evaluation.


7. In another terminal, source the workspace `source ./install/setup.bash`, and call the service to save the path:

.. code-block:: bash

   ros2 service call /teach_and_repeat/teach/save_path teach_and_repeat/srv/SavePath "{path_name: 'your_path_name'}"

Now, you can close the teleoperation node and the navigation system, and then you can use the saved path for repeating it.

