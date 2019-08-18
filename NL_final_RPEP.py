#!/usr/bin/env python
######################################################################################
### 																			   ###
### The Interaction Between Cognitive Control, Reward Representation and Scale     ###
###                                                                                ###
######################################################################################
"""

Research project in Experimental Psychology

@code by Isaiah Silverstein

## Experimental Design

Flanker tast w 5 different reward bins ; 2X2X5 design:

-> (congruent (Left/Right) | incongruent (Left/Right) )         "Congruency"

  X( deterministic scale | probabilistic scale )                "Reward Presentation"
  
  X( Bin1 | Bin2 | Bin3 | Bin4 | Bin5 )                         "Reward Size"


Reward Presentations differ per block, with reward size fluctuating within blocks. 



To escape the experiment at any time press ctrl+q  


"""
# # # # # # #
# The Code  #
# # # # # # #


#imports
from __future__ import division
from psychopy import data, visual, core, event,gui
import os, time, pandas, random, platform
import numpy as np

""" """ """ """ """ """ """ 
CORE PARAMETERS

The section below is for adjusting specific parameters:
the number of trials, blocks, repetitions,loops AND 
the timing of certain processes (fixation cross  , messages,etc.)

""" """ """ """ """ """ """
#Trials and Blocks #

n_trials = 140 #per block
n_conditions = 10
n_trial_rep = 7 #n_trials/n_conditions

n_blocks = 9  # block 0 is a practice block
n_practice_trials = 4
n_test_trials = 4


# Time settings #

t_fix_cross = .30
t_blank_screen =0.2
response_deadline = 0.4
t_reward_announcement = 1.2
t_feedback = .6

#Giving an estimate of how long the experiment will last
total_time = ((t_reward_announcement+t_fix_cross+response_deadline+t_feedback)*(((n_blocks-1)*n_trials)+n_practice_trials))/60
print("The total time of the experiment, excluding, breaks and instructions is around {0} minutes".format(total_time))

#Response Keys

left_key = 'k'
right_key = 'm'

#Upper limit noise of reward scale (measure for how far the reward fluctuates from the bin)
noise_upper_limit = 3

# Setting up other intial variables and objects
##   The Timer
experiment_timer = core.Clock()
experiment_times = []

# Initialising the Window
win = visual.Window(fullscr = True, color = 'black', allowGUI = True)


##   Text objects
# Empty instruction text object
instructions = visual.TextStim(win, text = "")
fix_cross = visual.TextStim(win, text = '+')
block_completed = visual.TextStim(win, text = "")
# Empty reward and accuracy counter
acc_counter = []
reward_counter = []

""" " """ """ """ """
Below is a short description of the used functions in the script:


directory_set() : calls up a gui, creates a unique data file and intializes the TrialHandler

wait_for_keypress(): simply halts the script until relevant keys are pressed 
                     and stops the script if the escape key is pressed

experiment_init_instructions(): creates intial instruction of the experiment

do_they_get it(): makes sure the participant understands instructions

instructions_per_block(): adjust instructions depending on the experimental block

counterbalance(): counterbalances the block order between participants

randomize(): creates the dataFram, transforms into a randomized list
             that has all the relevant information. If the user sets the object 
             'testrun' to 1, this list is a lot shorter and data isn't logged

create_reward_stimulus(): creates the relevant reward description 

create_trial_stimulus(): creates the relevant target flanker stimulus

performance_processing(): takes the results of the trial and spits out
                          the accuracy, the earned reward and relevant feedback
""" """ """ """ """ """ """

####################################################
################### FUNCTIONS ######################
####################################################


# Global event key (with modifier) to quit the experiment ("shutdown key").
event.globalKeys.add(key='q', modifiers=['ctrl'], func=core.quit)


# Creating a file for the participant and their data
'''
 ! IMPORTANT ! IMPORTANT !
CREATE A FOLDER WITH NAME "DATA" IN THE SAME FOLDER WHERE THE SCRIPT IS LOCATED
 ! MPORTANT ! IMPORTANT !
'''
 
