.. _getting_started:

Getting Started
###############

This repository implements a **Teach and Repeat** (T&R) navigation system for mobile robots, allowing them to autonomously follow previously demonstrated paths.

Dependencies
************
- `ROS 2 Humble <https://docs.ros.org/en/humble/Installation.html>`_
- Ubuntu 22.04
- Colcon Common Extensions
- Turtlebot3 simulation;

Installation
************
To set up the Teach and Repeat system, follow these steps:

First, create a workspace directory and navigate into it:

.. code-block:: zsh

    mkdir -p teach_repeat_ws/src
    cd teach_repeat_ws/src

Clone this repository along with its submodules:

.. code-block:: zsh

    git clone --recurse-submodules https://github.com/jardeldyonisio/teach_and_repeat.git

Make the installation script executable and run it with superuser privileges:

.. code-block:: zsh

    cd teach_and_repeat/
    chmod +x install.sh
    sudo ./install.sh

Navigate back to your workspace and initialize `rosdep`:

.. code-block:: zsh

    cd ~/teach_repeat_ws
    sudo rosdep init

Update `rosdep` to fetch the latest package information:

.. code-block:: zsh

    rosdep update

Install the required ROS package dependencies:

.. code-block:: zsh

    rosdep install --from-paths src -y --ignore-src --rosdistro humble

Once the dependencies are installed, proceed with building the workspace. First, source ROS2 and the workspace environment:

.. code-block:: bash

    cd ~/teach_repeat_ws
    source /opt/ros/humble/setup.bash
    source ./install/setup.bash
    colcon build

.. note::

    If you are using Zsh as your shell, replace `setup.bash` with `setup.zsh`:

    .. code-block:: zsh

        source /opt/ros/humble/setup.zsh
        source ./install/setup.zsh
        colcon build

Install the TurtleBot3 simulation for Gazebo Classic:

.. code-block:: bash

    sudo apt install ros-humble-turtlebot3
    sudo apt install ros-humble-turtlebot3-gazebo
