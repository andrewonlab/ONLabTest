
class JamesTest :



    def __init__(self) :
        self.default = ''

#        def print_hello_world(self,main):
#            print("hello world")
#*****************************************************************************************************************************************************************************************
#Test startup
#Tests the startup of Zookeeper1, RamCloud1, and ONOS1 to be certain that all started up successfully
    def CASE1(self,main) :  #Check to be sure ZK, Cass, and ONOS are up, then get ONOS version
        main.case("Initial setup")
        main.step("Stop ONOS")
        import time
        main.ONOS1.stop_all()
        main.ONOS2.stop_all()
        main.ONOS3.stop_all()
#        main.print_hello_world()
        main.ONOS4.stop_all()
        main.ONOS2.stop_rest()
        main.ONOS1.handle.sendline("cp ~/onos.properties.proactive ~/ONOS/conf/onos.properties")
        main.ONOS2.handle.sendline("cp ~/onos.properties.proactive ~/ONOS/conf/onos.properties")
        main.ONOS3.handle.sendline("cp ~/onos.properties.proactive ~/ONOS/conf/onos.properties")
        main.ONOS4.handle.sendline("cp ~/onos.properties.proactive ~/ONOS/conf/onos.properties")        
        main.step("Start tcpdump on mn")
#        main.Mininet2.start_tcpdump(main.params['tcpdump']['filename'], intf = main.params['tcpdump']['intf'], port = main.params['tcpdump']['port'])
        main.step("Start ONOS")
        main.Zookeeper1.start()
        main.Zookeeper2.start()
        main.Zookeeper3.start()
        main.Zookeeper4.start()
        time.sleep(1)
        main.RamCloud1.del_db()
        main.RamCloud2.del_db()
        main.RamCloud3.del_db()
        main.RamCloud4.del_db()
        main.log.report("Pulling latest code from github to all nodes")
        for i in range(2):
            uptodate = main.ONOS1.git_pull()
            main.ONOS2.git_pull()
            main.ONOS3.git_pull()
            main.ONOS4.git_pull()
            ver1 = main.ONOS1.get_version()
            ver2 = main.ONOS4.get_version()
            if ver1==ver2:
                break
            elif i==1:
                main.ONOS2.git_pull("ONOS1 master")
                main.ONOS3.git_pull("ONOS1 master")
                main.ONOS4.git_pull("ONOS1 master")
        if uptodate==0:
       # if 1:
            main.ONOS1.git_compile()
            main.ONOS2.git_compile()
            main.ONOS3.git_compile()
            main.ONOS4.git_compile()
        main.ONOS1.print_version()    
        main.ONOS1.start_all()
        main.ONOS2.start_all()
        main.ONOS3.start_all()
        main.ONOS4.start_all()
        main.ONOS2.start_rest()
        test= main.ONOS2.rest_status()
        if test == main.FALSE:
            main.ONOS1.start_rest()
        main.ONOS1.get_version()
        main.log.report("Startup check Zookeeper1, RamCloud1, and ONOS1 connections")
        main.step("Testing startup Zookeeper")   
        data =  main.Zookeeper1.isup()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Zookeeper is up!",onfail="Zookeeper is down...")
        main.step("Testing startup RamCloud")   
        data =  main.RamCloud1.status_serv() and main.RamCloud2.status_serv() and main.RamCloud3.status_serv() and main.RamCloud4.status_serv()
        if data == main.FALSE:
            main.RamCloud1.stop_coor()
            main.RamCloud1.stop_serv()
            main.RamCloud2.stop_serv()
            main.RamCloud3.stop_serv()
            main.RamCloud4.stop_serv()

            time.sleep(5)
            main.RamCloud1.start_coor()
            main.RamCloud1.start_serv()
            main.RamCloud2.start_serv()
            main.RamCloud3.start_serv()
            main.RamCloud4.start_serv()
            time.sleep(5)
            data =  main.RamCloud1.status_serv() and main.RamCloud2.status_serv() and main.RamCloud3.status_serv() and main.RamCloud4.status_serv()
            

        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="RamCloud is up!",onfail="RamCloud is down...")
        main.step("Testing startup ONOS")   
        data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup() and main.ONOS4.isup()
        for i in range(3):
            if data == main.FALSE: 
                #main.log.report("Something is funny... restarting ONOS")
                #main.ONOS1.stop()
                time.sleep(3)
                #main.ONOS1.start()
                #time.sleep(5) 
                data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup() and main.ONOS4.isup()
            else:
                break
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="ONOS is up and running!",onfail="ONOS didn't start...")
        time.sleep(20)
           
