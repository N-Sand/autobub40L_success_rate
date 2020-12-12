'''
ABUB SUCCESS RATE
Description
- Uses openCV to obtain some user-collected stats about autobub3 for pico40L data which is mainly focused on 
the bubble finding success rate


Authors
Nolan


### TO DO ###
- Make file finding method
- rotate images (not necessary)
- untarring


### KNOWN BUGS ###
- it only checks past runs not every single event so it might omit some if you try to do this in >1 sessions -- can be fixed by erasing
some of the text file entries

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
        finished_runs = set(np.genfromtxt(stats_file, skip_header = 1, usecols = (0), dtype=str))

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
                write_output(runname, ev[j], cam[j], False, evtype='cantfind')
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
                cv2.circle(img,(int(data_x[j]), int(data_y[j])), 50, (0,0,255), 1)


                #printing instructions onto image
                cv2.putText(
                    img, #numpy array on which text is written
                    "q - quit    y - correct    n - incorrect  o - overcount/doublecount  b - boiling    m - cam moved    c - cam glitch", #text
                    (20,20), #position at which writing has to start
                    cv2.FONT_HERSHEY_SIMPLEX, #font family
                    0.5, #font size
                    (0, 0, 255, 255), #font color
                    1)

                #show it 
                cv2.imshow('image', img)

                keypress = cv2.waitKey(1)
                

                #KEYSTROKE EVENTS

                #quit event
                if keypress == ord('q'):
                    cv2.destroyAllWindows()
                    display_results()
                    return
                
                #the user decides that a bubble is there
                if keypress == ord('y'):
                    key_pressed = True
                    write_output(runname, ev[j], cam[j], True)
                    
                #the user decides that it is a false positive
                if keypress == ord('n'):
                    key_pressed = True
                    write_output(runname, ev[j], cam[j], False)

                #the user decides that this is counting the same bubble more than once
                if keypress == ord('o'):
                    key_pressed = True
                    write_output(runname, ev[j], cam[j], True, evtype='multi')
                
                #the user decides that this is a boiling event
                if keypress == ord('b'):
                    key_pressed = True
                    write_output(runname, ev[j], cam[j], True, evtype='boiling')

                #the user decides that the camera moved
                if keypress == ord('m'):
                    key_pressed = True
                    write_output(runname, ev[j], cam[j], True, evtype='giration')

                #the user decides that the camera malfunctioned -- like a sudden change in a column of pixels or something
                if keypress == ord('c'):
                    key_pressed = True
                    write_output(runname, ev[j], cam[j], True, evtype='glitch')

                #the time waited between frames of the gif
                time.sleep(.2)

                #we cycle through 6 frame about the trigger frame in a gif-like format
                k += 1
                if k == 4:
                    k = -3

    display_results()
                

            
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

def display_results():
    #prints the results of abub data
    data = np.genfromtxt(stats_file, skip_header = 1, dtype=str)

    runname = data[:,0]
    ev = data[:,1]
    cam = data[:,2]
    success = data[:,3]
    evtype = data[:,4]

    N = len(success)

    #success rate (main goal)
    success_true = len(np.where(success == 'True')[0])

    #other stats like boiling events or camera shakes
    N_boiling = len(np.where(evtype == 'boiling')[0])

    N_giration = len(np.where(evtype == 'giration')[0])

    N_cam_glitch = len(np.where(evtype == 'glitch')[0])


    print('Success rate: %f' % (success_true/N))
    print('Boiling events per 100: %f' % (100 * N_boiling/N))
    print('Cam movements per 100: %f' % (100 * N_giration/N))
    print('Cam glitches per 100: %f' % (100 * N_cam_glitch/N))



main(raw_dir= '/mnt/d/40l-19-data', recon_dir='/home/nsand/data')
