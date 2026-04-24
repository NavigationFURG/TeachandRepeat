FBOT Teach and Repeat Framework
====================================

.. youtube:: 0qg6E9y5eEw


FBOT Teach and Repeat (T&R) is a framework for mobile robots that allows them to autonomously follow previously demonstrated paths. It consists of two main modules: the **Teach** module, which records the robot's movements during a demonstration, and the **Repeat** module, which enables the robot to follow the recorded path autonomously. Developed by the FBOT team, it works out-of-the-box for differential drive robots and can be adapted to other types of robots with simple modifications. To see the system in action, check out the :ref:`videos` section.

The Repeat module can be configured to use different approaches for path following, such as a custom path follower based on a Dynamic Window Approach (DWA), using Bézier curves for path generation and smoothing, or a waypoint following method using local and global planners provided by `Navigation Stack 2 (Nav2). <https://docs.nav2.org/index.html/>`_

If it is your first time using the package, it is recommended to follow the :ref:`getting_started` guide to learn the basics of the system. It will walk you through the process of setting up the package, teaching a path, and then following it using the Repeat module, both with the Bézier curve approach and with the waypoint following method, which integrates with Nav2.

Also, if you are interested in the technical details of the implementation, you can explore the :ref:`teaching_method` and :ref:`repeating_method` sections, which provide in-depth explanations of the algorithms and techniques used in both modules.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   tutorial/index
   videos/index
   teaching_method/index
   repeat_method/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