#**********************************************************************************************************************************************************************************************
#Assign Controllers
#This test first checks the ip of a mininet host, to be certain that the mininet exists(Host is defined in Params as <CASE1><destination>).
#Then the program assignes each ONOS instance a single controller to a switch(To be the initial master), then assigns all controllers.
#NOTE: The reason why all four controllers are assigned although one was already assigned as the master is due to the 'ovs-vsctl set-controller' command erases all present controllers if
#      the controllers already assigned to the switch are not specified.

    def CASE2(self,main) :    #Make sure mininet exists, then assign controllers to switches
        import time
        main.log.report("Check if mininet started properly, then assign controllers ONOS 1,2,3 and 4")
        main.case("Checking if one MN host exists")
        main.step("Host IP Checking using checkIP")
        result = main.Mininet1.checkIP(main.params['CASE1']['destination'])
        main.step("Verifying the result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Host IP address configured",onfail="Host IP address not configured")
        main.step("assigning ONOS controllers to switches")
        for i in range(25): 
            if i < 3:
                j=i+1
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
                time.sleep(1)
                main.Mininet1.assign_sw_controller(sw=str(j),count=4,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'])
            elif i >= 3 and i < 5:
                j=i+1
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip2'],port1=main.params['CTRL']['port2'])
                time.sleep(1)
                main.Mininet1.assign_sw_controller(sw=str(j),count=4,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'])
            elif i >= 5 and i < 15:
                j=i+1
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip3'],port1=main.params['CTRL']['port3'])
                time.sleep(1)
                main.Mininet1.assign_sw_controller(sw=str(j),count=4,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'])
            else:
                j=i+16
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip4'],port1=main.params['CTRL']['port4'])
                time.sleep(2)
                main.Mininet1.assign_sw_controller(sw=str(j),count=4,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'])
        main.Mininet1.get_sw_controller("s1")       
        time.sleep(10)
 
# **********************************************************************************************************************************************************************************************
#Add Flows
#Deletes any remnant flows from any previous test, add flows from the file labeled <FLOWDEF>, then runs the check flow test
#NOTE: THE FLOWDEF FILE MUST BE PRESENT ON TESTON VM!!! TestON will copy the file from its home machine into /tmp/flowtmp on the machine the ONOS instance is present on

    def CASE3(self,main) :    #Delete any remnant flows, then add flows, and time how long it takes flow tables to update
        main.log.report("Delete any flows from previous tests, then add flows from FLOWDEF file, then wait for switch flow tables to update")
        import time
        main.case("Taking care of these flows!") 
        main.step("Cleaning out any leftover flows...")
        #main.ONOS1.delete_flow("all")
        strtTime = time.time()
        main.ONOS1.rm_intents()
        print("world")
        main.ONOS1.add_intents()
        time.sleep(2)
        main.ONOS1.add_intents()
        print("hello")
       # main.ONOS1.add_flow(main.params['FLOWDEF']['testONip'],main.params['FLOWDEF']['user'],main.params['FLOWDEF']['password'],main.params['FLOWDEF']['flowDef'])
        main.case("Checking flows")
       
        count = 1
        i = 6
        while i < 16 :
            main.log.info("\n\t\t\t\th"+str(i)+" IS PINGING h"+str(i+25) )
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+25))
            if ping == main.FALSE and count < 9:
                count = count + 1
                i = 6
                main.log.info("Ping failed, making attempt number "+str(count)+" in 2 seconds")
                time.sleep(2)
            elif ping == main.FALSE and count ==9:
                main.log.error("Ping test failed")
                i = 17
                result = main.FALSE
            elif ping == main.TRUE:
                i = i + 1
                result = main.TRUE
        endTime = time.time()
        if result == main.TRUE:
            main.log.report("\tTime to add flows: "+str(round(endTime-strtTime,2))+" seconds")
        else:
            main.log.report("\tFlows failed check")

        result2 = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        main.step("Verifying the result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Flow check PASS",onfail="Flow check FAIL")

#**********************************************************************************************************************************************************************************************
#This test case removes Controllers 2,3, and 4 then performs a ping test.
#The assign controller is used because the ovs-vsctl module deletes all current controllers when a new controller is assigned.
#The ping test performs single pings on hosts from opposite sides of the topology. If one ping fails, the test waits 5 seconds before trying again.
#If the ping test fails 6 times, then the test case will return false
    def CASE41(self,main) :
        main.log.report("Testing Removal")
        time.sleep(10)
        main.ONOS2.stop()
        time.sleep(10)
        main.ONOS3.stop()
        time.sleep(10)
        main.ONOS4.stop()
        time.sleep(15)
        strtTime = time.time() 
        result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        for i in range(10):
            if result == main.FALSE:
                time.sleep(5)
                result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
            else:
                break

        count = 1
        i = 6
        while i < 16 :
            main.log.info("\n\t\t\t\th"+str(i)+" IS PINGING h"+str(i+25) )
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+25))
            if ping == main.FALSE and count < 6:
                count = count + 1
                i = 6
                main.log.info("Ping failed, making attempt number "+str(count)+" in 2 seconds")
                time.sleep(2)
            elif ping == main.FALSE and count ==6:
                main.log.error("Ping test failed")
                i = 17
                result = main.FALSE
            elif ping == main.TRUE:
                i = i + 1
                result = main.TRUE
        endTime = time.time() 
        if result == main.TRUE:
            main.log.report("\tTime to complete ping test: "+str(round(endTime-strtTime,2))+" seconds")
        else:
            main.log.report("\tPING TEST FAIL")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="NO PACKET LOSS, HOST IS REACHABLE",onfail="PACKET LOST, HOST IS NOT REACHABLE")
        time.sleep(10)
        main.ONOS2.start() 
        main.ONOS3.start()
        main.ONOS4.start() 
        time.sleep(20)


    def CASE4(self,main) :
        main.log.report("Remove ONOS 2,3,4 then ping until all hosts are reachable or fail after 6 attempts")
        import time
        for i in range(25):
            if i < 15:
                j=i+1
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])  #Assigning a single controller removes all other controllers
            else:
                j=i+16
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
      
        strtTime = time.time() 
        result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        for i in range(10):
            if result == main.FALSE:
                time.sleep(5)
                result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
            else:
                break

        count = 1
        i = 6
        while i < 16 :
            main.log.info("\n\t\t\t\th"+str(i)+" IS PINGING h"+str(i+25) )
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+25))
            if ping == main.FALSE and count < 6:
                count = count + 1
                i = 6
                main.log.info("Ping failed, making attempt number "+str(count)+" in 2 seconds")
                time.sleep(2)
            elif ping == main.FALSE and count ==6:
                main.log.error("Ping test failed")
                i = 17
                result = main.FALSE
            elif ping == main.TRUE:
                i = i + 1
                result = main.TRUE
        endTime = time.time() 
        if result == main.TRUE:
            main.log.report("\tTime to complete ping test: "+str(round(endTime-strtTime,2))+" seconds")
        else:
            main.log.report("\tPING TEST FAIL")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="NO PACKET LOSS, HOST IS REACHABLE",onfail="PACKET LOST, HOST IS NOT REACHABLE")
        time.sleep(10)

