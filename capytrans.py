#!/usr/bin/python3

def check_requirements():
    # Check the required python modules are installed
    import pkg_resources
    
    required = {'google-cloud-core', 'googleapis-common-protos', 'google-api-core', 'google-cloud-translate', 'google-auth', 'stopit'}
    
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed
    
    if missing:
        print("error: The following packages are required and are not installed; ")
        for i in range (len(missing)):
            print(list(missing)[i])
        print("For example, try;")
        print("'pip3 install stopit' for the stopit module.")
        print("'pip3 install google-cloud-translate==2.0.1' for the google modules.")
        exit()



def welcome():
    # Display the mighty capybara and general startup information
    print(r'''
                    yh+  :dho                                                       
             ``-:.s:+do`oh`                                                     
        .//:-`      h+  `d`                      `-/+ooooossssss/-              
    `/so:`   .sy/   /s/`+..--`            .:/+ooo+:-`          `-+yy+.          
  :ys-       :sy.            --::::::::://-.                        -sh+`       
.hs`                                                                   /ho`     
m: `                                                                     :h+    
m`.o`                                                                      /h.  
:s                                                                          `h: 
 :o/:-`                                                                      `d-
    `:+oosssso+/.                                                             .h
               `/+`                                                            m
                 `ss`                                                         -y
                   :d:                  .`                                   `y`
                    .hs`                 s                                  `h` 
                      -ss+.-             o-                                 h.  
                         .sos`           h.                                /:   
                          .s.y`         s/```.............-:/++:           ::   
                           `h+s        /+       ```..---:::-.///ho`         /.  
    ╔══════════════╗         .my/      -o                      ./+ohy.        y. 
    ║ capytrans.py ║          d/N`    `d`                         /syhy-      `h`
    ╚══════════════╝          ssd/    d/                            .ohdy.     o+
                             /dyo   +d                               +h.d.    ss
 Google Translate API CLI    /hy+   y-                               y+ /s    m/
                             hsm`   h                               +h  +o   /d 
                            shy` ..-+                           `//++.:+o   -d. 
                          /+hs+  +moo`                          -h+oNmN+.:+/++`  
                         `hd:dh+:./`                                `-          
    ''')
    print ("=" * 80)
    print("capytrans.py v" + version + " by " + author + ".")
    print ("Started on " + datetime.now().strftime("%Y-%m-%d") + " at " + datetime.now().strftime("%H:%M:%S") + " by user " + getpass.getuser() + ".")
    print ("Output File: " + output_file_path)
    print ("=" * 80)



def authenticate(keyfile):
    # Loads private key capytrans-aceced49eb5b.json to authenticate the environment.
    import os
    
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = keyfile



def translate_text(source, target, text):
    # Translates text into the target language.
    # Target must be an ISO 639-1 language code (https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
    import six
    from google.cloud import translate_v2 as translate
    
    translate_client = translate.Client()
    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")
    
    # Text can also be a sequence of strings, in which case this method will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target)
    return(result)



def print_output(text):
    # Takes a string and prints it to the terminal with a timestamp
    out_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\n' + text
    print(out_string)



if __name__ == "__main__":
    import argparse
    import time
    from datetime import datetime
    import getpass
    import sys
    import stopit
    
    version = "1.0"
    author = "DC 3353 David Barr"
    
    # The output file delimiter
    delimiter = "|"
    
    # After this many seconds, a timeout will be recorded
    max_response_time = 10
    
    # Call the function to check required python modules
    check_requirements()
    
    # Initialise the command line argument parser, with positional arguments of keyfile and input file
    # Optionally, the source and destination languages can be specified
    parser = argparse.ArgumentParser(description='A simple Google Translate API command line utility.')
    parser.add_argument('KEYFILE', action='store', 
    help="path to the Google Translate API .json keyfile.")
    parser.add_argument('INPUT', action='store', 
    help="the input text file to be translated.")
    parser.add_argument('-s', '--src_lang', action='store', 
    help="specify the source language in ISO 639-1 format, default if omitted is 'auto'.")
    parser.add_argument('-d', '--dst_lang', action='store', 
    help="specify the destination language in ISO 639-1 format, default if omitted is 'en'.")
    
    # Read the commands, and assign them to the correct variables
    args = parser.parse_args()
    # Currently it autdetects, unable to manually specify manual source language.
    source_lang = args.src_lang
    if args.dst_lang == None:
        dest_lang = 'en'
    else:
        dest_lang = args.dst_lang
    keyfile_path = args.KEYFILE
    input_file_path = args.INPUT    
    
    # Authenticate with the Google API by calling the function to set the environment variable
    authenticate(args.KEYFILE)
    
    # Create a file name for the output file
    start_time = datetime.now()
    output_file_path = start_time.strftime("%Y-%m-%d %H_%M_%S") + '.csv'
    
    # Open handles to the input and output files
    input_file = open(input_file_path, "r")
    output_file = open(output_file_path, 'w')
    
    # Write the header for the delimited output file
    output_file.write("INPUT STRING" + delimiter + "DETECTED LANGUAGE" + delimiter + "GOOGLE TRANSLATE OF INPUT STRING" + '\n')
    
    # Display the mighty capybara and version info
    welcome()
    
    # Initialise variables for the stats at the end including a list that will record detected languages, a line counter, and timeout counter
    detected_languages = []
    line_counter = 0
    error_counter = 0
    # The main loop, fear each line to translate in the file, strip line endings to prevent shenaningans
    for line in input_file:
        line = line.strip()
        # Use stopit to record the task state, as the API may hang on occasion
        with stopit.ThreadingTimeout(max_response_time) as to_ctx_mgr:
            assert to_ctx_mgr.state == to_ctx_mgr.EXECUTING
            # Call the translation function on the line
            result = translate_text(source_lang, dest_lang, line)
            # Output the results to standard out and file
            print_output(result["input"] + ' ---' + result["detectedSourceLanguage"] + '---> ' + result["translatedText"] + '\n')
            output_file.write(result["input"] + delimiter + result["detectedSourceLanguage"] + delimiter + result["translatedText"] + '\n')
            # Add the detected language ISO code to the list if its not in it
            if result["detectedSourceLanguage"] not in detected_languages:
                detected_languages.append(result["detectedSourceLanguage"])
            # Increment the line counter
            line_counter += 1
        # If the max_response_time was exceeded, increment the error coutner and output the error message to standard out and file
        if to_ctx_mgr.state == to_ctx_mgr.TIMED_OUT:
            print_output('error: Google API timeout' + '\n')
            output_file.write('error: Google API timeout' + '\n')
            error_counter += 1
    
    # We are done, close our files
    input_file.close()
    output_file.close()
    
    # Capture end time and calculate duration
    end_time = datetime.now()
    translation_duration = end_time.replace(microsecond=0) - start_time.replace(microsecond=0)
    
    # Print the footer information which contains file stats and a filename reminder
    print("=" * 80)
    print("All operations successfully completed.\n")
    print("Start time                 :", start_time.strftime("%Y-%m-%d %H:%M:%S"))
    print("End time                   :", end_time.strftime("%Y-%m-%d %H:%M:%S"))
    print("Time taken to translate    :", translation_duration)
    print("Total lines translated     :", line_counter)
    print("API timeouts detected      :", error_counter)
    print("Detected languages in file :", end=" ")
    for iso_code in detected_languages:
        print(iso_code, end=" ")
    print('\n')
    print("Check the contents of " + output_file_path + " for the translated results.")
    print("=" * 80)
