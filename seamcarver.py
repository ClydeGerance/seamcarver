#!/usr/bin/env python3

from picture import Picture
from PIL import Image
import math

class SeamCarver(Picture):
    ## TO-DO: fill in the methods below
    def energy(self, i: int, j: int) -> float:
        '''
        Return the energy of pixel at column i and row j
        '''
        # Border pixels have maximum energy.
        if i == 0 or i == self.width() - 1 or j == 0 or j == self.height() - 1:
            return 1000

        def square_gradient(a, b):
            """Calculate the square of the gradient between two colors."""
            return sum((a[k] - b[k]) ** 2 for k in range(3))

        # Get the colors around the pixel (i, j).
        color_up = self[i, j - 1]
        color_down = self[i, j + 1]
        color_left = self[i - 1, j]
        color_right = self[i + 1, j]

        # Calculate the gradients.
        gradient_x = square_gradient(color_right, color_left)
        gradient_y = square_gradient(color_down, color_up)

        # Return the energy.
        return math.sqrt(gradient_x + gradient_y)

    def find_vertical_seam(self) -> list[int]:
        '''
        Return a sequence of indices representing the lowest-energy
        vertical seam
        '''
        width, height = self.width(), self.height()
        energy = [[self.energy(x, y) for y in range(height)] for x in range(width)]
        dist_to = [[float('inf')] * height for _ in range(width)]
        edge_to = [[0] * height for _ in range(width)]

        for x in range(width):
            dist_to[x][0] = energy[x][0]

        for y in range(1, height):
            for x in range(width):
                # Check pixel above.
                if dist_to[x][y - 1] + energy[x][y] < dist_to[x][y]:
                    dist_to[x][y] = dist_to[x][y - 1] + energy[x][y]
                    edge_to[x][y] = x

                # Check pixel above and to the left.
                if x > 0 and dist_to[x - 1][y - 1] + energy[x][y] < dist_to[x][y]:
                    dist_to[x][y] = dist_to[x - 1][y - 1] + energy[x][y]
                    edge_to[x][y] = x - 1

                # Check pixel above and to the right.
                if x < width - 1 and dist_to[x + 1][y - 1] + energy[x][y] < dist_to[x][y]:
                    dist_to[x][y] = dist_to[x + 1][y - 1] + energy[x][y]
                    edge_to[x][y] = x + 1

        # Find the end of the minimum energy seam.
        min_dist = min(dist_to[x][height - 1] for x in range(width))
        min_x = [x for x in range(width) if dist_to[x][height - 1] == min_dist][0]

        # Reconstruct the seam path.
        seam = [min_x]
        for y in range(height - 1, 0, -1):
            min_x = edge_to[min_x][y]
            seam.append(min_x)

        seam.reverse()
        return seam

    def find_horizontal_seam(self) -> list[int]:
        '''
        Return a sequence of indices representing the lowest-energy
        horizontal seam
        '''
        # Transpose the image for horizontal seam calculation.
        transposed_picture = Picture(self.picture().transpose(Image.ROTATE_90))
        seam_carver_transposed = SeamCarver(transposed_picture.picture())
        transposed_seam = seam_carver_transposed.find_vertical_seam()

        # Transpose the seam to fit the original orientation.
        return transposed_seam

    def remove_vertical_seam(self, seam: list[int]):
        '''
        Remove a vertical seam from the picture
        '''
        width, height = self.width(), self.height()

        if width <= 1:
            raise SeamError("Width of the image is too small to remove a seam")

        if not all(0 <= x < width for x in seam):
            raise SeamError("Invalid seam")

        if any(abs(seam[j] - seam[j - 1]) > 1 for j in range(1, len(seam))):
            raise SeamError("Invalid seam")

        # Remove the seam
        for y in range(height):
            for x in range(seam[y], width - 1):
                self[x, y] = self[x + 1, y]
            del self[width - 1, y]  # Delete the last pixel in the row.

        self._width -= 1  # Update the image width.

    
    def remove_horizontal_seam(self, seam: list[int]):
        '''
        Remove a horizontal seam from the picture
        '''
        height = self.height()

        if height <= 1:
            raise SeamError("Height of the image is too small to remove a seam")

        if not all(0 <= y < height for y in seam):
            raise SeamError("Invalid seam")

        if any(abs(seam[i] - seam[i - 1]) > 1 for i in range(1, len(seam))):
            raise SeamError("Invalid seam")

        # Remove the seam by transposing and using remove_vertical_seam
        transposed_picture = Picture(self.picture().transpose(Image.ROTATE_90))
        seam_carver_transposed = SeamCarver(transposed_picture.picture())
        seam_carver_transposed.remove_vertical_seam(seam)

        # Update the picture with the transposed and seam-removed image.
        self.__dict__ = seam_carver_transposed.__dict__
        self._height -= 1  # Update the image height.

class SeamError(Exception):
    pass
