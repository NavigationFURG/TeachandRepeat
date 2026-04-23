
1. Repeat Method Based on Bézier Curves
=========================================

Overview
========

The Repeat method based on Bézier curves enables a robot to autonomously follow a previously taught path using Bézier curve fitting and a DWA-based lookahead path planning. The **RepeatBezierPath** ROS2 node loads a pre-recorded path, fits a Bézier curve through the waypoints to create a smooth trajectory, generates multiple lookahead trajectories for different steering angles, and selects the optimal steering command in real-time by comparing each simulated path against the reference curve. This approach smooths discrete waypoints into a continuous curve and optimizes trajectory selection at every step.

Originally, this method was suited for Ackermann robots, but also works in differential robots such as the ones we made experiments with. It is a home-made repeating algorithm, it probably has bugs and so we invite *YOU* to help us improve it! For industry-level operations, we recommend using the repeat method based on Waypoint following, which is developed with Navigation Stack 2 features, which are way more stable and less prone to failures.

Architecture and Core Components
=============================

The repeat system is implemented through the **RepeatBezierPath** ROS2 node, which operates as an autonomous path follower that:

- Loads a pre-recorded path from a text file (saved by the Teaching method);
- Fits a Bézier curve through the raw waypoints for smooth path approximation;
- Generates multiple lookahead paths representing potential future trajectories;
- Subscribes to robot pose data from localization (/amcl_pose);
- Evaluates possible steering angles in real-time based on a cost function;
- Publishes optimal velocity and steering commands to the robot;
- Records actual path traversal for path following error analysis;
- Provides real-time visualization of the Bézier curve, lookahead paths, and robot trajectory.


Parameters
==========

This repeat module is controlled by multiple parameters that determine path smoothness, lookahead planning depth, steering constraints, and robot kinematics. Here, we will try to make them as simple as possible to understand:

.. important::
    These parameters must be modified in the source code of repeat_bezier_path.py!

    We also have a default setup for both turtlebot and the logistics robot from the experiments and videos. They are both available at the github source code, in different branches (feat/turtlebot) and (feat/green).


**Velocity and Motion Parameters**
-----------------------------------------

**tractor_velocity**
  Type: float  
  Default: 0.1 m/s  
  
  The constant linear velocity of the robot while following the path. This value should match the robot's common operating speed. The velocity is used to compute wheel speeds through kinematic equations.

**tyre_radius**
  Type: float  
  Default: 0.033 m  
  
  The radius of the robot's wheels in meters. This parameter is used in kinematic calculations to convert steering angles to actual wheel velocities and odometry readings.

