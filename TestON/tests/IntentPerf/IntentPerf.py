#Class IntentPerf
#Measures latency regarding intent events
#CASE3: single intent add / rem latency
#CASE4: single intent reroute  latency
#CASE5: batch intent add latency
#CASE6: batch intent reroute latency
#NOTE:
# * each case is iterated numIter times. Then min/max/avg is calculated based on results.
#   If an iteration is omitted, it means unexpected results were found (such as negative
#   delta of timestamps or delta that is too large) 

#**********
#Google doc for test overview
#https://docs.google.com/a/onlab.us/presentation/d/1rnSDpAOm0IHv__U3PlwJiJuio3oYFWY7A17ZlWi5oTM/edit?usp=sharing
#**********


class IntentPerf:
    def __init__(self) :
        self.default = ''
#Test startup
    def CASE1(self,main) :  #Check to be sure ZK, Cass, and ONOS are up, then get ONOS version
        import time 
        main.log.report("Initial setup")
        main.step("Stop ONOS")
        main.ONOS1.stop()
        main.ONOS2.stop()
        main.ONOS3.stop()
        main.ONOS2.rest_stop()
        
        main.step("Start ONOS") 
        time.sleep(5)
        
        main.Zookeeper1.start()
        main.Zookeeper2.start()
        main.Zookeeper3.start()
        
        time.sleep(5)
        
        main.ONOS1.start()
        main.ONOS2.start()
        main.ONOS3.start()
        main.ONOS2.start_rest()
        
        time.sleep(3)
       
        main.ONOS1.handle.sendline("./onos.sh core start")
        main.ONOS2.handle.sendline("./onos.sh core start")
        main.ONOS3.handle.sendline("./onos.sh core start")

        test= main.ONOS2.rest_status()
        if test == main.FALSE:
            main.ONOS2.start_rest()

        main.ONOS1.get_version()
        main.log.info("Startup check Zookeeper1, and ONOS1 connections")
        main.step("Testing startup Zookeeper")   
        data =  main.Zookeeper1.isup()
        utilities.assert_equals(expect=main.TRUE,actual=data,
                onpass="Zookeeper is up!",
                onfail="Zookeeper is down...")
        
        time.sleep(20)

#******************************************
#CASE2
#Assign switches to controllers
#7 switches 
#s1, s2 = controller 1
#s3, s4, s5 = controller 2
#s6, s7 = controller3
#******************************************
    def CASE2(self, main):
        import time
        main.log.report("Assign switches to controllers")
        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS1_port = main.params['CTRL']['port1']
        ONOS2_port = main.params['CTRL']['port2']
        ONOS3_port = main.params['CTRL']['port3']
        assertion = main.TRUE

        for i in range(1,8):
            if i < 3:
                main.Mininet1.assign_sw_controller(sw=str(i),
                        ip1=ONOS1_ip,port1=ONOS1_port)
                time.sleep(5) 
            elif i < 6 and i > 2:
                main.Mininet1.assign_sw_controller(sw=str(i),
                        ip1=ONOS2_ip,port1=ONOS2_port)
                time.sleep(5)
            elif i < 8 and i > 5:
                main.Mininet1.assign_sw_controller(sw=str(i),
                        ip1=ONOS3_ip,port1=ONOS3_port)
                time.sleep(5)
        for j in range(1,8):
            result = main.Mininet1.get_sw_controller(sw=str(j))  
            if result == main.FALSE:
                assertion = main.FALSE
                main.log.info("Switch "+str(j)+" not assigned")
        utilities.assert_equals(expect=main.TRUE,actual=assertion,
                onpass="Switches assigned successfully",
                onfail="Switches NOT assigned")

