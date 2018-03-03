#coding=utf-8

import argparse
import socket
import struct
import time,random
import threading
import queue
import sys,os

m=0;n=0;t=[]

time1=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
t1=time.mktime(time.strptime(time1,'%Y-%m-%d %H:%M:%S'))
#current filepath and filename

file1=os.path.realpath(sys.path[0])+'\\'+str(int(time.time()))+'.txt'

def deal_ports(ports):
  #ports='12,23,34-56,567-9877' or '123' or '12-56' or '12,45,63'
  portlist=set()
  if (',' not in ports) and ('-' not in ports):
    portlist.add(int(ports))
    return portlist
	
  if (',' in ports) and ('-' not in ports):
    tmp=ports.split(',')
    for i in tmp:
      portlist.add(int(i))
    return portlist
  
  if (',' not in ports) and ('-' in ports):
    tmp=ports.split('-')
    if int(tmp[0])>int(tmp[1]):
      max0=int(tmp[0])+1
      min0=int(tmp[1])
    else:
      max0=int(tmp[1])+1
      min0=int(tmp[0])
    for i in range(min0,max0):
      portlist.add(int(i))
    return portlist

  if (',' in ports) and ('-' in ports): 
    tmp1=set()
    tmp=ports.split(',')
    for i in tmp:
      if '-' in i:
        tmp1.add(i)
      else:
        portlist.add(i)
    
    for i in tmp1:
      tmp3=ports.split('-')
      if int(tmp3[0])>int(tmp3[1]):
        max0=int(tmp3[0])+1
        min0=int(tmp3[1])
      else:
        max0=int(tmp3[1])+1
        min0=int(tmp3[0])
      for i in range(min0,max0):
        portlist.add(int(i)) 
		
    return portlist

def deal_hosts(hosts):
  tgtHosts=[];partlist1=[];partlist2=[];partlist3=[]
  tmplist=hosts.split(',')
  if '-' not in hosts:
    for i in tmplist:
      tgtHosts.append(i)
  elif '-' in hosts:
    for i in tmplist:
      if '-' not in i:
        partlist1.append(i)
      elif '-' in i:
        partlist2.append(i)
    for i in partlist2:
      j=i.split('-')
      startip=j[0]
      endip=j[1]
    #ip2number
      m=socket.ntohl(struct.unpack('I',socket.inet_aton(startip))[0])
      n=socket.ntohl(struct.unpack('I',socket.inet_aton(endip))[0])
      if m<n:
        m0=m
        n0=n+1
      else:
        m0=n
        n0=m+1       
    #number2iplist
      for i in range(m0,n0):
        x=socket.inet_ntoa(struct.pack('I',socket.htonl(i)))
        partlist3.append(x)
    tgtHosts=list(set(partlist1+partlist3))
  return tgtHosts

 #define class to run scan task:
templist1=[]
class scanports(threading.Thread): 
  def __init__(self,que):
    threading.Thread.__init__(self)
    self._que=que

  def run(self):
    global templist1
    while not self._que.empty():
      a=self._que.get()
      if not a:
        break
      host=a[0]
      port=a[1]
      iport=host+':'+str(port)
      s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
      try:
        socket.setdefaulttimeout(1)
        #sys.stdout.write('[-] trying %s ...\n'%iport)
        reiv=s.connect_ex((host,port))
        if reiv==0:
          sys.stdout.write('[+] %s is open!\n'%iport)
          templist1.append(iport)
        s.close()
      except:
        s.close()
        

def main():
  parser=argparse.ArgumentParser(description="multi-thread port scanner,python ver3.6.0, author: shadow008") 
  parser.add_argument('-H','--host',help='specify target ip[s], exam: 123.123.123.123-123.234.234.234',dest='Host')
  parser.add_argument('-p','--port',help='specify target port[s], exam: 80,8080,9000-10000',dest='Port')
  parser.add_argument('-t','--threads',help='specify scanning threads, exam: 80',dest='Threads',type=int,default=100)
  result=parser.parse_args()
  tgtHost=result.Host
  tgtPorts=result.Port
  scanThreads=result.Threads
  if(tgtHost==None) or (tgtPorts==None):
    parser.print_help()
    exit(0)
  print('Scanning starts! Start time is '+time1)

  #deal_hosts:
  hostlist=deal_hosts(tgtHost)

  #deal_port:
  portlist=deal_ports(tgtPorts)

  mixlist=[]
  #scan queue:
  que=queue.Queue()
  for host in hostlist:
    for port in portlist:
      mixlist.append((host,port))

  #randomize the list
  random.shuffle(mixlist) 
	  
  for i in mixlist:
    que.put(i)

  #start scan thread:
  for i in range(scanThreads):
    t.append(scanports(que))
  for i in t:  
    i.start()  
  for i in t:  
    i.join()
	
  if templist1:
    with open(file1,'a+') as f:
      for i in templist1:
        f.write(i+'\n')

  time2=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
  t2=time.mktime(time.strptime(time2,'%Y-%m-%d %H:%M:%S'))
  print('Scannig ends! End time is '+time2)

  b=int(t2-t1)
  s=b%60
  if (b-s)<3600:
    h=0;m=int(b/60)
  else:
    h=int((b-s)/3600);m=int(((b-s)%3600)/60)

  print('Time for scanning is '+str(h)+' hours '+str(m)+' minutes '+str(s)+' seconds')
  
  if os.path.isfile(file1):
    print('ip with open ports saved in %s'%file1)
  else:
    print('No open port found!')
  
if __name__=='__main__':
  try:
    main()
  except KeyboardInterrupt:
    sys.exit()  
    
