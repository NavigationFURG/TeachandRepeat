# FBOT Teach and Repeat Framework
FBOT Teach and Repeat (T&R) is a framework for mobile robots that allows them to autonomously follow previously demonstrated paths. It consists of two main modules: the Teach module, which records the robot’s movements during a demonstration, and the Repeat module, which enables the robot to follow the recorded path autonomously. Developed by the FBOT team, it works out-of-the-box for differential drive robots and can be adapted to other types of robots with simple modifications.

The Repeat module can be configured to use different approaches for path following, such as a custom path follower based on a Dynamic Window Approach (DWA), using [Bézier curves for path generation and smoothing](https://ieeexplore.ieee.org/document/10837801), or a waypoint following method using local and global planners provided by [Navigation Stack 2 (Nav2)](https://docs.nav2.org/).

Read the official documentation, including a step-by-step tutorial and example videos, [here!](https://teachandrepeat.readthedocs.io/en/latest/)