#***************************************** 
#CASE3
#Add intent to ONOS 1 and obtain metrics
#via REST call        
#***************************************** 
    def CASE3(self, main):
        import requests
        import json
        import time
        import os
 
        main.log.report("Single Intent add / delete latency") 
        
        #Intent generate related variables
        intent_id = main.params['INTENTS']['intent_id']
        intent_id2 = main.params['INTENTS']['intent_id2'] 
        intent_type = main.params['INTENTS']['intent_type']
        
        #Database related variables
        db_script = main.params['INTENTS']['databaseScript']
        table_name = main.params['INTENTS']['tableName']
        postToDB = main.params['INTENTS']['postToDB']
        
        #REST call related variables
        url = main.params['INTENTS']['url_new']
        url_add = main.params['INTENTS']['urlAddIntent'] 
        url_rem = main.params['INTENTS']['urlRemIntent']
        intent_ip = main.params['INTENTREST']['intentIP']
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        
        #Other variables 
        srcSwitch = main.params['INTENTS']['srcSwitch']
        srcPort = int(main.params['INTENTS']['srcPort'])
        srcMac = main.params['INTENTS']['srcMac']
        dstSwitch = main.params['INTENTS']['dstSwitch']
        dstPort = int(main.params['INTENTS']['dstPort'])
        dstMac = main.params['INTENTS']['dstMac']
        numIter = main.params['INTENTS']['numIter']
        host_ip = main.params['INTENTS']['hostIP'] 
        assertion = main.TRUE

        #Log related variables
        intentAddThreshold = main.params['LOG']['threshold']['intent_add1']
        intentRemThreshold = main.params['LOG']['threshold']['intent_rem1']
        logName1 = main.params['LOG']['logNameONOS1']
        logDir = main.params['LOG']['logDir']

        #We use list to store multiple iterations of latency outputs
        intent_add_lat_list = []
        intent_rem_lat_list = []

        #NOTE: REST call may change in the future
        for i in range(0, int(numIter)):
            add_result = main.ONOS1.add_intent(intent_id = intent_id, 
                    src_dpid = srcSwitch, dst_dpid = dstSwitch,
                    src_mac = srcMac, dst_mac = dstMac, intentIP = intent_ip)
            #Verify intent instsallation
            utilities.assert_equals(expect=main.TRUE,actual=add_result,
                    onpass="Intent Add Successful",
                    onfail="Intent Add NOT successful...") 
            time.sleep(5)
           
            #Get json object for parsing add timestamp
            json_obj = main.ONOS1.get_json(url_add) 
            intent_lat_add = main.ONOS1.get_single_intent_latency(json_obj)
            
            main.log.info("Intent Add Latency of Intent ID "+
                    intent_id+": " + str(intent_lat_add) + " ms")
            
            #Add result to list 
            intent_add_lat_list.append(intent_lat_add)

            #Delete intents. NOTE: The following method deletes only the
            #  specified intent id
            intent_del = requests.delete(url+"/"+intent_id)
            time.sleep(5)
            
            #Get json object for parsing remove timestamp
            json_obj = main.ONOS1.get_json(url_rem)
            intent_lat_rem = main.ONOS1.get_single_intent_latency(json_obj)
            main.log.info("Intent Rem Latency of Intent ID "+
                    intent_id+": " + str(intent_lat_rem) + "ms")
            intent_rem_lat_list.append(intent_lat_rem)

            time.sleep(2)

        #NOTE: Omit first 2 iterations to account for ONOS 'warmup' time
        if len(intent_add_lat_list) > 2 and len(intent_rem_lat_list) > 2:
            intent_add_lat_list = intent_add_lat_list[2:]
            intent_rem_lat_list = intent_rem_lat_list[2:]
        else:
            main.log.report("Warning: Less than 3 iterations have been calculated")

        min_lat_add = str(min(intent_add_lat_list))
        max_lat_add = str(max(intent_add_lat_list))
        avg_lat_add = str(sum(intent_add_lat_list) / len(intent_add_lat_list))

        min_lat_rem = str(min(intent_rem_lat_list))
        max_lat_rem = str(max(intent_rem_lat_list))
        avg_lat_rem = str(sum(intent_rem_lat_list) / len(intent_rem_lat_list))
                
        #If avg add lat exceeds threshold, trigger onos log copy
        if avg_lat_add > int(intentAddThreshold):
            log_result_add = main.ONOS1.tailLog(log_directory = logDir, 
                    log_name = logName1, tail_length = 50)
                
        if avg_lat_rem > int(intentRemThreshold):
            log_result_rem = main.ONOS1.tailLog(log_directory = logDir,
                    log_name = logName1, tail_length = 50)


        if int(avg_lat_add) > 0 and int(avg_lat_rem) > 0:
            if int(avg_lat_add) < 100000 and int(avg_lat_rem) < 100000:
                omit_iter_add = int(numIter) - int(len(intent_add_lat_list))
                omit_iter_rem = int(numIter) - int(len(intent_rem_lat_list))
                
                main.log.report("Intent add latency Min: "+
                        min_lat_add+" ms    Max: "+ 
                        max_lat_add + "ms    Avg: "+
                        avg_lat_add+ " ms")
                main.log.report("Iterations omitted/total: "+
                        str(omit_iter_add)+"/"+str(numIter)) 
                #NOTE: os.system runs a command on current (TestON) machine.
                #Hence, place the db_script in a TestON location 
                if postToDB == 'on':
                    os.system(db_script + " --name='1 intent add' --minimum='"+
                        min_lat_add+"' --maximum='"+max_lat_add+
                        "' --average='"+avg_lat_add+"' "+ "--table='"+table_name+"'")
                else:
                    main.log.report("Results were not posted to the database")
                
                main.log.report("Intent rem latency Min: "+min_lat_rem+
                        " ms    Max: "+max_lat_rem+" ms    Avg: "+avg_lat_rem+ " ms")
                main.log.report("Iterations omitted/total: "+
                        str(omit_iter_rem)+"/"+str(numIter)) 
        #If length of the list is less than 1, which means no successful
        #calculations of intents have occured, assertion is false. 
        if len(avg_lat_add) < 1 or len(avg_lat_rem) < 1:
            assertion = main.FALSE

        utilities.assert_equals(expect=main.TRUE,actual=assertion,
                onpass="Single intent add / rem successful",
                onfail="Single intent add / rem NOT successful")

