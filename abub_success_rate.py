'''
ABUB SUCCESS RATE
Description
- Uses openCV to obtain some user-collected stats about autobub3 for pico40L data which is mainly focused on 
the bubble finding success rate


Authors
Nolan


### TO DO ###
- Make file finding method
- Get images displayed on screen
- Get stats recording into file
- special events
- rotate images
- get gifs to play
- interprate keystrokes
- UI?


### KNOWN BUGS ###
- finished runs variable is not working

'''
import numpy as np
import os
import cv2
import time

print('Using OpenCV V' + str(cv2.__version__))

stats_file = 'abub_stats.txt'



def main(raw_dir = '', recon_dir=''):

    #if we do not already have recorded data, we initialize the file
    if not os.path.exists(stats_file):
        with open(stats_file, 'w') as f:
            #we write title of our recorded categories
            f.write('runname\tev\tcam\tsuccess\ttype\n')
            f.close()

    #this should be a list of file names for abub data
    listing = os.listdir(recon_dir)

    #finished runs we already have stats for
    try:
        finished_runs = set(np.genfromtxt(stats_file, skip_header = 0, usecols = (1)))
    except:
        finished_runs = set()

    print(finished_runs)

    #looking at each file name in the listing
    for i in range(len(listing)):

        #this will get runname, eg. '20200921_2'
        runname = os.path.splitext(listing[i])[0][-10:]
        datapath = os.path.join(recon_dir, listing[i])
        

        #if we have already done this run we skip it
        #(doesnt account for stopping data collection in the middle of a run file)
        if runname in finished_runs:
            continue

        #here, we get the quantities ev, camera, frame0, horiz and vert
        data = np.genfromtxt(datapath, skip_header = 6, usecols = (1,4,5,6,7))

        #seperate the data
        ev = data[:,0]
        cam = data[:,1]
        frame0 = data[:,2]
        data_x = data[:,3]
        data_y = data[:,4]

        #we will look for an image for each entry
        for j in range(len(ev)):
            
            #this is the case where abub couldnt find a bubble -- it puts 0s
            if data_x[j] == 0 and data_y[j] == 0:
                write_output(runname, ev[j], cam[j], False)
                continue

            #now we get the image to show the user
            #path example: /path/to/raw/20200912_2/0/Images/cam2_image45.png

            key_pressed = False
            k = 0

            while not key_pressed:
                #changing the frame we are currently seeing
                current_frame = frame0[j] + k

                image_path = os.path.join(raw_dir, runname, str(int(ev[j])), 'Images', 'cam%.0d_image%.0d.png'%(cam[j], current_frame))
                
                #load image, and draw genesis coords circle onto it
                img = cv2.imread(image_path, cv2.IMREAD_COLOR)
                cv2.circle(img,(int(data_x[j]), int(data_y[j])), 50, (0,0,255), 2)

                #show it 
                cv2.imshow('image', img)

                keypress = cv2.waitKey(1)
                
                #quit event
                if keypress == ord('q'):
                    cv2.destroyAllWindows()
                    return
                
                #the user decides that a bubble is there
                if keypress == ord('y'):
                    key_pressed = True
                    write_output(runname, ev[j], cam[j], True)
                    
                #the user decides that it is a false positive
                if keypress == ord('n'):
                    key_pressed = True
                    write_output(runname, ev[j], cam[j], False)
                    
                
                #the time waited between frames of the gif
                time.sleep(.2)

                #we cycle through 6 frame about the trigger frame in a gif-like format
                k += 1
                if k == 4:
                    k = -3


                

            





def write_output(runname, ev, cam, success, evtype=None):
    # writes results into file
    # success is a bool with success or no success
    # evtype is if there is a special event like boiling, etc.

    if not evtype:
        evtype = 'NA'

    #bool to string
    success = str(success)
    
    #save data to file
    with open(stats_file, 'a') as f:\
        f.write('%s\t%.0d\t%.0d\t%s\t%s\n'%(runname, ev, cam, success, evtype))



main(raw_dir= '/mnt/d/40l-19-data', recon_dir='/home/nsand/data')
