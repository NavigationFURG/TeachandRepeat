.. _getting_started:

1. Getting Started
###################

This repository implements a **Teach and Repeat** (T&R) navigation system for mobile robots, allowing them to autonomously follow previously demonstrated paths.

Requirements
************

- `ROS 2 Humble <https://docs.ros.org/en/humble/Installation.html>`_;
- Ubuntu 22.04;
- Colcon Common Extensions;
- Turtlebot3 simulation.


.. important::

    This documentation is based on ROS2 Humble, which is the recommended ROS version for this project. While it may be possible to use other ROS2 distributions, fine-tuning may be required.


Installation
************

To set up the Teach and Repeat system, follow these steps:

First, create a workspace directory and navigate into it:

.. code-block:: bash

    mkdir -p teach_repeat_ws/src
    cd teach_repeat_ws/src

Clone this repository along with its submodules:

.. code-block:: bash

    git clone --recurse-submodules https://github.com/NavigationFURG/TeachandRepeat.git

Make the installation script executable and run it with superuser privileges:

.. code-block:: bash

    cd TeachandRepeat/
    chmod +x install.sh
    sudo ./install.sh

Navigate back to your workspace and initialize `rosdep`:

.. code-block:: bash

    cd ~/teach_repeat_ws
    sudo rosdep init

Update `rosdep` to fetch the latest package information:

.. code-block:: bash

    rosdep update

Install the required ROS package dependencies:

.. code-block:: bash

    rosdep install --from-paths src -y --ignore-src --rosdistro humble

Once the dependencies are installed, proceed with building the workspace. First, source ROS2 and the workspace environment:

.. code-block:: bash

    cd ~/teach_repeat_ws
    source /opt/ros/humble/setup.bash
    colcon build
    source ./install/setup.bash

.. note::

    If you are using Zsh as your shell, replace `setup.bash` with `setup.zsh`:

    .. code-block:: zsh

        source /opt/ros/humble/setup.zsh
        colcon build
        source ./install/setup.zsh

Install Nav2 (required for navigation integration):

.. code-block:: bash

    sudo apt install ros-humble-navigation2 
    sudo apt install ros-humble-nav2-bringup

Install the TurtleBot3 simulation for Gazebo Classic:

.. code-block:: bash

    sudo apt install ros-humble-turtlebot3
    sudo apt install ros-humble-turtlebot3-gazebo

Configure TurtleBot3 environment variables:

.. code-block:: bash

    source /opt/ros/humble/setup.bash 
    export TURTLEBOT3_MODEL=burger  # Iron and older only with Gazebo Classic 
    export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/opt/ros/humble/share/turtlebot3_gazebo/models # Iron and older only with Gazebo Classic

.. note::

    These environment variables must be set **every time** before launching the simulation.

.. important::

    All examples in this documentation are based on **Gazebo Classic**, which is fully supported and stable.

    The system is expected to work with newer versions of Gazebo.