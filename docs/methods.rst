Methods
=======

There are two methods to follow the demonstrated path:

- **Dot-to-dot (nodes/repeat_path_coords.py)**: The robot follows a Pure Pursuit-like approach where it intercepts a look-ahead point. Once it reaches this point, a new point further along the path is set as the next target.

- **Bezier curve based (nodes/repeat_bezier_path.py)**: The robot simulates multiple potential paths ahead using Bézier curves and selects the optimal path based on predefined criteria.