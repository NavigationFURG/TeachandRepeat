#!/usr/bin/env python3

import os
import rclpy
import numpy as np

from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point

from rclpy.node import Node
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

from utils import filePathPointsToOrientedPoses

from ament_index_python.packages import get_package_share_directory


class NavigateThroughPoses(Node):
    
    def __init__(self):
        super().__init__('navigate_through_poses')
        
        # Initialize the navigator
        self.navigator = BasicNavigator()
        
        # Declare parameters
        self.declare_parameter('path_file', 'turtle_mod.txt')
        self.declare_parameter('frame_id', 'map')
        
        # Get parameters
        self.frame_id = self.get_parameter('frame_id').get_parameter_value().string_value
        self.path_name = self.get_parameter('path_file').get_parameter_value().string_value
        
        # TODO: Find a better way to get package path # ALSO DONE
        repeat_share = get_package_share_directory('teach_and_repeat')

        self.docks_file = os.path.join(repeat_share, 'path_saves', 'docks.json')
        path_saves_folder = os.path.join(repeat_share, 'path_saves')

        self.bezier_curve_marker_pub = self.create_publisher(Marker, 'teach_and_repeat/repeat/bezier_marker', 10)

        self.path_path = os.path.join(path_saves_folder, self.path_name)

        self.path_poses = filePathPointsToOrientedPoses(self.path_path)
        
        self.get_logger().info(f'NavigateThroughPoses node initialized')
        self.get_logger().info(f'Path file: {self.path_path}')
        
        # Start navigation after a small delay to ensure everything is ready
        self.create_timer(2.0, self.start_navigation)

        # Bezier path marker setup
        self.bezier_curve_marker = Marker()
        self.bezier_curve_marker.header.frame_id = self.frame_id
        self.bezier_curve_marker.lifetime = rclpy.duration.Duration(seconds=3000.0).to_msg() # TODO: Fix it to run while the robot is navigating
        self.bezier_curve_marker.type = Marker.LINE_STRIP
        self.bezier_curve_marker.action = Marker.ADD
        self.bezier_curve_marker.pose.orientation.w = 1.0
        self.bezier_curve_marker.scale.x = 0.01  # Increased line width
        self.bezier_curve_marker.scale.y = 0.1
        self.bezier_curve_marker.color.r = 1.0
        self.bezier_curve_marker.color.g = 0.0
        self.bezier_curve_marker.color.b = 0.0
        self.bezier_curve_marker.color.a = 1.0

        self.visualizePath()

        # Create timer to periodically republish the marker (every 5 seconds)
        self.marker_timer = self.create_timer(5.0, self.visualizePath)

    def visualizePath(self):
        '''
        This function plots the bezier curve.
        '''
        # Clear previous points and set timestamp
        self.bezier_curve_marker.points.clear()
        self.bezier_curve_marker.header.stamp = self.get_clock().now().to_msg()

        for pose_stamped in self.path_poses:
            point = Point()
            point.x = pose_stamped.pose.position.x
            point.y = pose_stamped.pose.position.y
            point.z = pose_stamped.pose.position.z
            self.bezier_curve_marker.points.append(point)

        self.bezier_curve_marker_pub.publish(self.bezier_curve_marker)
        self.get_logger().info(f'Published Bezier path marker with {len(self.bezier_curve_marker.points)} points on topic "teach_and_repeat/repeat/bezier_marker"', once=True)

    def start_navigation(self):
        """Start the navigation process"""
        try:
            # Wait for Nav2 to be active
            self.get_logger().info('Waiting for Nav2 to become active...')
            self.navigator.waitUntilNav2Active()
            self.get_logger().info('Nav2 is active!')
            
            # Check if path file exists
            if not os.path.exists(self.path_path):
                self.get_logger().error(f'Path file not found: {self.path_path}')
                return
            
            if len(self.path_poses) == 0:
                self.get_logger().error('No poses found')
                return
            
            behavior_tree_share = get_package_share_directory('lognav_navigation')
            behavior_tree_file = os.path.join(behavior_tree_share, 'bt', 'navigate_no_replan.xml')

            # Send poses for navigation
            self.navigator.goThroughPoses(self.path_poses,
                                          behavior_tree=behavior_tree_file)
            
            # Monitor navigation progress
            self.monitor_navigation()
            
        except Exception as e:
            self.get_logger().error(f'Error during navigation setup: {str(e)}')
    
    def monitor_navigation(self):
        """Monitor the navigation progress"""
        while not self.navigator.isTaskComplete():
            self.visualizePath()
            feedback = self.navigator.getFeedback()
            if feedback:
                try:
                    eta = feedback.estimated_time_remaining.sec
                    self.get_logger().info(f'ETA: {eta} seconds')
                except AttributeError:
                    self.get_logger().info('Navigation in progress...')
            
            # Sleep briefly to avoid busy waiting
            rclpy.spin_once(self, timeout_sec=1.0)
        
        # Check result
        result = self.navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            self.get_logger().info('Navigation completed successfully!')
        elif result == TaskResult.CANCELED:
            self.get_logger().warn('Navigation was canceled')
        elif result == TaskResult.FAILED:
            self.get_logger().error('Navigation failed')
        else:
            self.get_logger().warn('Navigation completed with unknown status')

def main(args=None):
    rclpy.init(args=args)
    
    try:
        navigate_node = NavigateThroughPoses()
        rclpy.spin(navigate_node)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f'Error: {e}')
    finally:
        if 'navigate_node' in locals():
            navigate_node.navigator.lifecycleShutdown()
            navigate_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()