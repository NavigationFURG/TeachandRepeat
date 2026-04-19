FROM osrf/ros:jazzy-desktop

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
    ros-jazzy-navigation2 \
    ros-jazzy-nav2-bringup \
    # tf_transformations
    ros-jazzy-tf-transformations \
    && rm -rf /var/lib/apt/lists/*

RUN rosdep init || true && rosdep update

# Remove apt-managed matplotlib to avoid duplicate version conflicts
RUN apt-get remove -y python3-matplotlib || true

# Install pinned Python requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --break-system-packages --ignore-installed -r /tmp/requirements.txt

WORKDIR /teach_repeat_ws

RUN echo "source /opt/ros/jazzy/setup.bash" >> /root/.bashrc

ENV QT_X11_NO_MITSHM=1

CMD ["bash"]