# **********************************************************************************************************************************************************************************************
#This test case restores the controllers removed by Case 4 then performs a ping test.

    def CASE5(self,main) :
        main.log.report("Restore ONOS 2,3,4 then ping until all hosts are reachable or fail after 6 attempts")
        import time
        for i in range(25): 
            if i < 3:
                j=i+1
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
                time.sleep(1)
                main.Mininet1.assign_sw_controller(sw=str(j),count=4,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'])
            elif i >= 3 and i < 5:
                j=i+1
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip2'],port1=main.params['CTRL']['port2'])
                time.sleep(1)
                main.Mininet1.assign_sw_controller(sw=str(j),count=4,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'])
            elif i >= 5 and i < 15:
                j=i+1
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip3'],port1=main.params['CTRL']['port3'])
                time.sleep(1)
                main.Mininet1.assign_sw_controller(sw=str(j),count=4,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'])
            else:
                j=i+16
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip4'],port1=main.params['CTRL']['port4'])
                main.Mininet1.assign_sw_controller(sw=str(j),count=4,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'])
                time.sleep(1)
        strtTime = time.time() 
        result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        for i in range(10):
            if result == main.FALSE:
                time.sleep(5)
                result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
            else:
                break

        count = 1
        i = 6
        while i < 16 :
            main.log.info("\n\t\t\t\th"+str(i)+" IS PINGING h"+str(i+25) )
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+25))
            if ping == main.FALSE and count < 6:
                count = count + 1
                i = 6
                main.log.info("Ping failed, making attempt number "+str(count)+" in 2 seconds")
                time.sleep(2)
            elif ping == main.FALSE and count ==6:
                main.log.error("Ping test failed")
                i = 17
                result = main.FALSE
            elif ping == main.TRUE:
                i = i + 1
                result = main.TRUE
        endTime = time.time()
        if result == main.TRUE:
            main.log.report("\tTime to complete ping test: "+str(round(endTime-strtTime,2))+" seconds")
        else:
            main.log.report("\tPING TEST FAILED")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="NO PACKET LOSS, HOST IS REACHABLE",onfail="PACKET LOST, HOST IS NOT REACHABLE")

# **********************************************************************************************************************************************************************************************
#Brings a link that all flows pass through in the mininet down, then runs a ping test to view reroute time

    def CASE6(self,main) :
        main.log.report("Bring Link between s1 and s2 down, then ping until all hosts are reachable or fail after 10 attempts")
        import time
        main.case("Bringing Link down... ")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Link DOWN!",onfail="Link not brought down...")
        time.sleep(10)
        strtTime = time.time() 
        result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],str(int(main.params['NR_Links'])-2))
        for i in range(10):
            if result == main.FALSE:
                time.sleep(5)
                result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],str(int(main.params['NR_Links'])-2))
            else:
                break

        count = 1
        i = 6
        while i < 16 :
            main.log.info("\n\t\t\t\th"+str(i)+" IS PINGING h"+str(i+25) )
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+25))
            if ping == main.FALSE and count < 10:
                count = count + 1
                main.log.info("Ping failed, making attempt number "+str(count)+" in 2 seconds")
                i = 6
                time.sleep(2)
            elif ping == main.FALSE and count == 10:
                main.log.error("Ping test failed")
                i = 17
                result = main.FALSE
            elif ping == main.TRUE:
                i = i + 1
                result = main.TRUE
        endTime = time.time()
        if result == main.TRUE:
            main.log.report("\tTime to complete ping test: "+str(round(endTime-strtTime,2))+" seconds")
        else:
            main.log.report("\tPING TEST FAILED")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="NO PACKET LOSS, HOST IS REACHABLE",onfail="PACKET LOST, HOST IS NOT REACHABLE")