#***************************************
#CASE4
#cut link between s3 - s5 
#measure reroute latency 
#tshark measures t0 on ONOS2
#REST call measures t1 
#***************************************
    def CASE4(self,main):
        import requests
        import json
        import time 
        import subprocess
        import os

        main.log.report("Single Intent reroute latency")
       
        #REST call url related variables
        url = main.params['INTENTS']['url_new']
        url_add_end = main.params['INTENTS']['urlAddIntentEnd']
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        
        #Intent related variables
        intent_id = main.params['INTENTS']['intent_id']
        intent_id2 = "1"+intent_id
        intent_type = main.params['INTENTS']['intent_type']
        srcSwitch = main.params['INTENTS']['srcSwitch2']
        srcPort = int(main.params['INTENTS']['srcPort'])
        srcMac = main.params['INTENTS']['srcMac2']
        dstSwitch = main.params['INTENTS']['dstSwitch2']
        dstPort = int(main.params['INTENTS']['dstPort'])
        dstMac = main.params['INTENTS']['dstMac2']
        intent_ip = main.params['INTENTREST']['intentIP']

        #Result posting to database related variables
        db_script = main.params['INTENTS']['databaseScript']
        postToDB = main.params['INTENTS']['postToDB']

        #Other test variables
        ONOS2_ip = main.params['CTRL']['ip2']
        numIter = main.params['INTENTS']['numIter']
        table_name = main.params['INTENTS']['tableName']
        tshark_output = "/tmp/tshark_of_port.txt"
        assertion = ""
        latency = []
        
        #Log related variables
        intentRerouteThreshold = main.params['LOG']['threshold']['intent_reroute1']
        logName1 = main.params['LOG']['logNameONOS1']
        logDir = main.params['LOG']['logDir']

        main.step("Removing any old intents")
        requests.delete(url)
        time.sleep(5)

        for i in range(0,int(numIter)): 

            #Add intents in both directions (flip dst / src)
            main.ONOS1.add_intent(intent_id = intent_id,
                    src_dpid = srcSwitch, dst_dpid = dstSwitch,
                    src_mac = srcMac, dst_mac = dstMac, 
                    intentIP = intent_ip)
            main.ONOS1.add_intent(intent_id = intent_id2, 
                    src_dpid = dstSwitch, dst_dpid = srcSwitch,
                    src_mac = dstMac, dst_mac = srcMac,
                    intentIP = intent_ip)

            main.step("Checking flow")
            result = main.Mininet1.pingHost(src="h1",target="h7") 

            time.sleep(5) 
            main.step("Starting tshark open flow capture") 
            main.ONOS2.tshark_grep("OFP 130", tshark_output)
            time.sleep(10) 

            main.step("Bring down interface s3-eth2")
            main.Mininet2.handle.sendline("sudo ifconfig s3-eth2 down")
            time.sleep(5)

            main.step("Call rest to obtain timestamp")
            json_obj = main.ONOS2.get_json(url_add_end) 

            time.sleep(20)
            main.ONOS2.stop_tshark()
            main.step("Checking flow between h1 and h7")
            result = main.Mininet1.pingHost(src="h1",target="h7") 
             
            #Read ONOS tshark_of_port file and get first line
            ssh = subprocess.Popen(['ssh', 'admin@'+ONOS2_ip,
                'cat', tshark_output],stdout=subprocess.PIPE)
            text = ssh.stdout.readline()
            obj = text.split(" ")
            if len(text) > 0:
                timestamp = int(float(obj[1])*1000)
                port_down_time_ms = timestamp
            else:
                main.log.info("Unexpected result from tshark output")
                port_down_time_ms = 0
 
            #Parse json object to obtain timestamp
            end_time = json_obj['gauges'][0]['gauge']['value'] 
            reroute_latency = int(end_time) - int(port_down_time_ms)
          
            #NOTE: alter threshold as needed
            if(reroute_latency > 0 and reroute_latency < 100000):
                 main.log.info("Intent Reroute Latency: "+str(reroute_latency)+" ms")
                 latency.append(int(reroute_latency)) 
            else:
                 main.log.info("Unexpected results for Reroute Latency."+
                         " Omitting iteration "+str(i))
                 main.log.info("Latency calculation returned: "+str(reroute_latency))
 
            time.sleep(10)

            main.step("Bringing interface up")
            main.Mininet2.handle.sendline("sudo ifconfig s3-eth2 up")
            time.sleep(10)

            main.step("Removing all intents")
            intent_del = requests.delete(url)
            time.sleep(10)
        #END LOOP
        
        if(latency):
            #NOTE: Omit first 2 iterations to account for ONOS 'warmup' period
            if len(latency) > 2:
                latency = latency[2:]
            else:
                main.log.report("Warning: Less than 3 iterations calculated")

            main.step("Calculating latency min,max,avg")
            min_lat = str(min(latency))
            max_lat = str(max(latency))
            avg_lat = str(sum(latency) / len(latency))
            omit_iter = int(numIter) - int(len(latency))
            
            if int(avg_lat) > int(intentRerouteThreshold):
                main.log.info("Average latency exceeded threshold of "+
                        str(intentRerouteThreshold))
                main.log.info("Getting onos-log for further investigation")
                main.log.info("Log fetched: "+logDir+logName1)
                log_result_reroute = main.ONOS1.tailLog(log_directory = logDir,
                        log_name = logName1, tail_length = 50)
                 

            if int(avg_lat) > 0 and int(avg_lat) < 100000:
                main.log.report("Single Intent Reroute latency Min: "+
                        min_lat+" ms    Max: "+max_lat+
                        " ms    Avg: "+avg_lat+" ms")
                main.log.report("Iterations omitted/total: "+
                        str(omit_iter)+"/"+str(numIter))
                if postToDB == 'on':
                    os.system(db_script + " --name='1 intent reroute' --minimum='"+
                        min_lat+"' --maximum='"+max_lat+"' --average='"+avg_lat+
                        "' " + "--table='"+table_name+"'")
                else:
                    main.log.report("Results have not been posted to the database")
                    
                assertion = main.TRUE
            else:
                assertion = main.FALSE
        else:
            #No latency was calculated / appended
            assertion = main.FALSE
        
        utilities.assert_equals(expect=main.TRUE,actual=assertion,
                onpass="Single Intent Reroute Successful",
                onfail="Single Intent Reroute NOT successful...") 

        
