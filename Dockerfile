FROM osrf/ros:humble-desktop

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool \
    build-essential \
    git \
    vim \
    python3-pip \
    # GUI / display dependencies
    libgl1 \
    libglx-mesa0 \
    libgl1-mesa-dri \
    mesa-utils \
    x11-apps \
    # Navigation 2
    ros-humble-navigation2 \
    ros-humble-nav2-bringup \
    # tf_transformations
    ros-humble-tf-transformations \
    ros-humble-turtlebot3-gazebo \
    && rm -rf /var/lib/apt/lists/*

RUN rosdep init || true && rosdep update

# Remove apt-managed matplotlib to avoid duplicate version conflicts
RUN apt-get remove -y python3-matplotlib || true

# Install pinned Python requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --ignore-installed -r /tmp/requirements.txt

WORKDIR /teach_repeat_ws

RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc
ENV TURTLEBOT3_MODEL=waffle
ENV GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/opt/ros/$ROS_DISTRO/share/turtlebot3_gazebo/models


ENV QT_X11_NO_MITSHM=1

CMD ["bash"]
