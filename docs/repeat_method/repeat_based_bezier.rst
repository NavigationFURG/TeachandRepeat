1. Repeat Method Based on Bézier Curve
==========================

The Repeat method is an autonomous path following technique that uses Bézier curve fitting and lookahead path planning to enable a robot to autonomously follow a previously taught path. Unlike simple waypoint following, the Repeat method implements advanced path smoothing through Bézier curve approximation and trajectory optimization through dynamic lookahead path selection. This section provides a detailed technical explanation of how the repeat mechanism works, its core components, parameters, and execution flow.


2. Architecture and Core Components
====================================

The repeat system is implemented through the **RepeatBezierPath** ROS2 node, which operates as an autonomous path follower that:

- Loads a pre-recorded path from a text file (saved by the Teaching method)
- Fits a Bézier curve through the raw waypoints for smooth path approximation
- Generates multiple lookahead paths representing potential future trajectories
- Subscribes to robot pose data from localization (/amcl_pose)
- Evaluates possible steering angles in real-time based on a cost function
- Publishes optimal velocity and steering commands to the robot
- Records actual path traversal for path following error analysis
- Provides real-time visualization of the Bézier curve, lookahead paths, and robot trajectory


3. Main Parameters
==================

The repeat module is controlled by multiple parameters that determine path smoothness, lookahead planning depth, steering constraints, and robot kinematics:

**3.1. Velocity and Motion Parameters**
-----------------------------------------

**tractor_velocity**
  Type: float  
  Default: 0.1 m/s  
  
  The constant linear velocity of the robot while following the path. This value should match the robot's safe operating speed and be appropriate for the environment. The velocity is used to compute wheel speeds through kinematic equations.

**tyre_radius**
  Type: float  
  Default: 0.033 m  
  
  The radius of the robot's wheels in meters. This parameter is used in kinematic calculations to convert steering angles to actual wheel velocities and odometry readings.

