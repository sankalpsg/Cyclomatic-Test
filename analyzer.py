# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 22:37:06 2017

@author: Sankalp
"""
import json, requests, subprocess

def run():
    
    masterIP = input("Enter the IP of the manager: ")
    masterPort = input("Enter the port of the manager: ")
    countOfCommits = 0

    req = requests.get("http://{}:{}/repo".format(masterIP,masterPort), json={'status': False})
    json_str = json.loads(req.text)
    repoUrl = json_str['repo']
    subprocess.call(["bash", "slaveInitScript.sh", repoUrl]) # API to fetch the repo

    req = requests.get("http://{}:{}/repo".format(masterIP,masterPort), json={'status': True}) 
    commitsLeft = True
    while commitsLeft:
        
        # Master Commits
        req = requests.get("http://{}:{}/cyclomatic".format(masterIP,masterPort))
        json_str = json.loads(req.text)
        print(json_str)
        print("Received: {}".format(json_str['sha']))
        
        if json_str['sha'] == -2: 
            print("Commits Still Left")
        else:
            if json_str['sha'] == -1:
                print("All Commits Completed")
                break
            
            subprocess.call(["bash", "slaveCommit.sh", json_str['sha']])
            
            # Call radon on the python repository and store its output
            binRadonCCOutput = subprocess.check_output(["radon", "cc", "-s", "-a" , "SlaveData"])
            radonCCOutput = binRadonCCOutput.decode("utf-8") 
            print(radonCCOutput)
            
            avgCCstartPos = radonCCOutput.rfind("(")
            if radonCCOutput[avgCCstartPos+1:-2] == "":  
                print("NO RELEVANT FILES")
                req = requests.post("http://{}:{}/cyclomatic".format(masterIP,masterPort),
                                  json={'commitSha': json_str['sha'], 'complexity': -1})
            else:
                meanCC = float(radonCCOutput[avgCCstartPos+1:-2])  # Mean of Cyclomatic Complexity
                req = requests.post("http://{}:{}/cyclomatic".format(masterIP,masterPort),
                                  json={'commitSha': json_str['sha'], 'complexity': meanCC})
            countOfCommits += 1  # Incrementing Commit Count
    print("Total Number of Commits)".format(countOfCommits))

if __name__ == "__main__":
    run()