## This functions creates the relevant data files while simultaneously gathering participant info
def directory_set():
    ##Calling up the current directory 
    my_directory =  os.getcwd()
    #
    ## participant info

    #initiate GUI
    already_exists = True
    while already_exists:
        info = { "Name":"", "Participant number": "","Gender": ["Female","Male","Other"], "testrun": [0,1]}
        #platform dependent notation
        if platform.system() == 'Windows':
            slash = '\\'
        else:
            slash = '/'
        win.mouseVisible = True
        #GUI object
        myDlg = gui.DlgFromDict(dictionary = info, title = "Response Conflict Experiment",show = False)
        myDlg.show()
        #Creating a folder for the participant
        # WARNING !!! make sure to create a folder with the name 'DATA' in the same location as the script
        directory_to_write_to = my_directory + slash + "DATA" +slash + "subject_"+info["Participant number"]
        
        #making the directory
        if not os.path.isdir(directory_to_write_to):
            os.mkdir(directory_to_write_to)
        #initiating a file name
        filename = directory_to_write_to + slash +"subject_" + str(info["Participant number"]) + "_data"

        #checking if file already exists or not
        if info["Participant number"].isdigit() == True:
            if not os.path.isfile(filename+".csv"):
                    already_exists = False
            else:
                myDlg2 = gui.Dlg(title = "Error")
                myDlg2.addText("Try another participant number")
                myDlg2.show()
        else:

            myDlg2 = gui.Dlg(title = "Error")
            myDlg2.addText("Try another participant number")
            myDlg2.show()
    #creating an ExperimentHandler object (in the correct location ! yay !)
    thisExp = data.ExperimentHandler(dataFileName=filename)
    
    #returning the relevant variables
    return thisExp, info




#waits for key to be pressed returns list with key pressed
def wait_for_keypress():
    keys = event.waitKeys(keyList = ['space','b','escape'])
    if keys[0] == 'escape':
        win.close()
        core.quit()
    else:
        return keys


# Instructional elements at the beginning of the experiment
def experiment_init_instructions():
    
    starting_instructions = ["Hallo {0} ! Welkom bij dit experiment \n\n druk de spatiebalk om verder te gaan".format(info["Name"]),
                              "Tijdens het experiment krijg je een reeks van pijlen te zien. Het is de bedoeling dat je telkens de orientatie van de middenste pijl aanduid."
                              +"\n \n \ndruk de spatiebalk om verder te gaan \n of 'b' om terug te gaan",
                              "Dit is een voorbeeld van zo'n pijlenreeks:\n\n              >><>>\n\nHier is de orientatie van de middenste pijl: 'Links'\n \ndruk de spatiebalk om verder te gaan \n of 'b' om terug te gaan",
                              "Voor elke reeks zal er een scherm verschijnen die de beloning die je kan ontvangen toont.\n"
                              + "Je krijgt uitsluitend een beloning als je de opgave juist beantwoordt\n \n \ndruk de spatiebalk om verder te gaan \n of 'b' om terug te gaan",
                              "De beloningen worden beschreven in punten, je hebt 200 punten nodig voor 1.25 cent, dus zorg ervoor dat je genoeg punten verzamelt!"+
                              "\n \n \ndruk de spatiebalk om verder te gaan \n of 'b' om terug te gaan",
                              "Om aan te duiden dat de pijl naar links wijst: druk de '{0}' toets\nOm aan te duiden dat de pijl naar rechts wijst: druk de '{1}' toets".format(left_key,right_key)+
                              "\n \n \ndruk de spatiebalk om verder te gaan \n of 'b' om terug te gaan",
                              "Je tijd om te antwoorden is beperkt, dus reageer zo snel mogelijk!\n\n\ndruk de spatiebalk om verder te gaan \n of 'b' om terug te gaan",
                              "We zullen eerst een paar pijlenreeksen oefenen.  Hierna is het niet meer mogelijk om terug te gaan"+
                              "\n \n \ndruk de spatiebalk om verder te gaan \n of 'b' om terug te gaan"]
    i = 0

    while i < len(starting_instructions):
        
        instructions.text = starting_instructions[i]
        
        instructions.draw()
        win.flip()
        k = wait_for_keypress()
        if k == ['b'] and i > 0:
            i = i-1
        elif k == ['space']:
            i += 1

    return    