# **********************************************************************************************************************************************************************************************
#Brings the link that Case 6 took down  back up, then runs a ping test to view reroute time

    def CASE7(self,main) :
        main.log.report("Bring Link between s1 and s2 up, then ping until all hosts are reachable or fail after 10 attempts")
        import time
        main.case("Bringing Link up... ")
        result = main.Mininet1.link(END1='s1',END2='s3',OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Link UP!",onfail="Link not brought up...")
        time.sleep(10) 
        strtTime = time.time() 
        result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],str(int(main.params['NR_Links'])-2))
        for i in range(10):
            if result == main.FALSE:
                time.sleep(15)
                result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],str(int(main.params['NR_Links'])-2))
            else:
                break

        strtTime = time.time()
        count = 1
        i = 6
        while i < 16 :
            main.log.info("\n\t\t\t\th"+str(i)+" IS PINGING h"+str(i+25) )
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+25))
            if ping == main.FALSE and count < 10:
                count = count + 1
                main.log.info("Ping failed, making attempt number "+str(count)+" in 2 seconds")
                i = 6
                time.sleep(2)
            elif ping == main.FALSE and count ==10:
                main.log.error("Ping test failed")
                i = 17
                result = main.FALSE
            elif ping == main.TRUE:
                i = i + 1
                result = main.TRUE
        endTime = time.time()
        if result == main.TRUE:
            main.log.report("\tTime to complete ping test: "+str(round(endTime-strtTime,2))+" seconds")
        else:
            main.log.report("\tPING TESTS FAILED")
        data = main.Mininet1.link(END1='s1',END2='s3',OPTION="up")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="NO PACKET LOSS, HOST IS REACHABLE",onfail="PACKET LOST, HOST IS NOT REACHABLE")