**distance_btw_wheels**
  Type: float  
  Default: 0.178 m  
  
  The wheelbase distance (distance between the robot's two drive wheels) in meters. This euclidean distance is critical for:
  - Converting steering angles to differential wheel speeds
  - Computing the Ackermann steering kinematics
  - Mapping desired curvature to achievable steering angles

**3.2. Steering Control Parameters**
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

**3.3. Lookahead Path Generation Parameters**
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

**3.4. Path Fitting Parameters**
--------------------------------

The Bézier curve fitting uses least-squares optimization to compute control points from the raw taught path. This is handled automatically by the **BezierFitDemo** algorithm without explicit parameter tuning. The algorithm:

- Takes the raw path waypoints as input
- Computes optimal Bézier control points using least-squares fitting
- The degree of the Bézier curve is determined by the number of control points needed for good approximation


4. Operating Principles and Path Following
============================================

**4.1. Initialization and Setup**
---------------------------------

Upon node startup, the RepeatBezierPath node performs the following initialization steps:

1. **Path Loading**: Reads the raw taught path file (default: TEST2_PATH.txt) from ``path_saves/`` directory
2. **Bézier Fitting**: Computes Bézier control points from raw waypoints using least-squares fitting
3. **Curve Generation**: Generates a smooth Bézier curve using these control points
4. **Point Resampling**: Resamples the Bézier curve to ensure ``dist_btw_points`` spacing between consecutive points
5. **Lookahead Generation**: Creates 30 different lookahead paths representing potential future trajectories for different steering angles
6. **Data Folder Creation**: Creates a timestamped folder in ``path_saves/`` to store execution data
7. **Marker Setup**: Initializes all visualization markers for RViz
8. **Localization Wait**: Waits for the first odometry message from AMCL before starting path following

**4.2. Tracking Window and Sliding Window Mechanism**
-----------------------------------------------------

The repeat algorithm uses a **sliding window** approach to focus on the immediate future of the path:

- **Window Size**: Defined by ``points_per_paths`` (default: 12 waypoints)
- **Current Window**: Contains waypoints from index ``new_min`` to index ``new_max``
- **Reference Points**: These window waypoints serve as the target for lookahead path optimization
- **Advancement**: When the robot comes within ``threshold_dist`` of the first point in the window, both ``new_min`` and ``new_max`` are incremented, advancing the window to the next set of waypoints

This mechanism provides:
- Computational efficiency by only considering nearby future waypoints
- Local path optimization (not forced to match distant waypoints)
- Natural completion detection (when all waypoints are consumed)

**4.3. Real-Time Path Following Cycle**
----------------------------------------

Once path following begins, the node executes this cycle at every odometry update (~10 Hz from AMCL):

1. **Pose Reception**: Receives current robot position (x, y) and orientation (yaw) from /amcl_pose
2. **Local Frame Transformation**: Transforms all lookahead paths from global to local robot frame
3. **Cost Evaluation**: For each of the 30 steering angles:
   - Transforms the simulated future trajectory to global frame
   - Compares it against the reference Bézier curve points in the current window
   - Calculates a cost metric (error between lookahead path and reference curve)
4. **Optimal Steering Selection**: Selects the steering angle with minimum cost
5. **Velocity Computation**: Calculates individual wheel velocities from the desired steering angle using Ackermann steering kinematics
6. **Command Publication**: Publishes velocity commands to the robot
7. **Window Advancement**: If robot is within threshold distance of the next waypoint, advances the tracking window
8. **Completion Check**: If no waypoints remain, stops the robot and saves results

**4.4. Steering Angle to Wheel Velocity Conversion**
-----------------------------------------------------

The node converts desired steering angles to differential wheel velocities using:

$$\text{left\_wheel\_speed} = \text{tractor\_velocity} - \text{steering\_angle} \times \frac{\text{distance\_btw\_wheels}}{2}$$

$$\text{right\_wheel\_speed} = \text{tractor\_velocity} + \text{steering\_angle} \times \frac{\text{distance\_btw\_wheels}}{2}$$

These wheel speeds are then converted to linear and angular velocity commands:

$$v_{linear} = \frac{\text{left\_wheel\_speed} + \text{right\_wheel\_speed}}{2}$$

$$v_{angular} = \frac{\text{right\_wheel\_speed} - \text{left\_wheel\_speed}}{\text{distance\_btw\_wheels}}$$


5. Bézier Curve Generation and Fitting
=======================================

**5.1. Why Bézier Curves**
---------------------------

The repeat method uses Bézier curves instead of raw waypoint following for several reasons:

- **Smoothness**: Creates a smooth, continuous path rather than discrete waypoints
- **Path Reduction**: A Bézier curve can approximate many raw points with fewer control points
- **Noise Filtering**: Inherently smooths out small errors or noise in the taught path
- **Differentiability**: Enables computation of path curvature and derivatives
- **Optimized Following**: Provides better reference trajectories for lookahead planning

**5.2. Bézier Curve Fitting Process**
--------------------------------------

The fitting process uses the **BezierFitDemo** algorithm:

1. **Input**: Raw waypoints from taught path (typically 50-200+ points depending on path length)
2. **Algorithm**: Least-squares Bézier fitting determines optimal control point positions
3. **Control Point Computation**: The algorithm minimizes the error between the raw points and the fitted curve
4. **Output**: A Bézier curve defined by its control points that approximates the taught path

The degree of the Bézier curve (number of control points - 1) is chosen to balance:
- Fidelity to the original path
- Computational efficiency
- Numerical stability

**5.3. Curve Generation and Storage**
-------------------------------------

After fitting:

1. **Bézier Curve Generation**: The curve is evaluated at many parameter values (t from 0 to 1) to generate a dense set of waypoints
2. **Point Resampling**: The generated curve is resampled to guarantee ``dist_btw_points`` spacing
3. **Storage**: The resampled Bézier curve points are saved to ``bezier_path_coords_data.txt`` in the execution folder
4. **Variable Assignment**: These resampled points become the reference trajectory (``bezier_path_coords``)

**5.4. Bézier Curve Output File Format**
-----------------------------------------

The Bézier curve is stored as comma-separated x,y coordinates:

::

    1.234,5.678
    1.254,5.698
    1.274,5.718
    1.294,5.738
    ...

Each line represents a waypoint on the smoothed Bézier curve, uniformly spaced at ``dist_btw_points`` distance apart.


6. Lookahead Path Generation
=============================

**6.1. Concept of Lookahead Paths**
-----------------------------------

Lookahead paths are simulated future trajectories of the robot corresponding to each possible steering angle. They represent "what would the robot's path look like if I applied steering angle θ?" This enables the algorithm to:

- Predict future motion before committing to a steering command
- Evaluate multiple steering options simultaneously
- Select the steering that best aligns with the desired Bézier curve

**6.2. Lookahead Path Generation Process**
-------------------------------------------

For each of the ``lookahead_total_paths`` steering angles:

1. **Initial Setup**: Start with robot at origin in local frame reference
2. **Trajectory Simulation**: Simulate robot motion using kinematic equations:
   - Assume constant velocity (``tractor_velocity``)
   - Apply the given steering angle
   - Compute the curvature of motion: $\kappa = \frac{\tan(\text{steering})}{\text{wheelbase}}$
3. **Point Generation**: Generate ``points_per_paths`` future waypoints along this simulated trajectory
4. **Point Spacing**: Ensure points are spaced at ``dist_btw_points`` distance
5. **Storage**: Store in dictionary with steering angle as key

**6.3. Steering Angle Distribution**
-------------------------------------

The ``lookahead_total_paths`` steering angles are distributed uniformly between ``min_steering`` and ``max_steering``:

$$\text{angle\_i} = \text{min\_steering} + \frac{i}{\text{lookahead\_total\_paths} - 1} \times (\text{max\_steering} - \text{min\_steering})$$

For default parameters with 30 paths, ``min_steering=-0.5``, ``max_steering=0.5``:
- Steering angles range from -0.5 to +0.5 radians
- Resolution: approximately 0.0345 radians (≈2 degrees) between paths


7. Path Following Mechanism
=============================

**7.1. Cost Function and Path Comparison**
-------------------------------------------

At each cycle, the algorithm compares each lookahead path against the reference Bézier curve segment using the **compare_bezier_lookahead** function. This function calculates a cost metric representing the alignment error:

$$\text{cost} = \sum_{i=0}^{n} \text{distance}(\text{lookahead\_point}_i, \text{reference\_point}_i)$$

This measures how well the simulated future trajectory aligns with the desired path. Lower cost indicates better alignment.

**7.2. Steering Angle Selection**
---------------------------------

From all ``lookahead_total_paths`` evaluated steering angles:

1. **Cost Calculation**: Compute cost for each steering angle
2. **Minimum Selection**: Select the steering angle with minimum cost
3. **Storage**: Store as ``desired_steering_angle``
4. **Path Storage**: Store corresponding lookahead path as ``best_lookahead_path``

This greedy approach ensures the robot follows the steering that best matches the reference path at each moment.

**7.3. Coordinate Frame Transformations**
------------------------------------------

The algorithm uses two coordinate frames:

- **Global Frame** (map): Where the taught path and all reference waypoints exist
- **Local Robot Frame**: Where lookahead paths are initially generated (robot at origin)

Transformation from local to global:

$$x_{global} = x_{robot} + d \times \cos(\text{angle} + \theta_{robot})$$

$$y_{global} = y_{robot} + d \times \sin(\text{angle} + \theta_{robot})$$

where:
- $(x_{robot}, y_{robot})$ = current robot position
- $d$ = distance from robot to point
- angle = angle to point in local frame
- $\theta_{robot}$ = current robot heading


8. Real-Time Visualization in RViz
===================================

**8.1. Published Markers**
--------------------------

During path following, the RepeatBezierPath node publishes multiple visualization markers:

- **Raw Points Marker** (GREEN POINTS): published to ``/raw_points``
  - Type: POINTS
  - Color: Green (r=0.0, g=1.0, b=0.0)
  - Size: 0.07 meters
  - Shows the original taught path waypoints

- **Bézier Curve Marker** (RED LINE): published to ``/bezier_curve_marker``
  - Type: LINE_STRIP
  - Color: Red (r=1.0, g=0.0, b=0.0)
  - Width: 0.01 meters
  - Shows the smooth Bézier curve fitted through the raw points

- **Bézier Points Marker** (YELLOW POINTS): published to ``/bezier_points_marker``
  - Type: POINTS
  - Color: Yellow (r=1.0, g=1.0, b=0.0)
  - Size: 0.05 meters
  - Shows the current ``points_per_paths`` window points on the reference curve

- **Lookahead Paths Marker** (BLUE POINTS): published to ``/lookahead_paths_marker``
  - Type: POINTS
  - Color: Blue (r=0.0, g=0.0, b=1.0)
  - Size: 0.05 meters
  - Shows all evaluated lookahead trajectories for all steering angles

- **Selected Lookahead Path Marker** (YELLOW LINE): published to ``/selected_lookahead_path_marker``
  - Type: LINE_STRIP
  - Color: Yellow (r=1.0, g=1.0, b=0.0)
  - Width: 0.01 meters
  - Highlights the optimal lookahead path for the current steering selection


8.2. Visualization Workflow**
-----------------------------

During each update cycle:

1. Raw taught path points are published
2. All evaluated lookahead paths are published (showing the fan of possibilities)
3. The current reference window (12 points ahead) is published
4. The best matching lookahead path is highlighted
5. Markers are published to ``/teach_and_repeat/teach/dock_markers`` namespace

This real-time visualization enables monitoring of:
- Path fitting quality (red Bézier vs green raw points)
- Algorithm performance (cost function selection among blue lookahead paths)
- Robot progress (yellow highlighted optimal path)


9. Execution Data and Output Files
===================================

**9.1. Output Folder Structure**
--------------------------------

When the node starts, it creates a timestamped folder with the format: ``YYYY-MM-DD_HH-MM-SS/``

Inside this folder, the following files are created:

**9.2. File Outputs**
---------------------

**TEST2_PATH.txt**
  - Copy of the original taught path file
  - Format: x,y coordinates, one per line
  - Purpose: Reference for comparing followed path

**bezier_path_coords_data.txt**
  - The smooth Bézier curve waypoints
  - Format: x,y coordinates at ``dist_btw_points`` spacing
  - Purpose: Reference trajectory used for lookahead planning

**following_data.txt**
  - Actual positions visited by the robot during path following
  - Format: x,y coordinates from odometry/localization
  - Purpose: Comparing actual path vs intended path

**variables.txt**
  - Key execution parameters and performance metrics
  - Stored as key-value pairs
  - Content includes:
    - Robot kinematic parameters (tyre_radius, distance_btw_wheels)
    - Control parameters (tractor_velocity, threshold_dist)
    - Lookahead parameters (points_per_paths, lookahead_total_paths)
    - Performance metrics:
      - **duration_time**: Total execution time in minutes
      - **erro_percentual**: Error % between original taught path and actual followed path
      - **erro_percentual_bezier**: Error % between Bézier curve and actual followed path

**9.3. Error Metrics Calculation**
----------------------------------

Two error metrics are calculated:

- **erro_percentual**: Compares actual path with the original raw taught path using the ``calculate_erro()`` function
- **erro_percentual_bezier**: Compares actual path with the smoothed Bézier curve approximation

These metrics quantify path following accuracy:
- 0% = perfect path following
- Higher % = greater deviation from intended path

The Bézier error is often lower because the curve is smoother and represents what the algorithm was actually trying to follow.

**9.4. Variables File Format**
------------------------------

The variables.txt file contains key-value pairs in text format:

::

    tyre_radius: 0.033
    max_steering: 0.5
    min_steering: -0.5
    tractor_velocity: 0.1
    points_per_paths: 12
    dist_btw_points: 0.2
    lookahead_total_paths: 30
    threshold_dist: 0.8
    sim_steps: 100
    dt: 0.01
    duration_time: 2.5
    erro_percentual: 5.3
    erro_percentual_bezier: 3.1


10. Practical Workflow
======================

A typical repeat execution follows this workflow:

1. **Path Teaching**: Use the Teach module to record a path and save it to ``path_saves/TEST2_PATH.txt``
2. **Launch Repeat Node**: Start the RepeatBezierPath node
3. **Wait for Initialization**: The node loads the path, fits Bézier curve, generates lookahead paths
4. **Initialize Localization**: Run AMCL and ensure the robot is in the correct global position
5. **Monitor RViz**:
   - Green line: original taught path
   - Red line: smooth Bézier approximation
   - Blue points: lookahead path options
   - Yellow line: selected optimal path
6. **Autonomous Following**: The robot moves autonomously following the path
7. **Real-Time Feedback**: Check terminal output for obstacle detection and path completion
8. **Check Results**: When complete, examine the timestamped folder for:
   - error metrics
   - execution time
   - actual vs intended trajectory comparison

The repeat module enables robust autonomous path following based on the geometry of the taught path, with optimization at every step to select the best steering angle.
