Teaching Method Overview
========================

1. Overview
-----------

The Teaching method is a path learning technique that allows a robot to record its trajectory while being manually guided through an environment. The recorded path can later be replayed by the Repeat module for autonomous navigation. This section provides a detailed explanation of how the teaching mechanism works, its core parameters, data recording formats, and reference frame options.


2. Architecture and Core Components
-----------------------------------

The teaching system is implemented through the **TeachPathCoords** ROS2 node, which runs as a standalone service that:

- Subscribes to robot pose data from either odometry (/odom) or localization (/amcl_pose);
- Records waypoints at configurable time intervals as the robot moves;
- Stores path data in a structured text format;
- Can manage named dock locations (special waypoints within the path);
- Provides real-time visualization in RViz through marker publishers;
- Exposes ROS2 service interfaces for saving paths and registering docks.


3. Main Parameters
------------------

The teaching module is controlled by two primary parameters that determine how data is captured and stored:

3.1. reference_frame
~~~~~~~~~~~~~~~~~~~~

Type: string  
Accepted values: ``'odom'`` or ``'map'``  


This parameter determines which reference frame the robot's position will be recorded relative to, and which sensor provides the pose data.

- **'odom' frame**: The node subscribes to the ``/odom`` topic (Odometry message). This provides relative positioning based on wheel odometry or other proprioceptive sensors. The odometry frame is local to the robot's starting position and accumulates drift over time. Recording in the odom frame is faster and more responsive, making it suitable for a more dense path. The issue, however, is that if the odometry is based only on the wheel encoder, it may not be as accurate as the other frame option 'map'.

- **'map' frame**: The node subscribes to the ``/amcl_pose`` topic (PoseWithCovarianceStamped message). This provides globally localized position through the Adaptive Monte Carlo Localization algorithm from a Navigation Stack 2 setup. The map frame is global and consistent with a pre-built map, reducing drift but requiring a map to be loaded. Recording in the map frame produces globally consistent paths.

The choice between odom and map depends on the application context:
- Use **'odom'** for faster feedback and local path recording without map dependency;
- Use **'map'** for long-distance paths or when consistency is required.


3.2. teach_orientation
~~~~~~~~~~~~~~~~~~~~~~

Type: boolean  
Accepted values: ``True`` or ``False``  


This parameter controls whether the robot's heading (yaw angle) is recorded along with its position.

- **False** (default): Only (x, y) coordinates are recorded. Each waypoint contains 2D Cartesian position information. The repeat system will then compute optimal orientations during path following, or the user can specify desired orientations separately. *Repeating a path with Bézier fitting will, by default, expect teach_orientation to be false*.

- **True**: Both position (x, y) and orientation (yaw) are recorded. Each waypoint contains 3D position-orientation information. The repeat system will attempt to follow both the spatial path and the recorded headings, useful for tasks where the robot's direction is critical (e.g., docking, manipulation, or paths that require specific approach angles). *By default, Repeating a path with Navigation Stack 2 Waypoint follower will expect teach_orientation to be true*.


4. Operating Principles and Data Recording
------------------------------------------

4.1. Recording Lifecycle
~~~~~~~~~~~~~~~~~~~~~~~~

The teaching process follows these steps:

1. **Initialization**: The TeachPathCoords node starts and waits for user input. A message is printed to the terminal: "Press ENTER to start recording the path...".

2. **Standby Mode**: The node continuously subscribes to odometry/localization data but does not record points. Markers are not published.

3. **Recording Activation**: When the user presses ENTER in the terminal, the ``recording`` flag is set to True. The node logs: "Recording started. Saving coordinates..." and begins capturing waypoints.

4. **Active Recording**: For each odometry/localization update received while ``recording`` is True:
   
   - The current robot position (and orientation if ``teach_orientation=True``) is extracted;
   - A 1.5-second sleep is introduced to prevent over-sampling of data points. This can be adjusted in the code if needed;
   - The waypoint is appended to the internal ``path_coords`` list;
   - The waypoint is added to a visualization marker and published to RViz.

5. **Termination**: When the user presses CTRL+C, the process terminates without automatically saving. The user must explicitly save the path using the service call.

4.2. Time Interval and Sampling Rate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The node implements a deliberate 1.5-second sleep between consecutive waypoint recordings. This interval serves multiple purposes:

- **Data Efficiency**: Reduces the number of waypoints, preventing unnecessary storage and computational overhead;
- **Sensor Rate Matching**: Approximates typical localization update rates (AMCL publishes at ~10-30 Hz with built-in filtering);
- **Stability**: Allows odometry/localization estimates to stabilize before recording the next point;

The resulting sampling rate of approximately one waypoint per 1.5 seconds means a 100-meter path with 10 meters between waypoints would require approximately 150 seconds (2.5 minutes) to record. This is very biased to our experimental setup with turtlebot and the industrial robot, and can be easily modified in the source code for your needs.

4.3. Data Point Extraction Process
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When the callback function receives a new pose message, the following extraction occurs:

For **teach_orientation=False**:
   - Extracts: x = pose.pose.position.x, y = pose.pose.position.y;
   - Creates: geometry_msgs.msg.Point object containing (x, y);
   - Stores: Point object in path_coords list;
   - Format in file: ``x,y``.

For **teach_orientation=True**:
   - Extracts: x = pose.pose.position.x, y = pose.pose.position.y, yaw = pose.pose.orientation.z;
   - Creates: Custom OrientedPoint object containing (x, y, yaw);
   - Stores: OrientedPoint object in path_coords list;
   - Format in file: ``x,y,yaw``.

Note: The z-coordinate of orientation is used to represent the yaw angle (rotation around the vertical axis). This is a 2D navigation convention where yaw is the heading angle in radians.


5. File Storage Format
----------------------

