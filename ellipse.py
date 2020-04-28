import math
import matplotlib.pyplot as plt

class Ellipse:

    def __init__(self, start, finish):
        # Parameters
        # ----------
        # start: List
        #        Gps coordinates [x,y,z] of beginning point of line
        # finish: List
        #         Gps coordinates [x,y,z] of end points of the line

        # Start and end point of h line for ellipse
        # Only x and z are needed, this is only for 2D
        self.start = [start[0], start[2]]
        self.finish = [finish[0], finish[2]]
        # How many points will be calculated on ellipse
        self.point_num = 100
        self.points = []
        self.ellipse_points = []
        # "Height" of a given ellipse (in meters)
        self.b = 2.5
        self.ellipse_calc()
    
    def ellipse_calc(self):
        try:
            # Calculate slope of line (not really needed)
            slope = 0
            try:
                slope = (self.finish[0] - self.start[0]) / (self.finish[1] - self.start[1])
            except Exception as e:
                pass

            # Get the a-value for the ellipse
            fs_len = math.sqrt((self.finish[0] - self.start[0])**2 + (self.finish[1] - self.start[1])**2)
            a = fs_len / 2

            # Get a range of points along vector FS
            # Find increment using point_num
            increment = fs_len / self.point_num

            # Find the midpoint of the line, will act as vertex of ellipse
            midpoint_x = (self.finish[0] + self.start[0]) / 2
            midpoint_y = (self.finish[1] + self.start[1]) / 2

            # Current 'x' counter var
            x_counter = self.start[0]
            # Create point_num # of points
            for i in range(self.point_num+1):
                #print(i)
                y = slope * x_counter - slope * self.finish[0] + self.finish[1]
                self.points.append([x_counter, y])
                if self.start[0] > self.finish[0]:
                    x_counter -= increment
                else:
                    x_counter += increment

            # Calculate x,z pairs for ellipse
            i = 0
            shift = 0
            for x_val, y_val in self.points:
                inner_frac = (1 - (x_val - midpoint_x)**2) / (a**2)
                #print(inner_frac)
                root = math.sqrt((self.b**2) * inner_frac)
                y = midpoint_y - root

                # Shift y value using midpoint
                if i == 0:
                    shift = y - midpoint_y
                    i += 1
                
                y -= shift

                self.ellipse_points.append([x_val, y])
            
        except Exception as e:
            print(e)
    
    # Plot the ellipse using matplotlib
    def plot_ellipse(self):
        fig = plt.figure()
        x, y = zip(*self.ellipse_points)
        plt.scatter(x, y, s=10, c='r',marker='x')
        plt.title("Show calculated ellipse on GPS map")
        plt.xlabel("X-coords")
        plt.ylabel("Z-coords")
        plt.show()
    
    # Plot the line the ellipse is based on with matplotlib
    def plot_line(self):
        fig = plt.figure()
        x, y = zip(*self.points)
        plt.scatter(x, y, s=10, c='r',marker='x')
        plt.title("Show calculated line on GPS map")
        plt.xlabel("X-coords")
        plt.ylabel("Z-coords")
        plt.show()