#********************************** 
#CASE5
#Intent Batch Installation Latency
#create a specified number of intents via dynamicIntent function
#This function is hardcoded to add intents on s1 to s7
#Measure latency of intent add via rest calls
#**********************************

    def CASE5(self,main):
        import time
        import os
        main.log.report("Adding batch of intents to calculate latency")
       
        #Intent related variables
        numflows = main.params['INTENTS']['numFlows']
        intaddr = main.params['INTENTS']['url_new']
        url_add = main.params['INTENTS']['urlAddIntent']
        numIter = main.params['INTENTS']['numIter']
        intent_ip = main.params['INTENTREST']['intentIP']
        
        #DB related variables
        db_script = main.params['INTENTS']['databaseScript']
        postToDB = main.params['INTENTS']['postToDB']
        table_name = main.params['INTENTS']['tableName']
        
        #Other variables
        assertion = main.TRUE
        latency = []
        
        #Log related variables
        intentAddThreshold = main.params['LOG']['threshold']['intent_add1']
        logName1 = main.params['LOG']['logNameONOS1']
        logDir = main.params['LOG']['logDir']

        for i in range(0,int(numIter)):
            result = main.ONOS1.dynamicIntent(NUMFLOWS = numflows,
                    INTADDR = intaddr, OPTION = "ADD")

            time.sleep(5)
            num_flows1 = main.Mininet1.getSwitchFlowCount("s1")
            num_flows2 = main.Mininet1.getSwitchFlowCount("s7")

            if(num_flows1 != numflows): 
                main.log.info("Bidirectional flow counts do not match...")
                main.log.info("Flow count on s1 returned: " + str(num_flows1))
                main.log.info("Flow count on s7 returned: " + str(num_flows2))

            json_obj = main.ONOS1.get_json(url_add) 
            intent_lat_add = main.ONOS1.get_single_intent_latency(json_obj)
            if(intent_lat_add > 0):
                main.log.info("Intent Add Batch latency: " + str(intent_lat_add) + " ms")
                latency.append(intent_lat_add)       
            else:
                main.log.info("Intent Add Batch calculation returned unexpected results")
                main.log.info("Omitting iteration "+numIter)   
    
            result = main.ONOS1.dynamicIntent(INTADDR = intaddr, OPTION = "REM")
            utilities.assert_equals(expect=main.TRUE,actual=result,
                    onpass="Intent removal successful",
                    onfail="Intent removal NOT successful...") 

            time.sleep(3) 
 
        if(latency):
            #Omit the first 2 iterations to account for ONOS warmup period
            if len(latency) > 2:
                latency = latency[2:]
            else:
                main.log.report("Warning: less than 3 iterations calculated")
            min_lat = str(min(latency))
            max_lat = str(max(latency))
            avg_lat = str(sum(latency) / len(latency))
            omit_iter = int(numIter) - int(len(latency))

            if int(avg_lat) > 0 and int(avg_lat) < 100000:
                main.log.report("Intent Batch Latency ("+numflows+" intents) Min: "+
                        min_lat + " ms    Max: "+max_lat+" ms    Avg: "+avg_lat+" ms" )
                main.log.report("Iterations omitted/total: "+str(omit_iter)+"/"+str(numIter))
                
                if postToDB == 'on':
                    os.system(db_script + " --name='1000 intents add' --minimum='"+min_lat+
                        "' --maximum='"+max_lat+"' --average='"+avg_lat+"' "+ "--table='"+table_name+"'")
                else:
                    main.log.report("Results have not been posted to the database")
            else:
                assertion = main.FALSE
        else:
            assertion = main.FALSE

        utilities.assert_equals(expect=main.TRUE,actual=assertion,
                onpass="Intent Batch Latency Calculation successful",
                onfail="Intent Batch Latency Calculation unsuccessful")