5.1. File Naming and Location
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Recorded paths are saved in the ``path_saves/`` directory at the root of the TeachandRepeat workspace:

``<workspace>/src/TeachandRepeat/path_saves/<path_name>.txt``

The user provides the ``path_name`` when calling the save service. If no name is provided, the default name ``path_coords`` is used.

5.2. Text Format for Position-Only Paths (teach_orientation=False)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each line in the text file contains two comma-separated floating-point values representing the x and y coordinates of a single waypoint, just as the example below:

::

    1.234,5.678
    1.456,5.890
    1.678,6.012
    1.890,6.234
    2.012,6.456

Format specification:
- One waypoint per line;
- Decimal values separated by comma (no spaces);
- Each value represents meters from the initial pose estimation. If ``/odom`` was chosen as the reference frame, it is relative to the initial robot pose. If ``/amcl_pose``, it is relative to the first 2d pose estimate given;
- No header or metadata, but it would be cool to have as future works!

5.3. Text Format for Oriented Paths (teach_orientation=True)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each line in the text file contains three comma-separated floating-point values representing the x and y coordinates and the yaw angle of a single waypoint:

::

    1.234,5.678,0.123
    1.456,5.890,0.145
    1.678,6.012,0.167
    1.890,6.234,0.189
    2.012,6.456,0.201

Format specification:
- One waypoint per line;
- Three decimal values separated by commas (no spaces);
- First two values: x, y coordinates in meters;
- Third value: yaw angle in radians;
- No header or metadata.

5.4. File Writing Logic
~~~~~~~~~~~~~~~~~~~~~~~

The file is written using one of two functions depending on the ``teach_orientation`` setting:

- **teach_orientation=False**: Uses ``save_coords_to_file()`` function, which iterates through the Point objects and formats each as ``"{},{}\n".format(point.x, point.y)``.

- **teach_orientation=True**: Uses ``saveOrientedCoordsToFile()`` function, which iterates through OrientedPoint objects and formats each as ``"{},{},{}\n".format(point.x, point.y, point.yaw)``.

Both functions create the parent directory if it does not exist and use UTF-8 encoding with newline terminators on each record.


.. 6. Reference Frame Selection
.. ----------------------------

.. 6.1. Odometry Frame (/odom)
.. ~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. When ``reference_frame='odom'``:

.. - **Data source**: ``/odom`` topic (nav_msgs/Odometry message)
.. - **Frame properties**: Local, egocentric, drift-prone
.. - **Characteristics**:
..   - Position accumulates drift over long distances
..   - Maintains relative accuracy in short-term paths
..   - Unaffected by map quality or global localization
..   - Provides immediate data without waiting for localization convergence
  
.. - **Use cases**:
..   - Paths in environments without pre-built maps
..   - Short-distance navigation (< 50 meters)
..   - Indoor spaces with good odometric accuracy (smooth floors, low-slip wheels)
..   - Development and testing before map deployment
  
.. - **Limitations**:
..   - Accumulated errors over long paths
..   - Requires proper odometry calibration for accuracy
..   - Path validity limited to the current robot session
..   - Cannot be reused across different robot initializations without careful alignment

.. 6.2. Map Frame (/map)
.. ~~~~~~~~~~~~~~~~~~~~~

.. When ``reference_frame='map'``:

.. - **Data source**: ``/amcl_pose`` topic (geometry_msgs/PoseWithCovarianceStamped message from AMCL)
.. - **Frame properties**: Global, allocentric, drift-free
.. - **Characteristics**:
..   - Position is corrected by global localization algorithm
..   - Maintains consistency with environment map
..   - Requires active localization (map + laser scanner data)
..   - Provides stable absolute coordinates

.. - **Use cases**:
..   - Long-distance paths (> 50 meters)
..   - Paths that should be reused across multiple robot sessions
..   - Outdoor paths or large-scale environments
..   - Applications requiring guaranteed global consistency
  
.. - **Limitations**:
..   - Requires a pre-built map of the environment
..   - Depends on laser scanner and map matching quality
..   - Localization must be initialized correctly before starting recording
..   - Requires AMCL or similar localization system to be running

.. 6.3. Frame Selection Impact on Repeat Performance
.. ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. The reference frame choice directly affects how the Repeat module performs path following:

.. - **Odom-based paths**: Repeat module assumes the robot starts at the same initial position with consistent odometry. Any significant change in starting position will cause path deviation.

.. - **Map-based paths**: Repeat module can relocalize to the global map coordinate system, allowing path following from any starting position that matches the map. This provides flexibility and robustness in multi-run scenarios.



6. Real-Time Visualization in RViz
----------------------------------

6.1. Published Markers
~~~~~~~~~~~~~~~~~~~~~~

During path recording, the TeachPathCoords node publishes visualization markers to aid in real-time monitoring:

- **Path marker** (RED LINE): published to ``/teach_and_repeat/teach/path_marker``
  - Includes all recorded waypoints connected in order.

6.2. Frame Consistency
~~~~~~~~~~~~~~~~~~~~~~

All markers use the same reference frame as the pose data (either "odom" or "map"). The markers are updated with current timestamp headers before each publication.


7. Service Interface
--------------------

7.1. SavePath Service
~~~~~~~~~~~~~~~~~~~~~

Service name: ``/teach_and_repeat/teach/save_path``  
Service type: ``teach_and_repeat/SavePath``

Request parameters:
- **path_name** (string): Name for the saved path file. If empty, defaults to "path_coords".

Response parameters:
- **success** (boolean): True if save succeeded, False otherwise;
- **message** (string): Descriptive message including file path or error details.

Behavior:
- Writes recorded waypoints to ``path_saves/<path_name>.txt``;
- Format depends on ``teach_orientation`` setting;
- Overwrites existing file with same name.