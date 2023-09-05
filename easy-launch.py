#!/usr/bin/env python3

import elsie
from elsie.ext import unordered_list

slides = elsie.SlideDeck(width=1920, height=1080)

slides.update_style(
    "default", elsie.TextStyle(font="Lato", align="left", size=48, color="white")
)
slides.update_style("code", elsie.TextStyle(size=36))

title = slides.get_style("default")
title.size = 60
title.bold = True
title.color = "white"
slides.set_style("title", title)

subtitle = slides.get_style("title")
subtitle.size = 36
subtitle.italic = True
subtitle.color = "white"
slides.set_style("subtitle", subtitle)

header = slides.get_style("default")
header.bold = True
slides.set_style("header", header)

bold_text = slides.get_style("default")
bold_text.bold = True
slides.set_style("bold", bold_text)

black_text = slides.get_style("default")
black_text.color = "black"
slides.set_style("black", black_text)

slides.set_style("link", elsie.TextStyle(color="blue"))


@slides.slide()
def title(slide):
    slide.box().image("layout_images/title_slide_bg.png")
    slide = slide.overlay(width="40%", p_left=100, p_top=500)
    slide.box(width="fill").text("Retro ROS 2 Launch", style="title")
    slide.box(width="fill").text("Remember XML files?", style="subtitle")
    slide.box(width="fill", p_top=10).text("September 5, 2023")
    slide.box(width="fill", p_top=180).text("Tyler Weaver", style="bold")
    slide.box(width="fill").text("Staff Software Engineer\ntyler@picknik.ai")


@slides.slide()
def author(slide):
    bg = slide.box().image("layout_images/layout_3_bg.png")
    slide = slide.overlay()
    header = slide.box(width="fill", height="20%", p_left=120).text(
        "Tyler Weaver", style="header"
    )
    content = slide.fbox(horizontal=True)
    text_area = content.box(width="50%", p_left=120)
    text_area.update_style("default", elsie.TextStyle(color="black"))
    image_area = content.box(width="fill").image("images/kart.jpg")
    lst = unordered_list(text_area)
    lst.item().text("Racing Kart Driver")
    lst.item().text("MoveIt Maintainer")
    lst.item().text("Rust Evangelist")
    lst.item().text("Docker Skeptic")


@slides.slide(debug_boxes=False)
def comfort_zone(slide):
    bg = slide.box().image("layout_images/layout_3_bg.png")
    slide = slide.overlay()
    header = slide.box(width="fill", height="20%", p_left=120).text(
        "Comfort Zone: ROS 1 Launch", style="header"
    )
    content = slide.fbox(width="fill", p_left=120, p_top=60).code(
        "xml",
        """
<launch>
  <arg name="pipeline" default="ompl" />
  <arg name="capabilities" default=""/>

  <node name="move_group" pkg="moveit_ros_move_group" type="move_group"
    output="screen">
    <param name="default_planning_pipeline" value="$(arg pipeline)" />
    <param name="capabilities" value="$(arg capabilities)" />
  </node>
</launch>
  """,
    )


@slides.slide()
def trigger(slide):
    bg = slide.box().image("layout_images/layout_8_bg.png")
    slide = slide.overlay()
    slide.update_style("code", elsie.TextStyle(size=16))
    slide.update_style("header", elsie.TextStyle(color="black"))
    header = slide.box(width="fill", height="20%", p_left=120).text(
        "Trigger: ROS 2 Launch", style="header"
    )
    content = slide.fbox(horizontal=True)
    content.box(width="50%", height="fill", p_left=120).code(
        "python",
        """
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.conditions import IfCondition, UnlessCondition
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument("rviz_config",
            default_value="kinova_moveit_config_demo.rviz",
            description="RViz configuration file",
        )
    )
    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])


def launch_setup(context, *args, **kwargs):
    launch_arguments = {
        "robot_ip": "xxx.yyy.zzz.www",
        "use_fake_hardware": "true",
        "gripper": "robotiq_2f_85",
        "dof": "7",
    }

    moveit_config = (
        MoveItConfigsBuilder("gen3", package_name="kinova_gen3_7dof_robotiq_2f_85_moveit_config")
        .robot_description(mappings=launch_arguments)
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .planning_scene_monitor(publish_robot_description=True, publish_robot_description_semantic=True)
        .planning_pipelines(pipelines=["ompl", "stomp", "pilz_industrial_motion_planner"])
        .to_moveit_configs()
    )
  """,
    )
    content.box(width="50%").code(
        "python",
        """
    # Start the actual move_group node/action server
    run_move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[moveit_config.to_dict()],
    )

    rviz_base = LaunchConfiguration("rviz_config")
    rviz_config = PathJoinSubstitution([FindPackageShare("moveit2_tutorials"), "launch", rviz_base])

    # RViz
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.planning_pipelines,
            moveit_config.joint_limits,
        ],
    )

    # Static TF
    static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="static_transform_publisher",
        output="log",
        arguments=["--frame-id", "world", "--child-frame-id", "base_link"],
    )

    # Publish TF
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="both",
        parameters=[moveit_config.robot_description],
    )

    nodes_to_start = [
        rviz_node,
        static_tf,
        robot_state_publisher,
        run_move_group_node
    ]

    return nodes_to_start
  """,
    )