# ******************************************************************************************************************************************************************
# Test Device Discovery function by yanking s6:s6-eth0 interface and re-plug it into a switch

    def CASE21(self,main) :
        import json
        main.log.report("Test device discovery function, by attach, detach, move host h1 from s1->s6->s1. Per mininet naming, switch port the host attaches will remain as 's1-eth1' throughout the test.")
        main.log.report("Check initially hostMAC/IP exist on the mininet...")
        host = main.params['YANK']['hostname']
        mac = main.params['YANK']['hostmac']
        RestIP1 = main.params['RESTCALL']['restIP1']
        RestPort = main.params['RESTCALL']['restPort']
        url = main.params['RESTCALL']['restURL']
       
        t_topowait = 5
        t_restwait = 5
        main.log.report( "Wait time from topo change to ping set to " + str(t_topowait))
        main.log.report( "Wait time from ping to rest call set to " + str(t_restwait))
        #print "host=" + host + ";  RestIP=" + RestIP1 + ";  RestPort=" + str(RestPort)
        time.sleep(t_topowait) 
        main.log.info("\n\t\t\t\t ping issue one ping from " + str(host) + " to generate arp to switch. Ping result is not important" )
        ping = main.Mininet1.pingHost(src = str(host),target = "10.0.0.254")
        time.sleep(t_restwait)
        Reststatus, Switch, Port = main.ONOS1.find_host(RestIP1,RestPort,url, mac)
        main.log.report("Number of host with MAC address = " + mac + " found by ONOS is: " + str(Reststatus))
        if Reststatus == 1:
            main.log.report("\t PASSED - Found host mac = " + mac + ";  attached to switchDPID = " +"".join(Switch) + "; at port = " + str(Port[0]))
            result1 = main.TRUE
        elif Reststatus > 1:
            main.log.report("\t FAILED - Host " + host + " with MAC:" + mac + " has " + str(Reststatus) + " duplicated mac  addresses. FAILED")
            main.log.report("switches are: " + "; ".join(Switch))
            main.log.report("Ports are: " + "; ".join(Port))
            result1 = main.FALSE
        elif Reststatus == 0 and Switch == []:
            main.log.report("\t FAILED - Host " + host + " with MAC:" + mac + " does not exist. FAILED")
            result1 = main.FALSE
        else:# check if rest server is working
            main.log.error("Issue with find host")
            result1 = main.FALSE


        ##### Step to yank out "s1-eth1" from s1, which is on autoONOS1 #####

        main.log.report("Yank out s1-eth1")
        main.case("Yankout s6-eth1 (link to h1) from s1")
        result = main.Mininet1.yank(SW=main.params['YANK']['sw1'],INTF=main.params['YANK']['intf'])
        time.sleep(t_topowait)
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Yank command suceeded",onfail="Yank command failed...")

        main.log.info("\n\t\t\t\t ping issue one ping from " + str(host) + " to generate arp to switch. Ping result is not important" )
        ping = main.Mininet1.pingHost(src = str(host),target = "10.0.0.254")
        time.sleep(t_restwait)
        Reststatus, Switch, Port = main.ONOS1.find_host(RestIP1,RestPort,url, mac)

        main.log.report("Number of host with MAC = " + mac + " found by ONOS is: " + str(Reststatus))
        if Reststatus == 1:
            main.log.report("\tFAILED - Found host MAC = " + mac + "; attached to switchDPID = " + "".join(Switch) + "; at port = " + str(Port))
            result2 = main.FALSE
        elif Reststatus > 1:
            main.log.report("\t FAILED - Host " + host + " with MAC:" + str(mac) + " has " + str(Reststatus) + " duplicated IP addresses. FAILED")
            main.log.report("switches are: " + "; ".join(Switch))
            main.log.report("Ports are: " + "; ".join(Port))
            main.log.report("MACs are: " + "; ".join(MAC))
            result2 = main.FALSE
        elif Reststatus == 0 and Switch == []:
            main.log.report("\t PASSED - Host " + host + " with MAC:" + str(mac) + " does not exist. PASSED - host is not supposed to be attached to the switch.")
            result2 = main.TRUE
        else:# check if rest server is working
            main.log.error("Issue with find host")
            result2 = main.FALSE
         
        ##### Step to plug "s1-eth1" to s6, which is on autoONOS3  ######
        main.log.report("Plug s1-eth1 into s6")
        main.case("Plug s1-eth1 to s6")
        result = main.Mininet1.plug(SW=main.params['PLUG']['sw6'],INTF=main.params['PLUG']['intf'])
        time.sleep(t_topowait)
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Plug command suceeded",onfail="Plug command failed...")
        main.log.info("\n\t\t\t\t ping issue one ping from " + str(host) + " to generate arp to switch. Ping result is not important" )

        ping = main.Mininet1.pingHost(src = str(host),target = "10.0.0.254")
        time.sleep(t_restwait)
        Reststatus, Switch, Port = main.ONOS1.find_host(RestIP1,RestPort,url, mac)

        main.log.report("Number of host with MAC " + mac + " found by ONOS is: " + str(Reststatus))
        if Reststatus == 1:
            main.log.report("\tPASSED - Found host MAC = " + mac + "; attached to switchDPID = " + "".join(Switch) + "; at port = " + str(Port[0]))
            result3 = main.TRUE
        elif Reststatus > 1:
            main.log.report("\t FAILED - Host " + host + " with MAC:" + str(mac) + " has " + str(Reststatus) + " duplicated IP addresses. FAILED")
            main.log.report("switches are: " + "; ".join(Switch))
            main.log.report("Ports are: " + "; ".join(Port))
            main.log.report("MACs are: " + "; ".join(MAC))            
            result3 = main.FALSE
        elif Reststatus == 0 and Switch == []:
            main.log.report("\t FAILED - Host " + host + " with MAC:" + str(mac) + " does not exist. FAILED")
            result3 = main.FALSE
        else:# check if rest server is working
            main.log.error("Issue with find host")
            result3 = main.FALSE

        ###### Step to put interface "s1-eth1" back to s1"#####
        main.log.report("Move s1-eth1 back on to s1")
        main.case("Move s1-eth1 back to s1")
        result = main.Mininet1.yank(SW=main.params['YANK']['sw6'],INTF=main.params['YANK']['intf'])
        time.sleep(t_topowait)
        result = main.Mininet1.plug(SW=main.params['PLUG']['sw1'],INTF=main.params['PLUG']['intf'])
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Yank/Plug command suceeded",onfail="Yank/Plug command failed...")
        main.log.info("\n\t\t\t\t ping issue one ping from " + str(host) + " to generate arp to switch. Ping result is not important" )

        ping = main.Mininet1.pingHost(src = str(host),target = "10.0.0.254")
        time.sleep(t_restwait)
        Reststatus, Switch, Port = main.ONOS1.find_host(RestIP1,RestPort,url, mac)

        main.log.report("Number of host with IP=10.0.0.1 found by ONOS is: " + str(Reststatus))
        if Reststatus == 1:
            main.log.report("\tPASSED - Found host MAC = " + mac + "; attached to switchDPID = " + "".join(Switch) + "; at port = " + str(Port[0]))
            result4 = main.TRUE
        elif Reststatus > 1:
            main.log.report("\t FAILED - Host " + host + " with MAC:" + str(mac) + " has " + str(Reststatuas) + " duplicated IP addresses. FAILED")
            main.log.report("switches are: " + "; ".join(Switch))
            main.log.report("Ports are: " + "; ".join(Port))
            main.log.report("MACs are: " + "; ".join(MAC))            
            result4 = main.FALSE
        elif Reststatus == 0 and Switch == []:
            main.log.report("\t FAILED -Host " + host + " with MAC:" + str(mac) + " does not exist. FAILED")
            result4 = main.FALSE
        else:# check if rest server is working
            main.log.error("Issue with find host")
            result4 = main.FALSE
        time.sleep(20)
        Reststatus, Switch, Port = main.ONOS1.find_host(RestIP1,RestPort,url,mac)
        main.log.report("Number of host with IP=10.0.0.1 found by ONOS is: " + str(Reststatus))
        if Reststatus ==1:
            main.log.report("\t FAILED - Host " + host + "with MAC:" + str(mac) + "was still found after expected timeout")
        elif Reststatus>1:
            main.log.report("\t FAILED - Host " + host + "with MAC:" + str(mac) + "was still found after expected timeout(multiple found)")
        elif Reststatus==0:
            main.log.report("\t PASSED - Device cleared after timeout")

        result = result1 and result2 and result3 and result4
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="DEVICE DISCOVERY TEST PASSED PLUG/UNPLUG/MOVE TEST",onfail="DEVICE DISCOVERY TEST FAILED")