**distance_btw_wheels**
  Type: float  
  Default: 0.178 m  
  
  The wheelbase distance (distance between the robot's two drive wheels) in meters. This euclidean distance is critical for:
  - Converting steering angles to differential wheel speeds;
  - Computing steering kinematics;
  - Mapping desired curvature to achievable steering angles.

**Steering Control Parameters**
-------------------------------------

**max_steering**
  Type: float  
  Default: 0.5  
  
  Maximum steering angle magnitude (in radians) that the robot can achieve. This limits the curvature of paths the robot can follow and prevents unrealistic steering commands.

**min_steering**
  Type: float  
  Default: -0.5  
  
  Minimum steering angle magnitude (in radians). Combined with max_steering, defines the steering angle range for lookahead path generation.

**threshold_dist**
  Type: float  
  Default: 0.8 m  
  
  The distance threshold between the robot and the next target point on the Bézier curve. When the robot moves within this distance of the current target point, the algorithm advances to the next point in the path, effectively creating a "sliding window" on the curve.

**Lookahead Path Generation Parameters**
----------------------------------------------

**points_per_paths**
  Type: integer  
  Default: 12  
  
  The number of future waypoints used in lookahead path evaluation. Each lookahead path contains this many points. A larger value provides better trajectory planning but increases computational load.

**dist_btw_points**
  Type: float  
  Default: 0.2 m  
  
  The desired spacing between consecutive waypoints on the Bézier curve. The raw Bézier curve is resampled to ensure uniform point spacing, improving path following stability and making cost calculations more meaningful. Points are generated at this distance apart.

**lookahead_total_paths**
  Type: integer  
  Default: 30  
  
  The total number of different steering angles evaluated for lookahead path planning. These angles are equally distributed between min_steering and max_steering. Higher values enable finer steering angle resolution but increase computational cost.

**Path Fitting Parameters**
--------------------------------

The Bézier curve fitting uses least-squares optimization to compute control points from the raw taught path. This is handled automatically by the **BezierFitDemo** algorithm without explicit parameter tuning. The algorithm:

- Takes the raw path waypoints as input;
- Computes optimal Bézier control points using least-squares fitting;
- The degree of the Bézier curve is determined by the number of control points needed for good approximation.


Operating Principles and Path Following
========================================

**Initialization and Setup**
---------------------------------

Upon node startup, the RepeatBezierPath node performs the following initialization steps:

1. **Path Loading**: Reads the raw taught path file (default: TEST2_PATH.txt) from ``path_saves/`` directory;
2. **Bézier Fitting**: Computes Bézier control points from raw waypoints using least-squares fitting;
3. **Curve Generation**: Generates a smooth Bézier curve using these control points;
4. **Point Resampling**: Resamples the Bézier curve to ensure ``dist_btw_points`` spacing between consecutive points;
5. **Lookahead Generation**: Creates lookahead paths representing potential future trajectories for different steering angles;
6. **Data Folder Creation**: Creates a timestamped folder in ``path_saves/`` to store execution data;
7. **Marker Setup**: Initializes all visualization markers for RViz;
8. **Localization Wait**: Waits for the first odometry message from AMCL before starting path following.

**Tracking Window and Sliding Window Mechanism**
-----------------------------------------------------

The repeat algorithm uses a **sliding window** approach to focus on the immediate future of the path:

- **Window Size**: Defined by ``points_per_paths`` (default: 12 waypoints);
- **Current Window**: Contains waypoints from index ``new_min`` to index ``new_max``;
- **Reference Points**: These window waypoints serve as the target for lookahead path optimization;
- **Advancement**: When the robot comes within ``threshold_dist`` of the first point in the window, both ``new_min`` and ``new_max`` are incremented, advancing the window to the next set of waypoints.

This mechanism provides computational efficiency and ensure a smoother local path following.

**Real-Time Path Following Cycle**
----------------------------------------

Once path following begins, the node executes this cycle at every odometry update (~10 Hz from AMCL):

1. **Pose Reception**: Receives current robot position (x, y) and orientation (yaw) from /amcl_pose;
2. **Local Frame Transformation**: Transforms all lookahead paths from global to local robot frame;
3. **Cost Evaluation**: For each of the steering angles:
   - Transforms the simulated future trajectory to global frame;
   - Compares it against the reference Bézier curve points in the current window;
   - Calculates a cost metric (error between lookahead path and reference curve).
4. **Optimal Steering Selection**: Selects the steering angle with minimum cost;
5. **Velocity Computation**: Calculates individual wheel velocities from the desired steering angle using, as of now, Ackermann steering kinematics;
6. **Command Publication**: Publishes velocity commands to the robot;
7. **Window Advancement**: If robot is within threshold distance of the next waypoint, advances the tracking window;
8. **Completion Check**: If no waypoints remain, stops the robot and saves results.

**Steering Angle to Wheel Velocity Conversion**
-----------------------------------------------------

The node converts desired steering angles to differential wheel velocities using:

.. math::

    \text{left\_wheel\_speed} = \text{tractor\_velocity} - \text{steering\_angle} \times \frac{\text{distance\_btw\_wheels}}{2}

.. math::

    \text{right\_wheel\_speed} = \text{tractor\_velocity} + \text{steering\_angle} \times \frac{\text{distance\_btw\_wheels}}{2}

These wheel speeds are then converted to linear and angular velocity commands:

.. math::

    v_{linear} = \frac{\text{left\_wheel\_speed} + \text{right\_wheel\_speed}}{2}

.. math::

    v_{angular} = \frac{\text{right\_wheel\_speed} - \text{left\_wheel\_speed}}{\text{distance\_btw\_wheels}}


Bézier Curve Generation and Fitting
====================================

**Why Bézier Curves**
---------------------------

The repeat method uses Bézier curves instead of raw waypoint following for several reasons:

- **Smoothness**: Creates a smooth, continuous path rather than discrete waypoints;
- **Path Reduction**: A Bézier curve can approximate many raw points with fewer control points;
- **Noise Filtering**: Inherently smooths out small errors or noise in the taught path;
- **Differentiability**: Enables computation of path curvature and derivatives;

**Bézier Curve Fitting Process**
--------------------------------------

The fitting process uses the **BezierFitDemo** algorithm:

1. **Input**: Raw waypoints from taught path;
2. **Algorithm**: Least-squares Bézier fitting determines optimal control point positions;
3. **Control Point Computation**: The algorithm minimizes the error between the raw points and the fitted curve;
4. **Output**: A Bézier curve defined by its control points that approximates the taught path.


**Curve Generation and Storage**
-------------------------------------

After fitting:

1. **Bézier Curve Generation**: The curve is evaluated at many parameter values (t from 0 to 1) to generate a dense set of waypoints;
2. **Point Resampling**: The generated curve is resampled to guarantee ``dist_btw_points`` spacing;
3. **Storage**: The resampled Bézier curve points are saved to ``bezier_path_coords_data.txt`` in the execution folder;
4. **Variable Assignment**: These resampled points become the reference trajectory (``bezier_path_coords``).


Lookahead Path Generation
==========================

**Concept of Lookahead Paths**
-----------------------------------

Lookahead paths are simulated future trajectories of the robot corresponding to each possible steering angle. They represent "what would the robot's path look like if I applied steering angle θ?". It is very much based on a DWA local planner and enables the algorithm to:

- Predict future motion before committing to a steering command;
- Evaluate multiple steering options simultaneously;
- Select the steering that best aligns with the desired Bézier curve.

**Lookahead Path Generation Process**
-------------------------------------------

For each of the ``lookahead_total_paths`` steering angles:

1. **Initial Setup**: Start with robot at origin in local frame reference;
2. **Trajectory Simulation**: Simulate robot motion using kinematic equations:
   - Assume constant velocity (``tractor_velocity``);
   - Apply the given steering angle;
   - Compute the curvature of motion: :math:`\kappa = \frac{\tan(\text{steering})}{\text{wheelbase}}`
3. **Point Generation**: Generate ``points_per_paths`` future waypoints along this simulated trajectory;
4. **Point Spacing**: Ensure points are spaced at ``dist_btw_points`` distance;
5. **Storage**: Store in dictionary with steering angle as key.


Path Following Mechanism
=========================

**Cost Function and Path Comparison**
-------------------------------------------

At each cycle, the algorithm compares each lookahead path against the reference Bézier curve segment using the **compare_bezier_lookahead** function. This function calculates a cost metric representing the alignment error:

.. math::

    \text{cost} = \sum_{i=0}^{n} \text{distance}(\text{lookahead\_point}_i, \text{reference\_point}_i)

This measures how well the simulated future trajectory aligns with the desired path.

**Steering Angle Selection**
---------------------------------

From all ``lookahead_total_paths`` evaluated steering angles:

1. **Cost Calculation**: Compute cost for each steering angle;
2. **Minimum Selection**: Select the steering angle with minimum cost;
3. **Storage**: Store as ``desired_steering_angle``;
4. **Path Storage**: Store corresponding lookahead path as ``best_lookahead_path``.

This greedy approach ensures the robot follows the steering that best matches the reference path at each moment.


Real-Time Visualization in RViz
================================

**Published Markers**
--------------------------

During path following, the RepeatBezierPath node publishes multiple visualization markers:

- **Raw Points Marker** (GREEN POINTS): published to ``/raw_points``
  - Shows the original taught path waypoints

- **Bézier Curve Marker** (RED LINE): published to ``/bezier_curve_marker``
  - Shows the smooth Bézier curve fitted through the raw points

- **Bézier Points Marker** (YELLOW POINTS): published to ``/bezier_points_marker``
  - Shows the current ``points_per_paths`` window points on the reference curve

- **Lookahead Paths Marker** (BLUE POINTS): published to ``/lookahead_paths_marker``
  - Shows all evaluated lookahead trajectories for all steering angles

- **Selected Lookahead Path Marker** (YELLOW LINE): published to ``/selected_lookahead_path_marker``
  - Highlights the optimal lookahead path for the current steering selection


Visualization Workflow**
-----------------------------

During each update cycle:

1. Raw taught path points are published;
2. All evaluated lookahead paths are published (showing the fan of possibilities);
3. The current reference window is published;
4. The best matching lookahead path is highlighted;
5. Markers are published to ``/teach_and_repeat/teach/dock_markers`` namespace.

This real-time visualization enables monitoring of:
- Path fitting quality (red Bézier vs green raw points);
- Algorithm performance (cost function selection among blue lookahead paths);
- Robot progress (yellow highlighted optimal path).


Execution Data and Output Files
===============================

**Output Folder Structure**
--------------------------------

When the node starts, it creates a timestamped folder in path_saves/ with the format: ``YYYY-MM-DD_HH-MM-SS/``.

Inside this folder, the following files are created:

**File Outputs**
---------------------

**your_file.txt**
  - Copy of the original taught path file;
  - Format: x,y coordinates, one per line;
  - Purpose: Reference for comparing followed path.

**bezier_path_coords_data.txt**
  - The smooth Bézier curve waypoints;
  - Format: x,y coordinates at ``dist_btw_points`` spacing;
  - Purpose: Reference trajectory used for lookahead planning.

**following_data.txt**
  - Actual positions visited by the robot during path following;
  - Format: x,y coordinates from odometry/localization;
  - Purpose: Comparing actual path vs intended path.

**variables.txt**
  - Key execution parameters and performance metrics;
  - Stored as key-value pairs.
  - Content includes:
    - Robot kinematic parameters (tyre_radius, distance_btw_wheels);
    - Control parameters (tractor_velocity, threshold_dist);
    - Lookahead parameters (points_per_paths, lookahead_total_paths).
    - Performance metrics:
      - **duration_time**: Total execution time in minutes;
      - **erro_percentual**: Error % between original taught path and actual followed path using the ``calculate_erro()`` function;
      - **erro_percentual_bezier**: Error % between Bézier curve and actual followed path.


