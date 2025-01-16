'''
From Christophe Pallier's (Christophe@pallier.org) 
lexdec_v3.py (https://github.com/chrplr/PCBS/blob/master/experiments/xpy_lexical_decision/lexdec_v3.py)
using the expyriment module.

Project: Single Word Processing (https://github.com/avalazem/Single-Word-Processing)
Author: Ali Al-Azem
Supervisor: Yair Lakretz

'''


import sys
import random
import pandas
from expyriment import design, control, stimuli
import os
from pydub import AudioSegment  # Import pydub for audio processing

# Constants
WORD_RESPONSE_KEY = 'f'
QUIT_KEY = 'q'
STIMULUS_DURATION = 200  # in milliseconds
SPEECH_WAIT_DURATION = 5000  # in milliseconds
WRITING_WAIT_DURATION = 10000  # in milliseconds

# Check for correct usage
if len(sys.argv) < 2:
    print("""Usage: [python] swp.py CSVFILE

where CSVFILE is a comma-separated file with columns:
    - `Word` (containing a word)
    - `Condition` (containing one of 12 conditions)
    - `Audio` (audio file name)
    """)
    sys.exit(1)

stim_file = sys.argv[1]  # Read second argument from command line

# Initialize the experiment
exp = design.Experiment(name="Single Word Processing", text_size=40)
control.initialize(exp)

# Prepare the stimuli
materials = pandas.read_csv(stim_file)
words = materials['Word'].tolist()
conditions = materials['Condition'].tolist()
audio_files = materials['Audio'].tolist()

# Create distinct runs
runs = {
    "word_covert_speech": [],
    "word_write": [],
    "audio_covert_speech": [],
    "audio_write": []
}

for word, condition, audio in zip(words, conditions, audio_files):
    runs["word_covert_speech"].append((word, condition, audio, 'word', 'Covert Speech'))
    runs["word_write"].append((word, condition, audio, 'word', 'write'))
    runs["audio_covert_speech"].append((word, condition, audio, 'audio', 'Covert Speech'))
    runs["audio_write"].append((word, condition, audio, 'audio', 'write'))

# Function to split runs into mini-runs
def split_into_mini_runs(trials, num_mini_runs):
    random.shuffle(trials)
    return [trials[i::num_mini_runs] for i in range(num_mini_runs)]

# Path to the audio files
audio_folder_path = r"C:\Users\ali_a\Desktop\Single_Word_Processing_Stage\Single_Word_Processing\Christophe_Stimulation\Stimuli\audio_files_wav"

# Shuffle the main runs
main_run_order = list(runs.keys())
random.shuffle(main_run_order)

# Path to instruction images
instruction_image_folder = r"C:\Users\ali_a\Desktop\Single_Word_Processing_Stage\Single_Word_Processing\Christophe_Stimulation\Images\Instructions"

# Start the experiment
control.start(skip_ready_screen=True)

# Display general instructions
instructions = stimuli.Picture(r"C:\Users\ali_a\Desktop\Single_Word_Processing_Stage\Single_Word_Processing\Christophe_Stimulation\Images\Instructions\instructions.png")
instructions.scale_to_fullscreen()
instructions.present()
exp.keyboard.wait_char(" ")


# Collect all mini-runs into a single list
all_mini_runs = []

for run_name in main_run_order:
    num_mini_runs = 4 if "write" in run_name else 2
    mini_runs = split_into_mini_runs(runs[run_name], num_mini_runs)
    all_mini_runs.extend([(run_name, mini_run) for mini_run in mini_runs])

# Shuffle all mini-runs while ensuring no repetition of the same run type
random.shuffle(all_mini_runs)

# Ensure no consecutive mini-runs of the same type
shuffled_mini_runs = [all_mini_runs.pop(0)]  # Start with the first mini-run
while all_mini_runs:
    next_run = all_mini_runs.pop(0)
    if shuffled_mini_runs[-1][0] == next_run[0]:  # Same run type as previous
        all_mini_runs.append(next_run)  # Push it to the end of the list
    else:
        shuffled_mini_runs.append(next_run)

# Present all mini-runs
for i, (run_name, mini_run) in enumerate(shuffled_mini_runs):
    # Display image-based instructions if available
    image_path = os.path.join(instruction_image_folder, f"{run_name}.png")
    if os.path.exists(image_path):
        instructions = stimuli.Picture(image_path)
        instructions.scale_to_fullscreen()
        instructions.present()
    else:
        fallback_text = f"Instructions for {run_name.replace('_', ' ').capitalize()}\nPress SPACE to begin."
        instruction_screen = stimuli.TextScreen(f"Mini-Run", fallback_text)
        instruction_screen.present()

    exp.keyboard.wait_char(" ")

    # Present each trial in the mini-run
    for word, condition, audio, stimulus_type, response_mode in mini_run:
        cue = stimuli.FixCross(size=(50, 50), line_width=4)
        cue.present()
        exp.clock.wait(500)  # Fixation duration (500 ms)

        if stimulus_type == "word":
            word_stimulus = stimuli.TextLine(word)
            word_stimulus.present()
            
            # Wait for STIMULUS_DURATION while checking for QUIT_KEY
            start_time = exp.clock.time
            while exp.clock.time - start_time < STIMULUS_DURATION:
                key = exp.keyboard.check()
                if key == QUIT_KEY:
                    control.end()
                    sys.exit()
                    
            # Clear cue/stimulus
            blank_screen = stimuli.BlankScreen()
            blank_screen.present()
            
        elif stimulus_type == "audio":
            audio_path = os.path.join(audio_folder_path, audio)
            audio_clip = AudioSegment.from_file(audio_path)
            audio_duration = len(audio_clip)

            audio_stimulus = stimuli.Audio(audio_path)
            audio_stimulus.play()
            exp.clock.wait(audio_duration)
            stimuli.BlankScreen().present()

        # Wait for participant response
        response_time = SPEECH_WAIT_DURATION if response_mode == "Covert Speech" else WRITING_WAIT_DURATION
        start_time = exp.clock.time
        key, rt = exp.keyboard.wait_char([WORD_RESPONSE_KEY, QUIT_KEY], duration=response_time)

        if key == QUIT_KEY:
            control.end()
            sys.exit()

        if key == WORD_RESPONSE_KEY:
            rt = exp.clock.time - start_time  # Record reaction time (USE IF WANT TO SKIP THROUGH!!)
            # exp.clock.wait(response_time - rt) # Record reaction time (USE FOR ACTUAL EXPERIMENT!!)

        # Save trial data
        exp.data.add([word, condition, audio, stimulus_type, response_mode, key, rt])

    # Break between mini-runs (skip for last mini-run)
    if i < len(shuffled_mini_runs) - 1:
        for remaining_seconds in range(30, 0, -1):
            break_message = stimuli.TextScreen(
                "Break",
                f"Take a 30-second break. Relax and prepare for the next part.\n\n"
                f"The next part will start automatically in {remaining_seconds} seconds."
            )
            break_message.present()
            exp.clock.wait(1000)  # Wait 1 second (1000 ms)


# Display thank you instructions
thank_you_message = stimuli.Picture(r"C:\Users\ali_a\Desktop\Single_Word_Processing_Stage\Single_Word_Processing\Christophe_Stimulation\Images\Instructions\thank_you.png")
thank_you_message.scale_to_fullscreen()
thank_you_message.present()
exp.keyboard.wait_char(" ")

control.end()