# Run a pure ping test. 

    def CASE31(self, main):
        main.log.report("Performing Ping Test")        
        count = 1
        i = 6
        while i < 16 :
            main.log.info("\n\t\t\t\th"+str(i)+" IS PINGING h"+str(i+25) )
            strtTime = time.time()
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+25))
            if ping == main.FALSE and count < 6:
                count = count + 1
                i = 6
                main.log.info("Ping failed, making attempt number "+str(count)+" in 2 seconds")
                time.sleep(2)
            elif ping == main.FALSE and count ==6:
                main.log.error("Ping test failed")
                i = 17
                result = main.FALSE
            elif ping == main.TRUE:
                i = i + 1
                result = main.TRUE
        endTime = time.time()
        if result == main.TRUE:
            main.log.report("\tTime to complete ping test: "+str(round(endTime-strtTime,2))+" seconds")
        else:
            main.log.report("\tPING TEST FAIL")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="NO PACKET LOSS, HOST IS REACHABLE",onfail="PACKET LOST, HOST IS NOT REACHABLE")


    def CASE66(self, main):
        main.log.report("Checking ONOS logs for exceptions")
        count = 0
        check1 = main.ONOS1.check_exceptions()
        main.log.report("Exceptions in ONOS1 logs: \n" + check1)
        check2 = main.ONOS2.check_exceptions()
        main.log.report("Exceptions in ONOS2 logs: \n" + check2)
        check3 = main.ONOS3.check_exceptions()
        main.log.report("Exceptions in ONOS3 logs: \n" + check3)
        check4 = main.ONOS4.check_exceptions()
        main.log.report("Exceptions in ONOS4 logs: \n" + check4)
        result = main.TRUE
        if (check1 or check2 or check3 or check4):
            result = main.FALSE
            count = len(check1.splitlines()) + len(check2.splitlines()) + len(check3.splitlines()) + len(check4.splitlines())
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="No Exceptions found in the logs",onfail=str(count) + " Exceptions were found in the logs")
        main.Mininet2.stop_tcpdump()


    def CASE8(self,main) :
        main.log.report("Testing Removal of Zookeeper")
        main.Zookeeper2.stop()
        main.Zookeeper3.stop()
        main.Zookeeper4.stop()
        strtTime = time.time() 
        result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        for i in range(10):
            if result == main.FALSE:
                time.sleep(5)
                result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
            else:
                break

        count = 1
        i = 6
        while i < 16 :
            main.log.info("\n\t\t\t\th"+str(i)+" IS PINGING h"+str(i+25) )
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+25))
            if ping == main.FALSE and count < 6:
                count = count + 1
                i = 6
                main.log.info("Ping failed, making attempt number "+str(count)+" in 2 seconds")
                time.sleep(2)
            elif ping == main.FALSE and count ==6:
                main.log.error("Ping test failed")
                i = 17
                result = main.FALSE
            elif ping == main.TRUE:
                i = i + 1
                result = main.TRUE
        endTime = time.time() 
        if result == main.TRUE:
            main.log.report("\tTime to complete ping test: "+str(round(endTime-strtTime,2))+" seconds")
        else:
            main.log.report("\tPING TEST FAIL")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="NO PACKET LOSS, HOST IS REACHABLE",onfail="PACKET LOST, HOST IS NOT REACHABLE")
        time.sleep(10)
        main.Zookeeper2.start() 
        main.Zookeeper3.start()
        main.Zookeeper4.start() 
        time.sleep(10)


    def CASE67(self, main) :
        main.case("Flapping link s1-s2")
        main.log.report("Toggling of link s1-s2 multiple times")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")

        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],str(int(main.params['NR_Links'])-2))
        for i in range(10):
            if result == main.FALSE:
                time.sleep(15)
                result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],str(int(main.params['NR_Links'])-2))
            else:
                break

        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],str(int(main.params['NR_Links'])))
        for i in range(10):
            if result == main.FALSE:
                time.sleep(15)
                result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],str(int(main.params['NR_Links'])))
            else:
                break
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],str(int(main.params['NR_Links'])-2))
        for i in range(10):
            if result == main.FALSE:
                time.sleep(15)
                result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],str(int(main.params['NR_Links'])-2))
            else:
                break
           


    def CASE101(self,main) :
        import time
        import json
        import re
        main.case("Testing the Intent Framework of ONOS")
        
