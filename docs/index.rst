Teach and Repeat using Bézier Curves
====================================

.. youtube:: crmZR9EUTow


Teach and Repeat (T&R) is a navigation system for mobile robots that allows them to autonomously follow previously demonstrated paths. Consisting of two main modules, the **Teach** module records the robot's movements during a demonstration, while the **Repeat** module enables the robot to autonomously follow the recorded path. It works out-of-the-box for differential drive robots, and can be adapted to other types of robots with simple modifications.

The repeat module can be configured to use different approaches for path following, such as a home-made Dynamic Window Approach (DWA) that utilizes Bézier curves for path generation and smoothing, or local and global planners defined by `Navigation Stack 2 (Nav2). <https://docs.nav2.org/index.html/>`_

If it is your first time using the package, it is recommended to follow the :ref:`getting_started` guide to learn the basics of the system.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   tutorial/index
   teaching_method/index
   repeat_method/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
