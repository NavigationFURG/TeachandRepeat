# FBOT Teach and Repeat Framework
FBOT Teach and Repeat (T&R) is a framework for mobile robots that allows them to autonomously follow previously demonstrated paths. It consists of two main modules: the Teach module, which records the robot’s movements during a demonstration, and the Repeat module, which enables the robot to follow the recorded path autonomously. Developed by the FBOT team, it works out-of-the-box for differential drive robots and can be adapted to other types of robots with simple modifications.

The Repeat module can be configured to use different approaches for path following, such as a custom path follower based on a Dynamic Window Approach (DWA), using [Bézier curves for path generation and smoothing](https://ieeexplore.ieee.org/document/10837801), or a waypoint following method using local and global planners provided by [Navigation Stack 2 (Nav2)](https://docs.nav2.org/).

Read the official documentation, including a step-by-step tutorial and example videos, [here!](https://teachandrepeat.readthedocs.io/en/latest/)

## Quick Install

### Dependencies
- ROS2 Humble;
- Ubuntu 22.04;
- Colcon common extensions;
- Turtlebot3 simulation.
- We also provide a Dockerfile for easier set-up in non-ubuntu 22.04 machines. Read it in the [respective branch](https://github.com/NavigationFURG/TeachandRepeat/blob/feat/docker/Dockerfile) for more details.

First, create a workspace directory and navigate into it:

```
mkdir -p teach_repeat_ws/src
cd teach_repeat_ws/src
```

Clone this repository along with its submodules:

```
git clone --recurse-submodules https://github.com/NavigationFURG/TeachandRepeat.git
```

Make the installation script executable and run it with superuser privileges:

```
cd TeachandRepeat/
chmod +x install.sh
sudo ./install.sh
```

Navigate back to your workspace and initialize rosdep:

```
cd ~/teach_repeat_ws
sudo rosdep init
rosdep update
rosdep install --from-paths src -y --ignore-src --rosdistro humble
```

Then, build the workspace!

```
cd ~/teach_repeat_ws
source /opt/ros/humble/setup.bash
colcon build
source ./install/setup.bash
```

As our framework is integrated with Navigation Stack 2 features, you will also need to install it. 

```
sudo apt install ros-humble-navigation2
sudo apt install ros-humble-nav2-bringup
```

We also use Turtlebot3 packages as a example in tutorial, so we recommend to install it:

```
sudo apt install ros-humble-turtlebot3
sudo apt install ros-humble-turtlebot3-gazebo
```

And that is it! Have fun with our project. Remember to follow the [tutorial](https://teachandrepeat.readthedocs.io/en/latest/tutorial/getting_started.html) for more information. For more information about [Navigation Stack 2](https://docs.nav2.org/) and [Turtlebot](https://emanual.robotis.com/docs/en/platform/turtlebot3/quick-start/) features, please proceed to their respective pages.