def do_they_get_it():
    practice_stimulus = visual.TextStim(win, text = '',units = 'norm', height = .12,pos = [0,-0.2])
    practice_feedback = visual.TextStim(win, text = '')
    instructions.text = "Duid de orientatie aan van de pijl in het midden van de reeks"

    #first practice round 
    practice_stimulus.text = ">><>>"
    right_answer = False
    while not right_answer:
        instructions.draw()
        practice_stimulus.draw()
        win.flip()
        keypress = event.waitKeys(keyList =[left_key,right_key])
        ##If they get it
        if keypress[0] == left_key:
            right_answer = True
        ## If they don't get it
        else: 
            practice_feedback.text = "Fout!\n Voor links, druk '{0}'\n Voor rechts, druk '{1}'\n\n\nspatie om verder te gaan".format(left_key,right_key)
            practice_feedback.draw()
            win.flip()
            wait_for_keypress()
    #They got it!
    practice_feedback.text = "Correct !\n\n\nspatie om verder te gaan"
    practice_feedback.draw()
    win.flip()
    wait_for_keypress()

    practice_stimulus.text = ">>>>>"
    right_answer = False
    while not right_answer:
        instructions.draw()
        practice_stimulus.draw()
        win.flip()
        keypress = event.waitKeys(keyList =[left_key,right_key])
        ##If they get it
        if keypress[0] == right_key:
            right_answer = True
        ## If they don't get it
        else: 
            practice_feedback.text = "Fout!\n Voor links, druk '{0}'\n Voor rechts, druk '{1}'\n\n\nspatie om verder te gaan".format(left_key,right_key)
            practice_feedback.draw()
            win.flip()
            wait_for_keypress()
    #They got it!
    practice_feedback.text = "Correct !\n\n\nspatie om verder te gaan naar de oefenronde"
    practice_feedback.draw()
    win.flip()
    wait_for_keypress()

    return


#counterbalancing the subjects for block design
def counterbalance(participant_number):
    if participant_number%2 == 0:
        c_b = 1 
    else:
        c_b = 0
    
    return c_b


# RANDOMIZATION: creates the list of trials and their info, randomizes them according to block
# if the option testrun is set to '1' in the GUI then this list is significantly shortened
def randomize(c_b, block):
    
    # Variables and their Parameters
    bins = ['Bin_1','Bin_2','Bin_3','Bin_4','Bin_5']
    scaleType = ['Prob','Det']
    congruency = ['L_Con','R_Con','L_Incon','R_Incon']
    
    # Inserting the parameters into the block design
 
    if block !=0:
        if block%2 == c_b:
            Design = data.createFactorialTrialList({"Bins": bins, "Congruency": congruency})
            dataFrame = pandas.DataFrame.from_dict(Design)
            dataFrame["ScaleType"] = "Prob"
        else:
            Design = data.createFactorialTrialList({"Bins": bins, "Congruency": congruency})
            dataFrame = pandas.DataFrame.from_dict(Design)
            dataFrame["ScaleType"] = "Det"
    else:
        Design = data.createFactorialTrialList({"ScaleType": scaleType,"Bins": bins, "Congruency": congruency})
        dataFrame = pandas.DataFrame.from_dict(Design)

    # Adding in index tags and correct response column via DataFrame()
    
    ##adding in index tags
    dataFrame["Tag"] = range(len(dataFrame))
    
    ##adding in correct responses 
    dataFrame['CorAns'] = dataFrame["Congruency"]
    dataFrame['CorAns'].replace(['L_Con','R_Con','L_Incon','R_Incon'],[left_key,right_key,left_key,right_key],inplace = True)

    ##adding in reward magnitude
    dataFrame['BinSize'] =  dataFrame['Bins']
    dataFrame['BinSize'].replace(['Bin_1','Bin_2','Bin_3','Bin_4','Bin_5'],[0,20,50,80,100],inplace = True)

    
    
    #Convert dataframe back to list of dictionaries
    trial_list = pandas.DataFrame.to_dict(dataFrame, orient = "records")
    



    # TESTRUN
    # If the experimenter wishes to test-run option, reduced amount of trials are given
    if int(info["testrun"]) == 1:
        
        ## including a practice block
        if block == 0:
            trials = data.TrialHandler(trialList = random.sample(trial_list,n_practice_trials),  nReps = 1, method = "random")
        else: 
            trials = data.TrialHandler(trialList = random.sample(trial_list,n_test_trials), nReps=1, method='random')
            thisExp.addLoop(trials)   
    else:
        if block == 0:
            trials = data.TrialHandler(trialList = random.sample(trial_list,n_practice_trials), nReps=1, method='random')
        else:
            trials = data.TrialHandler(trialList = trial_list, nReps=n_trial_rep, method='random')
            thisExp.addLoop(trials)
    
    return trials



