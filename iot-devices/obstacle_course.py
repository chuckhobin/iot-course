import picar_4wd as fc
import time
from statistics import mean
from enum import Enum

# Hands-on Internet of Things Specialization  https://www.coursera.org/specializations/uiuc-iot
# IOT Devices Course
# Code for Hardware Lab
#
# Program the SunFounder PiCar-4WD smart car kit to autonomously navigate a simple obstacle course.

SPEED = 10
STEP = 2
MAX_LEFT_ANGLE = 90
MIN_LEFT_ANGLE = 80
MAX_RIGHT_ANGLE = -80
MIN_RIGHT_ANGLE = -90
OUTLIER_DISTANCE = 100

class TurnDirection(Enum):
    LEFT = 1
    RIGHT = 2
    UNKNOWN = 3

# Move the car forward until it is within 20cm of an obstacle directly in
# front of it.
def move_forward_until_blocked():
    # Be sure the ultrasonic sensor is facing forward.
    distance = fc.get_distance_at(0)
    time.sleep(0.5)
    while True:
        fc.forward(SPEED)
        distance = fc.get_distance_at(0)
        print('move forward distance=', distance)
        # Note that -1 and -2 can be returned by the get_distance()
        # function.  Keep moving forward if these values are seen.
        if distance >= 0 and distance <= 20:
            break
        time.sleep(0.25)
    fc.stop()

# This function is used to see if there is a "wall" on either side of the
# stopped car.  It moves the servo through a small arc, taking a distance
# reading over a series of small steps. 
def scan_arc(min_angle, max_angle, step):
    distances = {}
    current_angle = min_angle
    dist = fc.get_distance_at(current_angle)
    time.sleep(0.25)
    while current_angle <= max_angle:
        dist = fc.get_distance_at(current_angle)
        distances[current_angle] = dist
        print(current_angle, dist)
        current_angle += step
        time.sleep(0.25)
    return distances

# Compute the mean distance from a list of distance reading.
# If -1 or -2 is seen, we assume there is no obstacle detected
# and therefore we use a large "outlier" distance for that reading
# so our decision logic for turning the car will work correctly.
def compute_mean_distance(distances):
    count = len(distances)
    for i in range(count):
        if distances[i] < 0:
            distances[i] = OUTLIER_DISTANCE
    return mean(distances)

# When the car has stopped in front of an obstacle, scan to the left and to the right
# to see which side has a nearby wall.  By making distance measurements on both sides 
# we can detect the wall.  We then set the turn direction to the side that does not have
# a wall.
#
# We make several distance measurements over a small arc on each side and compute an 
# mean distance.  This is to smoothe out any inaccuracies in individual pings.
def get_turn_direction():
    left_distances = scan_arc(MIN_LEFT_ANGLE, MAX_LEFT_ANGLE, STEP) 
    right_distances = scan_arc(MIN_RIGHT_ANGLE, MAX_RIGHT_ANGLE, STEP) 
    left_mean_distance = compute_mean_distance(list(left_distances.values()))
    right_mean_distance = compute_mean_distance(list(right_distances.values()))
    print("left mean=", left_mean_distance)
    print("right mean=", right_mean_distance)
    if left_mean_distance < right_mean_distance:
        return TurnDirection.RIGHT
    elif right_mean_distance < left_mean_distance:
        return TurnDirection.LEFT
    else:
        return TurnDirection.UNKNOWN

# Move the car forward until an obstacle is reached, then stop. 
# Detect the presence of a wall on one side of the car.
# Turn the car 90 degrees in the direction away from the wall. This
# will allow the car to proceed unimpeded to the next obstacle.
#
# Given the sensors available on the car, there is no way to accurately 
# detect when the car has turned 90 degrees after the turn is started.
# Through trial and error, we determined the amount of time it takes
# for the car to turn that much.
def navigate_through_one_obstacle():
    move_forward_until_blocked()
    turn_direction = get_turn_direction()
    print(turn_direction)
    if turn_direction == TurnDirection.LEFT:
        fc.turn_left(SPEED)
    elif turn_direction == TurnDirection.RIGHT:
        fc.turn_right(SPEED)
    # Wait the amount of time needed to make approximately one quarter turn.
    time.sleep(1.75)
    fc.stop()

# Move the car quickly forward and backward.
def finale():
    # One ... Two ... Cha-Cha-Cha
    fc.forward(SPEED)
    time.sleep(2.5)
    fc.backward(SPEED)
    time.sleep(0.5)
    fc.forward(SPEED)
    time.sleep(0.25)
    fc.backward(SPEED)
    time.sleep(0.25)
    fc.forward(SPEED)
    time.sleep(0.25)

    fc.stop()
    time.sleep(0.5)

    # Three ... Four ... Cha-Cha-Cha
    fc.forward(SPEED)
    time.sleep(0.5)
    fc.backward(SPEED)
    time.sleep(0.5)
    fc.forward(SPEED)
    time.sleep(0.25)
    fc.backward(SPEED)
    time.sleep(0.25)
    fc.forward(SPEED)
    time.sleep(0.25)

    fc.stop()

def main():

    # Give some time to start recording with the camera.
    time.sleep(5)

    # My obstacle course has 4 obstacles to navigate through.
    for i in range(4):
        navigate_through_one_obstacle()

    # Make the car dance when it reaches the end.
    finale()
 
if __name__ == "__main__":
    try: 
        main()
    finally: 
         fc.stop()
