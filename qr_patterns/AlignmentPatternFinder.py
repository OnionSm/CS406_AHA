import sys 
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from .AlignmentPattern import AlignmentPattern

class AlignmentPatternFinder:
    def __init__(self, image, startX, startY, width, height, moduleSize, resultPointCallback=None):
        """
        Creates a finder that will look in a portion of the whole image.
        :param image: 2D list or similar structure representing the binary image.
        :param startX: left column from which to start searching.
        :param startY: top row from which to start searching.
        :param width: width of region to search.
        :param height: height of region to search.
        :param moduleSize: estimated module size so far.
        :param resultPointCallback: optional callback when a point is found.
        """
        self.image = image
        self.possibleCenters = []
        self.startX = startX
        self.startY = startY
        self.width = width
        self.height = height
        self.moduleSize = moduleSize
        self.crossCheckStateCount = [0, 0, 0]
        self.resultPointCallback = resultPointCallback

    def find(self):
        startX = self.startX
        height = self.height
        maxJ = startX + self.width
        middleI = self.startY + height // 2
        stateCount = [0, 0, 0]

        for iGen in range(height):
            i = middleI + ((iGen + 1) // 2 if iGen % 2 == 0 else -(iGen + 1) // 2)
            stateCount = [0, 0, 0]
            j = startX

            # Skip leading white pixels
            while j < maxJ and not self.image[i][j]:
                j += 1

            currentState = 0
            while j < maxJ:
                if self.image[i][j]:
                    if currentState == 1:
                        stateCount[1] += 1
                    else:
                        if currentState == 2:
                            if self.foundPatternCross(stateCount):
                                confirmed = self.handlePossibleCenter(stateCount, i, j)
                                if confirmed:
                                    return confirmed
                            stateCount[0], stateCount[1] = stateCount[2], 1
                            stateCount[2] = 0
                            currentState = 1
                        else:
                            stateCount[currentState] += 1
                else:
                    if currentState == 1:
                        currentState += 1
                    stateCount[currentState] += 1
                j += 1

            if self.foundPatternCross(stateCount):
                confirmed = self.handlePossibleCenter(stateCount, i, maxJ)
                if confirmed:
                    return confirmed

        if self.possibleCenters:
            return self.possibleCenters[0]
        raise ValueError("Not Found")

    @staticmethod
    def centerFromEnd(stateCount, end):
        return (end - stateCount[2]) - stateCount[1] / 2.0

    def foundPatternCross(self, stateCount):
        moduleSize = self.moduleSize
        maxVariance = moduleSize / 2.0
        return all(abs(moduleSize - count) < maxVariance for count in stateCount)

    def crossCheckVertical(self, startI, centerJ, maxCount, originalStateCountTotal):
        maxI = len(self.image)
        stateCount = [0, 0, 0]
        i = startI

        while i >= 0 and self.image[i][centerJ] and stateCount[1] <= maxCount:
            stateCount[1] += 1
            i -= 1

        if i < 0 or stateCount[1] > maxCount:
            return float('nan')

        while i >= 0 and not self.image[i][centerJ] and stateCount[0] <= maxCount:
            stateCount[0] += 1
            i -= 1

        if stateCount[0] > maxCount:
            return float('nan')

        i = startI + 1
        while i < maxI and self.image[i][centerJ] and stateCount[1] <= maxCount:
            stateCount[1] += 1
            i += 1

        if i == maxI or stateCount[1] > maxCount:
            return float('nan')

        while i < maxI and not self.image[i][centerJ] and stateCount[2] <= maxCount:
            stateCount[2] += 1
            i += 1

        if stateCount[2] > maxCount:
            return float('nan')

        stateCountTotal = sum(stateCount)
        if 5 * abs(stateCountTotal - originalStateCountTotal) >= 2 * originalStateCountTotal:
            return float('nan')

        return self.centerFromEnd(stateCount, i) if self.foundPatternCross(stateCount) else float('nan')

    def handlePossibleCenter(self, stateCount, i, j):
        stateCountTotal = sum(stateCount)
        centerJ = self.centerFromEnd(stateCount, j)
        centerI = self.crossCheckVertical(i, int(centerJ), 2 * stateCount[1], stateCountTotal)
        if not (centerI != float('nan')):
            return None

        estimatedModuleSize = sum(stateCount) / 3.0
        for center in self.possibleCenters:
            if center.aboutEquals(estimatedModuleSize, centerI, centerJ):
                return center.combineEstimate(centerI, centerJ, estimatedModuleSize)

        point = AlignmentPattern(centerJ, centerI, estimatedModuleSize)
        self.possibleCenters.append(point)
        if self.resultPointCallback:
            self.resultPointCallback(point)
        return point