# Creates the description of the type of reward of each trial
def create_reward_stimulus(trial):
    reward_announcement = visual.TextStim(win, text = "")
    reward_size_text = visual.TextStim(win, text = "")
    rand_noise  = noise_upper_limit + 1

    while abs(rand_noise) > noise_upper_limit:

        rand_noise = round(int(np.random.normal(0,5,1)),2)
        
    if trial["Bins"] == "Bin_1":
        reward_size = int(trial['BinSize'])
    elif trial["Bins"] == "Bin_2":
        reward_size = int(trial['BinSize']  + rand_noise)
    elif trial["Bins"] == "Bin_3":
        reward_size = int(trial['BinSize']  + rand_noise)
    elif trial["Bins"] == "Bin_4":
        reward_size = int(trial['BinSize']  + rand_noise)
    else:
        reward_size = int(trial['BinSize']  - abs(rand_noise))


    if trial["ScaleType"] == "Prob":
    	reward_announcement.text = "The chance of a reward is:"
        reward_size_text.text = "{0} %".format(reward_size)
        reward_size_text.color = [0,0.7,1]
    else:
    	reward_announcement.text = "The size of the reward is:"
        reward_size_text.text = "{0}".format(reward_size)
        reward_size_text.color = [0,0.7,1]



    reward_announcement.pos = [0,0.2] 
    return reward_size, reward_announcement, reward_size_text

# Creates the relevant target stimulus depending on the trial
def create_trial_stimulus(trial):
    trial_stimulus = visual.TextStim(win, text = '',units = 'norm', height = .12)
    if trial["Congruency"] == "L_Con":
        trial_stimulus.text = "<<<<<"
    elif trial["Congruency"] == "R_Con":
        trial_stimulus.text = ">>>>>"
    elif trial["Congruency"] == "L_Incon":
        trial_stimulus.text = ">><>>"
    else:
        trial_stimulus.text = "<<><<"
    
    return trial_stimulus 

# Processes how the participant answered the relevant trial
def performance_processing(block, trial, rt, key_press, reward_size,response_deadline):

    #accuracy check  
    if rt > response_deadline:
        accuracy = 0
        
    else:
        if trial['CorAns'] == key_press[0]:
            accuracy = 1
            
        else: 
            accuracy = 0
            
    
    # giving the participant the reward they deserve
    if accuracy == 1 and trial["ScaleType"] == "Det":
        earned_reward = reward_size
    elif accuracy == 1 and trial["ScaleType"] == "Prob":
        earned_it = np.random.choice([True,False],p = [(reward_size/100),(1-(reward_size/100))])
        if earned_it == True:
            earned_reward = 100
        else:
            earned_reward = 0   
    else:
        earned_reward = 0
    
    if block == 0:
        feedback_text = visual.TextStim(win, text = "Blijf oefenen!")
        total_reward = 0
        total_accuracy = 0
    else:

        reward_counter.append(earned_reward)
        acc_counter.append(accuracy)
        total_accuracy = round((sum(acc_counter)/len(acc_counter))*100,1)
        total_reward = sum(reward_counter)

        if rt > response_deadline:
            feedback_text = visual.TextStim(win, text = "Te traag!")
        else:
            feedback_text = visual.TextStim(win, text = "+{0}".format(earned_reward))
        

    return feedback_text, total_reward, earned_reward, accuracy, total_accuracy

#adjusting response deadline relative to performance  

def update_deadline(acc_counter,response_deadline):
    
    lower_limit = 0.42  
    upper_limit = 0.82

    if lower_limit <= response_deadline <= upper_limit:
        if accuracy == 1:
            response_deadline = response_deadline - 0.01
        else:  
            response_deadline = response_deadline + 0.08
    else: 
        if response_deadline < lower_limit:
            response_deadline = lower_limit
        elif response_deadline > upper_limit:
            response_deadline = upper_limit
    return round(response_deadline,2)
    

