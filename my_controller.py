"""my_controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot, Motor, PositionSensor, GPS, Compass
from ellipse import Ellipse
import math, time

# create the Robot instance.
robot = Robot()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# Device setup

# Get motors
left_front = robot.getMotor("wheel1")
right_front = robot.getMotor("wheel2")
left_rear = robot.getMotor("wheel3")
right_rear = robot.getMotor("wheel4")

# Set acceleration
left_front.setPosition(float("inf"))
right_front.setPosition(float("inf"))
left_rear.setPosition(float("inf"))
right_rear.setPosition(float("inf"))
    
# Get GPS and enable
gps = robot.getGPS("gps")
gps.enable(timestep)

# Get compass and enable
compass = robot.getCompass("compass")
compass.enable(timestep)

# Functions

# Turn speed value
turn_speed = 0.25

# Make robot go forward
def forward():
    left_front.setVelocity(2)
    right_front.setVelocity(2)
    left_rear.setVelocity(2)
    right_rear.setVelocity(2)
    
# Make robot go backward
def stop():
    left_front.setVelocity(0)
    right_front.setVelocity(0)
    left_rear.setVelocity(0)
    right_rear.setVelocity(0)

# Make robot turn left
def left():
    left_front.setVelocity(turn_speed)
    left_rear.setVelocity(turn_speed)
    right_front.setVelocity(-turn_speed)
    right_rear.setVelocity(-turn_speed)

# Make robot turn right
def right():
    left_front.setVelocity(-turn_speed)
    left_rear.setVelocity(-turn_speed)
    right_front.setVelocity(turn_speed)
    right_rear.setVelocity(turn_speed)

# Drive in a line a given distance using gps coordinates
def line(gps_start, line_dist):
    # Check if distance has been traveled
    if abs(gps.getValues()[0] - gps_start[0]) > line_dist:
        # Stop moving 
        stop()
        return True
    else:
        forward()
        return False

# Gets the current compass bearing of robot in degrees
def get_bearing_in_degrees():
    # Get the radian values for bearing
    north = compass.getValues()
    # Convert to single radian value
    rad = math.atan2(north[0], north[2])
    # Convert to degrees
    bearing = (rad-1.5708) / math.pi * 180
    # If the bearing is negative, convert
    if bearing < 0.0:
        bearing = bearing + 360
    return bearing

# Given an angle in degrees, adjust the robot to face the right way
def adjust_to_angle_degrees(angle):
    # Get the current heading in degrees
    cur_angle = get_bearing_in_degrees()
    # Execution loop
    while robot.step(timestep) != -1:
        # Get the difference between desired and current angle (degrees)
        diff = angle - cur_angle
        # Refresh current angle
        cur_angle = get_bearing_in_degrees()
        # Normal desired angle
        if angle != 0 and angle != 360:
            if abs(diff) < 0.2:
                stop()
                break
        # 0/360 angle
        else:
            if cur_angle > 359.0 or cur_angle < 1.0:
                stop()
                break
        if diff > 0:
            left()
        else:
            right()

# Given a GPS coordinate target robot drives to target  
def drive_to_point_ellipse(gps_target):
    # Execution loop
    while robot.step(timestep) != -1:
        # Refresh the current point
        cur_point = gps.getValues()
        # Gets x and z diffs on driving plane
        x_diff = abs(gps_target[0] - cur_point[0])
        z_diff = abs(gps_target[2] - cur_point[2])
        # If within threshold stop
        if x_diff < 0.01 and z_diff < 0.01:
            stop()
            break
        else:
            forward()

# Logic for drawing a curve
def curve():
    # Get current and desired points for ellipse generation
    cur_point = gps.getValues()
    point_to = gps.getValues()
    point_to[0] -= curve_sep
    # Make ellipse from points
    ellipse = Ellipse(cur_point, point_to)
    to_travel = ellipse.ellipse_points    
    
    # Take x,z coord pairs and have robot drive to each one
    for x, z in to_travel:
        # Finding correct angle to drive on
        cur_point = gps.getValues()
        # Calculate the distance between current location and (x,z)
        dist = math.sqrt((cur_point[0] - x)**2 + (cur_point[2] - z)**2)
        # Calculate the abs(x_diff) between current location and (x,z)
        x_diff = abs(cur_point[0] - x)

        # Calculate angle from x axis for proper travel (radians)
        theta = math.acos(x_diff/dist)
        # Convert to degrees
        theta = theta * (180 / math.pi)
        # Adjust theta based on which moving up or down
        if z < cur_point[2]:
            theta += 90
        else:
            theta = 90 - theta
        # Adjust to new angle
        adjust_to_angle_degrees(theta)

        # Drive to point
        drive_to_point_ellipse([x,0,z])


    # Reset to line for next curve or final step
    adjust_to_angle_degrees(90)

# Vars for comparisions
# GPS
gps_start = []
# Compass
compass_start = []
init_mes = True
# Vars for movement
begin = True
curves = False
end = False

# Line dist for various things (in m)
line_dist = 0.15
curve_sep = 0.6
curve_jump = 0.3
peak_change = 0.5

# Main loop:
while robot.step(timestep) != -1:
    # Init starting measurements and set var to skip this next loop
    # Also orients to 90 degrees on the x-axis (flat)
    if init_mes:
        gps_start = gps.getValues()
        compass_start = compass.getValues()
        adjust_to_angle_degrees(90)
        init_mes = False
    
    # Go forward in straight line for beginning
    if begin:
        # Draw line until true
        result = line(gps_start, line_dist)
        if result:
            # Change pattern to peaks
            begin = False
            curves = True
            # Reset distances
            gps_start = gps.getValues()

    # Create curves
    if curves:
        # Make 4 curves
        for i in range(4):
            curve()
        # Change drive state
        curves = False
        end = True
        # Reset GPS coords
        gps_start = gps.getValues()
     
    # Create end line
    if end:
        result = line(gps_start, line_dist)
        adjust_to_angle_degrees(90)
        if result:
            end = False
            break  
     
# Enter here exit cleanup code.
print("TADA")