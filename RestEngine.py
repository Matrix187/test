from http.server import BaseHTTPRequestHandler, HTTPServer
import cv2
import os
import time
import threading
import sys
import torch

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

from util import LogUtils
from util import ConfigUtils
from util import Constants
from util import ExtractFrames
from detection import drawOnImage
log      = LogUtils.log
config   = ConfigUtils.config

class Worker(object):
    """Worker implementation for jobs 
    
	"""

	
    def __init__(self, date,time, interval=1):
        """Initialize Worker for submitted jobs

        Args:
            date (string): current date.\n
            time(string): threshold parameter used for binary label prediction.
        Returns:
            dataset (BinaryLabelDataset): Transformed Dataset.
        """

		
        self.interval = interval
        self.dateParameter = date
        self.timeParameter = time
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution
		

    def generateVisualization(self,framesDir,redAlertDir):
        """Generated visualization.
        """
		
		       
        log.info("Generating video from frames dir: " + framesDir + " in: " + redAlertDir)
		

    def doAlert(self,framesDir,fps,averageNumOfPersons,greenAlertDir,redAlertDir,alertPercentage):
        """ Performs alert
		
        Args:
            framesDir (string): directory where frames are located
        Returns:
            Test: Returns self.
        """
        	

        log.info("Processing alert ...")

        if (averageNumOfPersons < alertPercentage):
            log.info("Processing RED alert (1 person detected) !!")
            outFile = os.path.join(redAlertDir,"result.avi")
            ExtractFrames.generateVisualization(framesDir, outFile, fps)
        else:
            log.info("Processing GREEN alert (2 person detected) !!")
            outFile = os.path.join(greenAlertDir, "result.avi")
            ExtractFrames.generateVisualization(framesDir, outFile,fps)		

    def funcToCheck(self, a,b,c):
        """ funcToCheck method

        Args:
            a (string): b c
        Returns:
            Test: Returns -1
        """

        log.info("Processing alert ...")

        return -1


    def getVideoByDate(self,year,month,day,hours,minutes,seconds,jobTempDir,threshold):
        """ Retrieves  relevant video file according to provided date/time
		
        Args:
            param: Input param.
        Returns:
            Test: Returns self.
        """
		
		
        foundDavFiles = []

        log.info("Searching for folder with name=date(yyyy-mm-dd): " + str(year) + "-" + str(month) + "-" + str(day) + " in " + self.rootVideoFolder)
        targetFolder = os.path.join(self.rootVideoFolder,str(year) + "-" + str(month) + "-" + str(day))
        if (not os.path.exists(targetFolder )):
            log.error("Not able to find records folder: " + targetFolder + " skipping ...")
            return foundDavFiles

        log.info("Video folder: " + targetFolder + " found, searching for DAV file by time ...")
        log.info("Searching for video by time(hh:mm:ss): " + str(hours) + "-" + str(minutes) + "-" + str(seconds))
        inputStartAbsoluteSeconds = int(hours)*60*60 + int(minutes)*60 + int(seconds) - threshold
        inputEndAbsoluteSeconds = int(hours) * 60 * 60 + int(minutes) * 60 + int(seconds) + threshold
        log.info("inputStartAbsoluteSeconds: " + str(inputStartAbsoluteSeconds) )
        log.info("inputEndAbsoluteSeconds: " + str(inputEndAbsoluteSeconds))

        for targetVideo in os.listdir(targetFolder):
            log.info("Checking time range of targetVideo: " + targetVideo)
            tempArr = targetVideo.split(".")[0].split("_")
            startTime = tempArr[len(tempArr)-2].replace(year+month+day,"")
            endTime = tempArr[len(tempArr)- 1].replace(year+month+day,"")
            timeArr = list(startTime)
            targetAbsoluteStartTime = int(timeArr[0] + timeArr[1])*60*60 + int(timeArr[2]+timeArr[3])*60 + int(timeArr[4]+timeArr[5])
            timeArr.clear()
            timeArr = list(endTime)
            targetAbsoluteEndTime = int(timeArr[0] + timeArr[1]) * 60 * 60 + int(timeArr[2] + timeArr[3]) * 60 + int(timeArr[4] + timeArr[5])


            if (targetAbsoluteStartTime <= inputStartAbsoluteSeconds and inputEndAbsoluteSeconds  <= targetAbsoluteEndTime):
                log.info(
                    "targetAbsoluteStartTime <= inputStartAbsoluteSeconds and inputEndAbsoluteSeconds  <= targetAbsoluteEndTime  : "
                    + str(targetAbsoluteStartTime) + " <= " + str(inputStartAbsoluteSeconds) + " and " + str(
                        inputEndAbsoluteSeconds) + " <= " + str(targetAbsoluteEndTime))
                log.info("Adding target video: " + targetVideo)
                foundDavFiles.append(os.path.join(targetFolder, targetVideo))
                continue

            if (targetAbsoluteStartTime <= inputStartAbsoluteSeconds and inputStartAbsoluteSeconds  <= targetAbsoluteEndTime):
                log.info(
                    "targetAbsoluteStartTime <= inputStartAbsoluteSeconds and inputStartAbsoluteSeconds  <= targetAbsoluteEndTime  : "
                    + str(targetAbsoluteStartTime) + " <= " + str(inputStartAbsoluteSeconds) + " and " + str(
                        inputStartAbsoluteSeconds) + " <= " + str(targetAbsoluteEndTime))
                log.info("Adding target video: " + targetVideo)
                foundDavFiles.append(os.path.join(targetFolder, targetVideo))
                continue

            if (targetAbsoluteStartTime <= inputEndAbsoluteSeconds and inputEndAbsoluteSeconds <= targetAbsoluteEndTime):
                log.info(
                    "targetAbsoluteStartTime <= inputEndAbsoluteSeconds and inputEndAbsoluteSeconds <= targetAbsoluteEndTime  : "
                    + str(targetAbsoluteStartTime) + " <= " + str(inputEndAbsoluteSeconds) + " and " + str(
                        inputEndAbsoluteSeconds) + " <= " + str(targetAbsoluteEndTime))
                log.info("Adding target video: " + targetVideo)
                foundDavFiles.append(os.path.join(targetFolder, targetVideo))
                continue


        if (len(foundDavFiles) == 0):
            log.error("No DAV video files found for specified time: " + str(hours) + "-" + str(minutes) + "-" + str(seconds))
            return foundDavFiles

        print(foundDavFiles)
        log.info("Found total relevant DAV videos: " + str(len(foundDavFiles)))

        foundMp4Files = ExtractFrames.convertDAVtoMP4(foundDavFiles,jobTempDir)
        log.info("Total converted to MP4 videos: " + str(len(foundMp4Files)))

        #foundVideoPath = "D:/poc4paz/paz_videos/PAZ_input.avi"
        return foundMp4Files
		
		
		
def main():
    hostName = config[Constants.GLOBAL][Constants.HTTP_HOST]
    hostPort = config[Constants.GLOBAL][Constants.HTTP_PORT]
    myServer = HTTPServer((hostName, int(hostPort)), MyServer)
    log.info(str(time.asctime()) + "Starting REST Engine Service on - " + hostName + ":" + str(hostPort) + ".")

    try:
        myServer.serve_forever()
    except KeyboardInterrupt:
        pass

    myServer.server_close()
    log.info(str(time.asctime()) + "Terminating REST Engine Service on - " + hostName + ":" + str(hostPort) + ".")

if __name__ == "__main__":
    main()		