@slides.slide(debug_boxes=False)
def initial_success(slide):
    content = slide.box(width="fill", p_left=30, p_top=60).code(
        "xml",
        """
<launch>
  <arg name="robot_ip" default="xxx.yyy.zzz.www" />
  <arg name="use_fake_hardware" default="true" />
  <arg name="gripper" default="robotiq_2f_85" />
  <arg name="dof" default="7" />

  <let name="robot_description"
    value="$(command 'xacro $(find-pkg-share kortex_description)/robots/gen3.xacro
      robot_ip:=$(var robot_ip) use_fake_hardware:=$(var use_fake_hardware)
      gripper:=$(var gripper) dof:=$(var dof)')" />
  <let name="robot_description_semantic"
    value="$(command 'xacro $(find-pkg-share kinova_moveit_config)/config/gen3.srdf')"
  />

  <!-- MoveGroup -->
  <node pkg="moveit_ros_move_group" exec="move_group" output="screen">
    <param name="robot_description" value="$(var robot_description)" />
    <param name="robot_description_semantic" value="$(var robot_description_semantic)" />
    <param from="$(find-pkg-share cpp_parameters)/config/moveit.yaml" />
  </node>
</launch>
  """,
    )


@slides.slide(debug_boxes=False)
def crisis(slide):
    bg = slide.box().image("layout_images/layout_3_bg.png")
    slide = slide.overlay()
    header = slide.box(width="fill", height="20%", p_left=120).text(
        "Crisis: YAML parsing of params", style="header"
    )
    content = slide.fbox(width="fill", p_left=120, p_top=60)
    content.box(width="fill").code(
        "xml",
        """
<let name="robot_description_semantic"
    value="$(command 'xacro $(find-pkg-share kinova_moveit_config)/config/gen3.srdf')"
  />
...
<param name="robot_description_semantic" value="$(var robot_description_semantic)" />
  """,
    )
    content.box(width="fill").rect(bg_color="black").text(
        """' using yaml rules: yaml.safe_load() failed
mapping values are not allowed here
  in "<unicode string>", line 11, column 13:
      <!--GROUPS: Representation of a set of joi ...
                ^
""",
        style="tt",
    )
    text_box = content.box(width="fill")
    text_box.update_style("default", elsie.TextStyle(color="black"))
    text_box.update_style("tt", elsie.TextStyle(color="green"))
    lst = unordered_list(text_box)
    lst.item().text(
        "SRDF parameter loaded into variable ~tt{robot_description_semantic}"
    )
    lst.item().text("value attribute is parsed as yaml")
    lst.item().text("yaml parser fails when it finds ~tt{:} character")
    lst.item().text(
        "Open issue on ros2/launch: ~link{https://github.com/ros2/launch/issues/729}"
    )


@slides.slide(debug_boxes=False)
def recovery(slide):
    bg = slide.box().image("layout_images/layout_3_bg.png")
    slide = slide.overlay()
    header = slide.box(width="fill", height="20%", p_left=120).text(
        "Recovery?", style="header"
    )
    content = slide.fbox(width="fill", p_left=120, p_top=60)
    text_box = content.box(width="fill")
    text_box.update_style("default", elsie.TextStyle(color="black"))
    text_box.update_style("tt", elsie.TextStyle(color="green"))
    lst = unordered_list(text_box)
    lst.item().text("Try quoting string to get it to stop parsing")
    lst.item(show="2+").text("Realize error is parsing comment")
    lst.item(show="3+").text("Remove ~tt{:} character from comment in ~tt{srdf} files")
    lst.item(show="4+").text("Profit!")
    content.box(show="4+").image("images/rviz.png")


@slides.slide(debug_boxes=False)
def better_place(slide):
    bg = slide.box().image("layout_images/layout_3_bg.png")
    slide = slide.overlay()
    header = slide.box(width="fill", height="20%", p_left=120).text(
        "Better Place: ROS 2 XML Launch", style="header"
    )
    content = slide.fbox(width="fill", p_left=120, p_top=60)
    text_box = content.box(width="fill")
    text_box.update_style("default", elsie.TextStyle(color="black"))
    text_box.update_style("bold", elsie.TextStyle(color="black"))
    lst = unordered_list(text_box)
    lst.item().text(
        "Launch demo with ~bold{43} lines of XML vs ~bold{>500} lines of Python"
    )
    lst.item().text("Single ~code{moveit.yaml} config for MoveIt")
    lst.item().text(
        "ROS 2 XML Launch Docs: ~link{docs.ros.org/en/rolling/How-To-Guides/\nMigrating-from-ROS1/Migrating-Launch-Files.html}"
    )
    lst.item().text(
        "Comparing Python/XML/YAML: ~link{docs.ros.org/en/rolling/How-To-Guides/\nLaunch-file-different-formats.html}"
    )
    lst.item().text("Source: ~link{github.com/tylerjw/easy_ros2_launch_talk}")


@slides.slide(debug_boxes=False)
def thank_you(slide):
    bg = slide.box().image("layout_images/thank_you_bg.png")
    slide = slide.overlay(p_top=800)
    slide.update_style("default", elsie.TextStyle(align="middle"))
    slide.text("github.com/tylerjw/easy_ros2_launch_talk")


slides.render("easy-launch.pdf")
