#!-*- coding:utf-8-*-
#!author:xeldax
#--------------
#一秒钟10个数据
#5秒钟一个周期
#一个周期50组数据
#这是模拟锅炉温度的模拟器
#--------------
import random
import os
import sys
import time
import threading
from Queue import Queue

period=5
sec=0.1
flag=-1
queue=Queue()

def data(queue=None,nodename=None,nodenum=None,temperture=None,floatable=None):
    global flag
    global period
    global sec
    tmp_list=[]
    flag=-1
    while True:
        time.sleep(sec)
        #print nodenum,flag
        if flag==nodenum:
            print '[+]attack'
            f=temperture+random.randint(-300,300)
            flag=-1
        else:
            f=temperture+random.randint(0,int(floatable))
            print f
            tmp_list.append(f)
        if len(tmp_list)==int(period/sec):
            print tmp_list
            queue.put([nodename,tmp_list])
            tmp_list=[]

def key_hook():
    global flag
    #print 'Press to start attack'
    while True:
        a=raw_input()
        #print a
        flag=int(a)#!!!
        print '--------',flag
        time.sleep(0.1)
        flag=-1

def file_save(queue,max_node_num):
    buf=[]
    while True:
        buf.append(queue.get())
        if len(buf)==int(max_node_num):
            file_handle=open('nodeinformation.info','w')
            for i in buf:
                file_handle.write(str(i[0])+': ')
                for j in i[1]:
                    file_handle.write(str(j)+' ')
                file_handle.write('\n')
            buf=[]
            file_handle.close()

if __name__=='__main__':

    thd=threading.Thread(target=key_hook)
    thd.daemon=True
    print 'Please set the number of node:'
    node=int(input())
    threadpool=[]
    for i in range(1,node+1):
        print 'Temperture'
        temperture=input()
        print 'floatable'
        floatable=input()
        print 'nodename'
        nodename=str(raw_input())
        tmp=threading.Thread(target=data,args=(queue,nodename,i,temperture,floatable))
        threadpool.append(tmp)
    for i in threadpool:
        i.start()
    thd.start()
    thd=threading.Thread(target=file_save,args=(queue,node))
    thd.start()
