#!/usr/bin/env python3

from picture import Picture
import math

class SeamCarver(Picture):
    def energy(self, i: int, j: int) -> float:
        '''
        Return the energy of pixel at column i and row j
        '''
        width = self.width()
        height = self.height()

        # Raises IndexError() Exception if i and j are outside the image's prescribed range 
        if not(0 <= i < width and 0 <= j < height):
            raise IndexError()
        
        else: 
            # Obtain the RGB values of the pixels (i-1, j) and (i+1, j)
            xMinus = self[(i-1)%width, j]
            xPlus = self[(i+1)%width, j]

            # Get the absolute value of the difference between the x-gradients
            rx = abs(xPlus[0]-xMinus[0])
            gx = abs(xPlus[1]-xMinus[1])
            bx = abs(xPlus[2]-xMinus[2])
            # Raise the differences to the 2nd power 
            deltaX = rx**2 + gx**2 + bx**2
        
            #Obtain the RGB values of the pixels (i, j-1) and (i, j+1)
            yMinus = self[i, (j-1)%height]
            yPlus = self[i, (j+1)%height]
        
            # Get the absolute value of the difference between the y-gradients
            ry = abs(yPlus[0]-yMinus[0])
            gy = abs(yPlus[1]-yMinus[1])
            by = abs(yPlus[2]-yMinus[2])
            # Raise the differences to the 2nd power 
            deltaY = ry**2 + gy**2 + by**2

            # Implement the energy gradient function
            energyPixel = math.sqrt(deltaX + deltaY)
            return energyPixel

    def find_vertical_seam(self) -> list[int]:
        width, height = self.width(), self.height() 

        pictureEnergy = [[0 for i in range(width)] for y in range(height)]
        
        #create the energy tables
        for i in range(width-1, -1, -1):
            for j in range(height):
                pictureEnergy[j][i] = self.energy(i, j)

        leastEnergy = [[0 for i in range(width)] for y in range(height)]

        #Setting the first row of the leastEnergy table to be the first row of the pictureEnergy array
        leastEnergy[0] = pictureEnergy[0]

        #From the row under the working, proceeding down, find the leastenergy from its three neighbors above
        for i in range(height-1):
            for j in range(width):

                #Basically the values of the range of the row of the three(two if its a border) adjacent values
                j1, j2 = max(0, j-1), min(j+2, width) 

                #the minimum energy of the three neightbors above
                e = min(leastEnergy[i][j1:j2])

                energy_val = pictureEnergy[i+1][j]

                leastEnergy[i+1][j] += e
                leastEnergy[i+1][j] += energy_val

        miniIndexList = []
        g = 1
        for i in range(height): # this computes the seam
            if i == 0: #computes the very last row
                minimumValPerRow = min(leastEnergy[height-g])
                miniIndex = leastEnergy[height-g].index(minimumValPerRow)
                miniIndexList.append(miniIndex)
            else: #if its not the first row, continue
                if miniIndex+1 == width: #if the minimum value above the pixel to the right matches the width, meaning it is the right most border part of the image
                    k = min(leastEnergy[height-g-1][miniIndex-1], leastEnergy[height-g-1][miniIndex]) #then only the upper left and top value is considered
                    if (leastEnergy[height-g-1][miniIndex-1]) == k:
                        miniIndex = miniIndex-1
                    miniIndexList.append(miniIndex)
             
                elif miniIndex == 0: #if it is the left most border part of the image, then only the upper right and top value is considered
                    k = min(leastEnergy[height-g-1][miniIndex+1], leastEnergy[height-g-1][miniIndex])
                    if (leastEnergy[height-g-1][miniIndex+1]) == k:
                        miniIndex = miniIndex+1
                    miniIndexList.append(miniIndex)    
                    
                else: #otherwise, continue to search for the three minimum values above it            
                    k = min(leastEnergy[height-g-1][miniIndex-1], leastEnergy[height-g-1][miniIndex], leastEnergy[height-g-1][miniIndex+1])
                    if (leastEnergy[height-g-1][miniIndex-1]) == k:
                        miniIndex = miniIndex-1
                    elif (leastEnergy[height-g-1][miniIndex+1]) == k:
                        miniIndex = miniIndex+1
                    miniIndexList.append(miniIndex)
                g+=1

        miniIndexList.reverse()
 
        return miniIndexList

    def transpose_image(self):
        transposed = set()
        for col in range(self._width):
            for row in range(self._height):
                if(col,row) not in transposed and (row, col) not in transposed:
                    if row >= self.width() or col >= self.height():
                        self[row, col] = None
                        setTempPixel = True
                    temp = self[col, row]
                    self[col, row] = self[row, col]
                    self[row, col] = temp
                    if row >= self.width() or col >= self.height():
                        del self[col, row]
                    transposed.add((col, row))
                    transposed.add((row, col))
        tempWidth = self._width
        self._width = self._height
        self._height = tempWidth
        
    def find_horizontal_seam(self) -> list[int]:
        #transposes the image
        self.transpose_image()

        #applies vertical seam finder to find the horizontal seam
        horizontal_seam = self.find_vertical_seam()

        #transposes the image back to its original form
        self.transpose_image()
        return horizontal_seam 

    def remove_vertical_seam(self, seam: list[int]):
        '''
        Remove a vertical seam from the picture
        '''
        energyDiff = 0

        if self.width() == 1 or len(seam) != self.height():
            raise SeamError
        for i in range(len(seam)-1):
            energyDiff = abs(seam[i] - seam[i+1])
            if energyDiff > 1:
                raise SeamError
            
        else:      
            for r in range(len(seam)):      #r is equal to the row index at which the column in seam should be removed
                del self[seam[r], r]        #self[seam[r],r] is the pixel value
                                            #seam[r] = column coordinate                                   
                for p in range(self.width()-1):     
                    if p < seam[r]:
                        continue   
                    else:
                        self[p, r] = self [p+1, r]
                del self[self.width()-1,r]
            self._width -= 1

    def remove_horizontal_seam(self, seam: list[int]):
        '''
        Remove a horizontal seam from the picture
        '''
        energyDiff = 0

        if self.height() == 1 or len(seam) != self.width():
            raise SeamError
        for i in range(len(seam)-1):
            energyDiff = abs(seam[i] - seam[i+1])
            if energyDiff > 1:
                raise SeamError

        else: 
            self.transpose_image()
            self.remove_vertical_seam(seam)
            self.transpose_image()
            
class SeamError(Exception):
    pass

class IndexError(Exception):
    pass
