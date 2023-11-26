import numpy as np
from math import ceil, exp, pow
from math import sqrt
from random import randint

# function to convolve src image with a mask
def convolve(src, mask):
    src = src.astype(np.float64)
    output = np.zeros(shape=src.shape, dtype=float)
    height, width = src.shape
    length = len(mask)
    for y in range(height):
        for x in range(width):
            sum = float(mask[0] * src[y, x])
            for i in range(1, length):
                sum += mask[i] * (
                        src[y, max(x - i, 0)] + src[y, min(x + i, width - 1)])
            output[y, x] = sum
    return output

# function to normalize a mask
def normalize(mask):
    sum = 2 * np.sum(np.absolute(mask)) + abs(mask[0])
    return np.divide(mask, sum)

# function to smoothen an image
def smoothen(src, sigma):
    mask = make_gaussian_filter(sigma)
    mask = normalize(mask)
    tmp = convolve(src, mask)
    dst = convolve(tmp, mask)
    return dst

# function to create a gaussian filter
def make_gaussian_filter(sigma):
    sigma = max(sigma, 0.01)
    length = int(ceil(sigma * 4.0)) + 1
    mask = np.zeros(shape=length, dtype=float)
    for i in range(length):
        mask[i] = exp(-0.5 * pow(i / sigma, i / sigma))
    return mask

# function to calculate difference between two pixels
def difference(red_band, green_band, blue_band, x1, y1, x2, y2):
    return sqrt(
        (red_band[y1, x1] - red_band[y2, x2]) ** 2 + \
        (green_band[y1, x1] - green_band[y2, x2]) ** 2 + \
        (blue_band[y1, x1] - blue_band[y2, x2]) ** 2
    )

# function to generate a random RGB image
def get_random_rgb_image():
    rgb = np.zeros(3, dtype=int)
    rgb[0] = randint(0, 255)
    rgb[1] = randint(0, 255)
    rgb[2] = randint(0, 255)
    return rgb

# function to generate a random grayscale image
def get_random_gray_image():
    gray = np.zeros(1, dtype=int)
    gray[0] = randint(0, 255)
    return gray

# class to implement Disjoint Set Data Structure
class DisjointSet:
    # constructor
    def __init__(self, n_elements):
        self.num = n_elements
        self.elements = np.empty(
            shape=(n_elements, 3),
            dtype=int
        )
        # initialize all elements of disjoint set
        for i in range(n_elements):
            self.elements[i, 0] = 0 #height of set
            self.elements[i, 1] = 1 #nummber of nodes
            self.elements[i, 2] = i #parent node

    # function to return number of nodes in set x
    def size(self, x):
        return self.elements[x, 1]  #how many node in the set

    # function to return number of disjoint sets
    def num_sets(self):
        return self.num
    # function to find the root of set x and perform path compression
    def find(self, x): # return root of set
        y = int(x)
        while y != self.elements[y, 2]:
            y = self.elements[y, 2]
        self.elements[x, 2] = y
        return y

    def join(self, x, y): # merge two sets based on height of sets
        if self.elements[x, 0] > self.elements[y, 0]:
            self.elements[y, 2] = x
            self.elements[x, 1] += self.elements[y, 1]
        else:
            self.elements[x, 2] = y
            self.elements[y, 1] += self.elements[x, 1]
            if self.elements[x, 0] == self.elements[y, 0]:
                self.elements[y, 0] += 1
        self.num -= 1


def segment_graph(num_vertices, num_edges, edges, c): # c is the threshold that we add to find evidence of boudries
    edges[0 : num_edges, :] = edges[edges[0 : num_edges, 2].argsort()] #sort edges based on value of difference bitween her pixels
    print(num_vertices)
    u = DisjointSet(num_vertices)
    threshold = np.zeros(shape=num_vertices, dtype=float)
    for i in range(num_vertices):
        threshold[i] = c
    for i in range(num_edges):
        pedge = edges[i, :]  # pedge[0] is pixel(1) pedge[1] is his neighbour pedge[2] weight
        a = u.find(pedge[0]) # parent of pixel(1)
        b = u.find(pedge[1]) # parent of pixel(1) neighbour
        if a != b:
            if (pedge[2] <= threshold[a]) and (pedge[2] <= threshold[b]):
                u.join(a, b)  # combine a and b
                a = u.find(a)
                threshold[a] = pedge[2] + (c / u.size(a))
    return u


def segment(in_image, sigma, k, min_size):
    height, width, band = in_image.shape
    smooth_red_band = smoothen(in_image[:, :, 0], sigma)
    smooth_green_band = smoothen(in_image[:, :, 1], sigma)
    smooth_blue_band = smoothen(in_image[:, :, 2], sigma)
    # build graph
    edges_size = width * height * 4
    edges = np.zeros(shape=(edges_size, 3), dtype=object)
    num = 0
    for y in range(height):
        for x in range(width):
            # print(edges)
            if x < width - 1:
                edges[num, 0] = int(y * width + x)
                edges[num, 1] = int(y * width + (x + 1))
                edges[num, 2] = difference(
                    smooth_red_band, smooth_green_band,
                    smooth_blue_band, x , y , x + 1 , y
                )
                num += 1
            if y < height - 1:
                edges[num, 0] = int(y * width + x)
                edges[num, 1] = int((y + 1) * width + x)
                edges[num, 2] = difference(
                    smooth_red_band, smooth_green_band,
                    smooth_blue_band, x, y, x, y + 1
                )
                num += 1
            if (x < width - 1) and (y < height - 1): # height - 2
                edges[num, 0] = int(y * width + x)
                edges[num, 1] = int((y + 1) * width + (x + 1))
                edges[num, 2] = difference(
                    smooth_red_band, smooth_green_band,
                    smooth_blue_band, x, y, x + 1, y + 1
                )
                num += 1
            if (x < width - 1) and (y > 0):
                edges[num, 0] = int(y * width + x)
                edges[num, 1] = int((y - 1) * width + (x + 1))
                edges[num, 2] = difference(
                    smooth_red_band, smooth_green_band,
                    smooth_blue_band, x, y, x + 1, y - 1
                )
                num += 1
    u = segment_graph(width * height, num, edges, k)
    for i in range(num): # to enhance segmentation
        a = u.find(edges[i, 0])
        b = u.find(edges[i, 1])
        if (a != b) and ((u.size(a) < min_size) or (u.size(b) < min_size)):
            u.join(a, b)
    num_cc = u.num_sets()
    output = np.zeros(shape=(height, width, 3))

    colors = np.zeros(shape=(height * width, 3))
    for i in range(height * width):
        colors[i, :] = get_random_rgb_image()
    for y in range(height):
        for x in range(width):
            comp = u.find(y * width + x)
            output[y, x, :] = colors[comp, :]
    return output