#*****************************************************************************************
#*****************************************************************************************
# The first part of CASE 101 will be assigning the master controllers to the switches
# and to check that each one is assigned correctly. 
#*****************************************************************************************
#*****************************************************************************************
        main.step("Assigning Master Controllers to the Switches and check")
        for i in range(25):
            if i<3:
                j=i+1
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
            elif i>=3 and i<5:
                j=i+1
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip2'],port1=main.params['CTRL']['port1'])
            elif i>=5 and i<15:
                j=j+1
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip3'],port1=main.params['CTRL']['port1'])
            else:
                j=i+16
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip4'],port1=main.params['CTRL']['port1'])
        result = main.TRUE
        for i in range(25):
            if i<3:
                j=i+1
                response=main.Mininet1.get_sw_controller("s"+str(j))
                print("Response is " + str(response))
                if re.search("tcp:"+main.params['CTRL']['ip1'],response) :
                    result = result and main.TRUE
                else:
                    result = main.FALSE
            elif i>=3 and i<5:
                j=i+1
                response=main.Mininet1.get_sw_controller("s"+str(j))
                if re.search("tcp:"+main.params['CTRL']['ip2'],response) :
                    result = result and main.TRUE
                else:
                    result = main.FALSE
            elif i>=5 and i<15:
                j=j+1
                response=main.Mininet1.get_sw_controller("s"+str(j))
                if re.search("tcp:"+main.params['CTRL']['ip3'],response) :
                    result = result and main.TRUE
                else:
                    result = main.FALSE
            else:
                j=i+16
                response=main.Mininet1.get_sw_controller("s"+str(j))
                if re.search("tcp:"+main.params['CTRL']['ip4'],response) :
                    result = result and main.TRUE
                else:
                    result = main.FALSE
            print(result)
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Master Controllers assigned Properly",onfail="FAILED TO ASSIGN MASTER CONTROLLERS!")

#*****************************************************************************************
#*****************************************************************************************
# Assign all controllers to the switches as backups. Run a get-controller on each
# switch to ensure that all controllers have been assigned properly to its switches
#*****************************************************************************************
#*****************************************************************************************
        main.step("Assigning all Controllers as Backups to Switches and Check")
        for i in range(25):
            if i<15:
                j=i+1
                main.Mininet1.assign_sw_controller(sw=str(j),count=4,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'])
            else:
                j=i+16
                main.Mininet1.assign_sw_controller(sw=str(j),count=4,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'])
        result = main.TRUE
        time.sleep(5)
        for i in range(25):
            if i<15:
                j=i+1
                response=main.Mininet1.get_sw_controller("s"+str(j))
                if re.search("tcp:"+main.params['CTRL']['ip1'],response) and re.search("tcp:"+main.params['CTRL']['ip2'],response) and re.search("tcp:"+main.params['CTRL']['ip3'],response) and re.search("tcp:"+main.params['CTRL']['ip4'],response):
                    result = result and main.TRUE
                else:
                    result = main.FALSE
            else:
                j=i+16
                response=main.Mininet1.get_sw_controller("s"+str(j))
                if re.search("tcp:"+main.params['CTRL']['ip1'],response) and re.search("tcp:"+main.params['CTRL']['ip2'],response) and re.search("tcp:"+main.params['CTRL']['ip3'],response) and re.search("tcp:"+main.params['CTRL']['ip4'],response):
                    result = result and main.TRUE
                else:
                    result = main.FALSE
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Controllers assigned properly to all switches",onfail="FAILED TO ASSIGN CONTROLLERS PROPERLY!")


        
#*****************************************************************************************
#*****************************************************************************************
# Installation of Intents. This part will run run a forloop and add an intent from 
# h6 to h31, h7 to h32, etc and the other way as well, h31 to h6, h32 to h7, etc.
# then Check by dumping the flows on SW2 and check for flows going bidirectionally.
#*****************************************************************************************
#*****************************************************************************************
        main.step("Install intents and Check for Installation of Flows")
        intentIP = main.params['INTENTREST']['intentIP']
        intentPort=main.params['INTENTREST']['intentPort']
        intentURL=main.params['INTENTREST']['intentURL']
        count = 1
        for i in range(6,16):
            time.sleep(1)
            srcMac = '00:00:00:00:00:' + str(hex(i)[2:]).zfill(2)
            dstMac = '00:00:00:00:00:'+str(hex(i+10)[2:])
            #srcDPID=str(i)
            #dstDPID=str(i+10)
            srcDPID = '00:00:00:00:00:00:10:'+str(i).zfill(2)
            dstDPID= '00:00:00:00:00:00:20:' +str(i+25)
            main.ONOS1.add_intent(intent_id=str(count),src_dpid=srcDPID,dst_dpid=dstDPID,src_mac=srcMac,dst_mac=dstMac,intentIP=intentIP,intentPort=intentPort,intentURL=intentURL)
            count +=1
            dstMac = '00:00:00:00:00:' + str(hex(i)[2:]).zfill(2)
            srcMac = '00:00:00:00:00:'+str(hex(i+10)[2:])
            #srcDPID=str(i)
            #dstDPID=str(i+10)
            dstDPID = '00:00:00:00:00:00:10:'+str(i).zfill(2)
            srcDPID= '00:00:00:00:00:00:20:' +str(i+25)
            main.ONOS1.add_intent(intent_id=str(count),src_dpid=srcDPID,dst_dpid=dstDPID,src_mac=srcMac,dst_mac=dstMac,intentIP=intentIP,intentPort=intentPort,intentURL=intentURL)
            count+=1
        result = main.TRUE
        response = main.Mininet1.check_flows(sw="s1")
        print(response)
        for i in range(6,16):
            if re.search("dl_src=00:00:00:00:00:"+''.join('%02x'%i),response) and re.search("dl_src=00:00:00:00:00:"+''.join('%02x'%(i+10)),response) and re.search("dl_dst=00:00:00:00:00:"+''.join('%02x'%i),response) and re.search("dl_dst=00:00:00:00:00:"+''.join('%02x'%(i+10)),response):   
                result = result and main.TRUE
            else:
                result = main.FALSE
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Flows added Properly",onfail="Flows were not added properly")
 
#*****************************************************************************************
#*****************************************************************************************
# This step will run a ping test from h6 to h31, h7 to h32, etc as an End to End test
# All of these pings should run through. 
#*****************************************************************************************
#*****************************************************************************************
        main.step("Ping Test as End to End Test that the Intents were Correctly Installed")
        main.log.report("Performing Ping Test")        
        count = 1
        i = 6
        while i < 16 :
            main.log.info("\n\t\t\t\th"+str(i)+" IS PINGING h"+str(i+25) )
            strtTime = time.time()
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+25))
            if ping == main.FALSE and count < 6:
                count = count + 1
                i = 6
                main.log.info("Ping failed, making attempt number "+str(count)+" in 2 seconds")
                time.sleep(2)
            elif ping == main.FALSE and count ==6:
                main.log.error("Ping test failed")
                i = 17
                result = main.FALSE
            elif ping == main.TRUE:
                i = i + 1
                result = main.TRUE
        endTime = time.time()
        if result == main.TRUE:
            main.log.report("\tTime to complete ping test: "+str(round(endTime-strtTime,2))+" seconds")
        else:
            main.log.report("\tPING TEST FAIL")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="NO PACKET LOSS, HOST IS REACHABLE",onfail="PACKET LOST, HOST IS NOT REACHABLE")
        