#adjust instructions per block when needed
def instructions_per_block(c_b, block, total_reward):
    
    if block == 0:
            instructions.text = "Ga aan de slag met de oefenronde\n\nDruk de spatiebalk om te beginnen"
            block_completed.text = "Laten we beginnen met het echte experiment!\n\nDruk de spatiebalk om verder te gaan"   
    else: 
        if block%2 == c_b:
            instructions.text = "Voor elke reeks is er een bepaalde kans om 100 punten te verdienen na een juist antwoord\nEr verschijnt telkens een percentage in het blauw die toont wat die kans is\n\nDruk de spatiebalk om de ronde te beginnen!"
            
            if block == n_blocks:
                block_completed.text = "Dat was de laatste ronde ! \n\nDruk de spatiebalk om verder te gaan"
            else:
                block_completed.text = "Tot nu heb je al {0} Punten of {1} euro! \n\nDruk de spatiebalk om verder te gaan".format(total_reward,round((total_reward/16000),2))

        else:
            if block == n_blocks:
                block_completed.text = "Dat was de laatste ronde ! \n\nDruk de spatiebalk om verder te gaan"
            else:
                block_completed.text = "Tot nu heb je al {0} Punten of {1} euro! \n\nDruk de spatiebalk om verder te gaan".format(total_reward,round((total_reward/16000),2))
           
            instructions.text = "Voor elke reeks komt er een cijfer in het blauw dat aantoont hoeveel punten je precies kan verdienen als je een reeks correct beantwoordt\n\nDruk de spatiebalk om verder te gaan"

####################################################
############## THE EXPERIMENT LOOP #################
####################################################




## This line of code below will initiate the GUI for the participant to fill out
## as well as create the ExperimentHandler object and file location.
## The participants information is saved in the 'info' dictionary 
## and the ExperimentHandler object in 'thisExp'.
win.fullscr = False
thisExp ,info = directory_set()
win.fullscr = True




#Welcome message and explanation
experiment_init_instructions()

#Making sure the subjects have understood the instructions
do_they_get_it()

#counterbalancing between participants for blocked design
c_b = counterbalance(int(info['Participant number']))

total_reward = sum(reward_counter)

#blockloop
for  block in range(n_blocks):
    
    ##randomizing the trials
    trials = randomize(c_b, block)
    
    ##giving the instructions
    instructions_per_block(c_b, block,total_reward)
    instructions.draw()
    win.flip()
    wait_for_keypress()


    #trail loop !
    for trial in trials: 
        
        # initiate the reward description
        reward_size, reward_announcement, reward_size_text = create_reward_stimulus(trial)
        #reward_announcement.draw()
        reward_size_text.draw()
        win.flip()
        time.sleep(t_reward_announcement)
        
        ## Fixation cross
        fix_cross.draw()
        win.flip()
        time.sleep(t_fix_cross)
        
        ##Initializing a trial
        trial_stimulus = create_trial_stimulus(trial)
        event.clearEvents()
        trial_stimulus.draw()
        win.flip()

        experiment_timer.reset()

        ##wait for response + escape function
        response = event.waitKeys(keyList = [left_key,right_key,'escape'], maxWait = response_deadline)
        #get the reaction time
        rt = experiment_timer.getTime()
        experiment_times.append(rt)
        #logging a non-response
        if rt >= response_deadline:
            response = "None"
        #escape option
        if response[0] == 'escape':
            core.quit()
            win.close()      

        # Feedback based on conditions and performance
        feedback_text, total_reward, earned_reward, accuracy, total_accuracy = performance_processing(block, trial, rt, response, reward_size,response_deadline)
        # Updating response deadline relative to total accuracy
        response_deadline = update_deadline(accuracy,response_deadline)
        
        feedback_text.draw()
        win.flip()
        time.sleep(t_feedback)
        win.flip()
        time.sleep(t_blank_screen)

        ## logging the data onto the csv file
        trials.addData("Accurate Response",accuracy)
        trials.addData('response', response[0])
        trials.addData('RT',rt)
        trials.addData('Block',block)
        trials.addData('Reward Size', reward_size)
        trials.addData("Earned Reward", earned_reward)
        thisExp.nextEntry()
    
    instructions_per_block(c_b, block,total_reward)

    block_completed.draw()
    win.flip()
    wait_for_keypress()


thisExp.addData("total_reward",total_reward)
## Final Words

monetary_reward = round((total_reward/16000),2)

instructions.text = "Bedankt voor uw deelname. In totaal heb je {0} punten ofwel {1} euro!!\n Je antwoord was juist {2}% van de tijd".format(total_reward,monetary_reward,total_accuracy)
instructions.draw()
win.flip()
wait_for_keypress()
instructions.text = "Informeer de proefleider dat het experiment is afgerond"
instructions.draw()
win.flip()
wait_for_keypress()
win.close()
core.quit()
        




        