#********************************
#CASE6
#Intent Batch Reroute Latency
#Add batch of intents via dynamicIntent function
#obtain tshark timestamp value from ONOS2
#obtain rest timestamp value and get delta
#********************************
    def CASE6(self, main):
        import requests
        import json
        import time
        import subprocess
       
        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']

        #Intent related variables
        numflows = main.params['INTENTS']['numFlows']
        intaddr = main.params['INTENTS']['url_new']
        numIter = main.params['INTENTS']['numIter']
        url_add_end = main.params['INTENTS']['urlAddIntentEnd']
        intentIp = main.params['INTENTREST']['intentIP']
        
        #Database related variables
        db_script = main.params['INTENTS']['databaseScript']
        postToDB = main.params['INTENTS']['postToDB']
        table_name = main.params['INTENTS']['tableName']
        
        #Log related variables
        intentAddThreshold = main.params['LOG']['threshold']['intent_add1']
        logName1 = main.params['LOG']['logNameONOS1']
        logName2 = main.params['LOG']['logNameONOS2']
        logDir = main.params['LOG']['logDir']
        
        #Other variables 
        tshark_port_batch = "/tmp/tshark_of_port_batch.txt"
        assertion = main.TRUE

        main.log.report("Calculating batch reroute latency")

        end_time_temp = ""        
        latency = []
	
        main.step("Removing any old intents before adding")
        intent_del = requests.delete(intaddr)
        time.sleep(5)

        for i in range(0, int(numIter)):
            main.step("Adding "+numflows+" intents")
            result = main.ONOS1.dynamicIntent(NUMFLOWS = numflows, 
                    INTADDR = intaddr, OPTION = "ADD")
            utilities.assert_equals(expect=main.TRUE,actual=result,
                    onpass="Batch installation successful",
                    onfail="Batch installation NOT successful...")

            time.sleep(10)
            num_flows1 = main.Mininet1.getSwitchFlowCount("s1")
            num_flows2 = main.Mininet1.getSwitchFlowCount("s7")

            if(num_flows1 != numflows):
                main.log.info("Flow count on s1 and s7 do not match (expected same count)")
                main.log.info("Flow count on s1 returned: " + str(num_flows1))
                main.log.info("Flow count on s7 returned: " + str(num_flows2))

            main.step("Starting wireshark")
            main.ONOS2.tshark_grep("OFP 130", tshark_port_batch)
            time.sleep(10)            

            main.step("Bringing interface down") 
            main.Mininet2.handle.sendline("sudo ifconfig s3-eth2 down")  
            time.sleep(10)
            main.ONOS2.stop_tshark()

            main.step("Getting timestamp from REST")
            json_obj = main.ONOS2.get_json(url_add_end)
            end_time = json_obj['gauges'][0]['gauge']['value']

            ssh = subprocess.Popen(['ssh', 'admin@'+ONOS2_ip, 'cat', 
                tshark_port_batch],stdout=subprocess.PIPE)
            
            text = ssh.stdout.readline()
            obj = text.split(" ")
            
            #Only calculate timestamp if text exists. 
            if text:
                timestamp = int(float(obj[1])*1000)
            #Making timestamp 0 will make delta exceed the threshold below, throwing an omit
            else:
                timestamp = 0
            delta = int(end_time) - int(timestamp)
           
            #NOTE: Modify threshold for what is reasonable 
            if delta > 0 and delta < 1000000:
                main.log.info("Latency of reroute: "+str(delta)+" ms") 
                latency.append(int(delta))
            else:
                main.log.info("Unexpected result from latency calculation. Omitting iteration "+str(i))
                main.log.info("Calculation result: "+str(delta))
 
            time.sleep(5)
            main.step("Removing intents")
            intent_del = requests.delete(intaddr)            
            time.sleep(5) 

            main.step("Bringing interface up") 
            main.Mininet2.handle.sendline("sudo ifconfig s3-eth2 up")
            time.sleep(10)

        if latency:
            main.step("Calculate latency max, min, average")
           
            #Omit the first two iterations to account for ONOS warmup time
            if len(latency) > 2:
                latency = latency[2:]
            else:
                main.log.report("Warning: less than 3 iterations have been calculated")
            
            max_lat = str(max(latency))
            min_lat = str(min(latency))
            avg_lat = str(sum(latency) / len(latency))
            omit_iter = int(numIter) - int(len(latency))
 
            if int(avg_lat) > 0 and int(avg_lat) < 100000: 
                main.log.report("Intent Batch Reroute Latency ("+numflows+" Intents) Min: "+
                                 min_lat+" ms    Max: "+max_lat+" ms    Avg: "+avg_lat+" ms")
                main.log.report("Iterations omitted/total: "+str(omit_iter)+"/"+str(numIter))
               
                if postToDB == 'on':
                    os.system(db_script + " --name='1000 intents reroute' --minimum='"+min_lat+"' --maximum='"+max_lat+
                                  "' --average='"+avg_lat+"' "+ "--table='"+table_name+"'")
                else:
                    main.log.report("Results have not been posted to the database")
            else:
                assertion = main.FALSE
        else:
            assertion = main.FALSE
        utilities.assert_equals(expect=main.TRUE,actual=assertion,
                onpass="Batch Reroute Latency Calculations Successful",
                onfail="Batch Reroute Latency Calculations NOT successful")

#**********
#END SCRIPT
#andrew@onlab.us
#**********