#*****************************************************************************************
#*****************************************************************************************
# Removing a single intent. Then check to ensure that intent was found by calling
# show_intent. Then check that flows are removed by pinging. 
#*****************************************************************************************
#*****************************************************************************************
        main.step("Delete a single intent and ensure that flows are deleted")
        main.ONOS1.del_intent(intentIP=intentIP,intentPort=intentPort,intentURL=intentURL,intent_id="intent_id=10")
        time.sleep(2)
        response = main.ONOS1.show_intent(intentIP=intentIP,intentPort=intentPort,intentURL=intentURL,intent_id=10)
        if re.search("INTENT_NOT_FOUND",response):
            main.log.report("Intent Removed Properly!")
        else:
            main.log.report("ERROR REMOVING INTENT")
        main.log.report("Performing Ping Test")        
        count = 1
        for count in range(4):
            ping = main.Mininet1.pingHost(src="h10",target="h35")
            if ping==main.FALSE and count == 3:
                main.log.info("Ping failed as expected. Intent Deleted")
                result = main.TRUE
            elif ping == main.TRUE:
                main.log.error("Intent was not deleted correctly")
                result = main.FALSE
            else:
                main.log.info("So far so good, attempting "+str(4-count) + " more times")
        if result == main.TRUE:
            main.log.report("\tIntent Deleted!")
        else:
            main.log.report("\tINTENT FAILED TO BE DELETED")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Intent Deleted Properly - Step Passed",onfail="INTENT NOT DELETED - STEP FAILED")
        main.ONOS1.del_intent(intentIP=intentIP,intentPort=intentPort,intentURL=intentURL)


#*****************************************************************************************
#*****************************************************************************************
# Install a bad intent. Then, ensure that we are able to get rid of it
# Installing an intent as ID=200, from a random dpid/mac to random dpid/mac. Then, 
# check to make sure the intent is there, then delete it and ensure that it is gone
#*****************************************************************************************
#*****************************************************************************************


        main.step("Installing incorrect intent and checking for deletion")
        main.ONOS1.add_intent(intent_id=str(200),src_dpid="00:00:00:00:00:00:45:67",dst_dpid="00:00:00:00:00:32:21:10",src_mac="00:00:00:01:11:11",dst_mac="00:12:12:12:12:12",intentIP=intentIP,intentPort=intentPort,intentURL=intentURL)

        
        


    def CASE10(self, main) :
        import time
        time.sleep(600)
