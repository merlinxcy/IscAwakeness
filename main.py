#!-*-coding:utf-8-*-
#!author:xeldax

import numpy
import os
import re
import time
import sys

class File():
    def __init__(self):
        self.path=os.path.abspath('.')

    def open_file(self,file_name):
        if os.path.exists(file_name):
            try:
                self.file_handle=open(file_name)
            except Exception as e:
                print e
        else:
            print 'file not exists'

    """
    <- File Format ->
    NodeX: x x x
    """
    def get_node_type1(self):
        try:
            file_content=self.file_handle.read()
            #print file_content
            tmp=re.findall(r'(.*?): (.*?)\n',file_content)
            result=[]
            for i in tmp:
                #print i
                tmp2=i[1].split(' ')
                tmp2=[tt for tt in tmp2 if tt!='']
                #print tmp2
                for m,n in enumerate(tmp2):
                    tmp2[m]=int(n)
                result.append([i[0],tmp2])
            return result
        except Exception as e:
            print e
            return None


class ISCAwakenness():
    def __init__(self,period):
        self.period=period
        self.unit_time=1
        self.file_manager=File()
        self.period_pass=1

    def _xor_(self,a,b):
        if a==b:
            return 0
        else:
            return 1

    def _xnor_(self,a,b):
        if a==b:
            return 1
        else:
            return 0

    def _and_(self,*args):
        num=len(args)
        if num==0:
            return None
        if num==1:
            return args[0]
        for i in range(0,num):
            if i==0:
                return 0
        return 1

    def get_nodedata(self,filename='nodeinformation.info'):
        self.file_manager.open_file(filename)
        node_info=self.file_manager.get_node_type1()
        result=[]
        for i in node_info:
            #print i[1]
            a=numpy.array(i[1])
            avg_tmp=a.mean()
            fangcha_tmp=a.var()
            result.append([i[0],avg_tmp,fangcha_tmp,min(i[1]),max(i[1])])
        return result

    def set_normal_state(self,time=10):
        print '[*]设备运作期间需人工介入选定稳态'
        print '开始摘取样本'
        while True:
            tmp_node=self.get_nodedata()
            print tmp_node
            print '该样本是否为稳定节点(Y/N)'
            a=raw_input()
            if a=='Y' or a=='y':
                #print tmp_node
                return tmp_node
            else:
                print '重新开始选取样本'

    def set_ok_state(self,normal_state):
        result=[]
        for j,i in enumerate(normal_state):
            print '请输入'+i[0]+'节点允许上下温度浮动的范围'
            percent=float(raw_input())
            node_name=i[0]
            node_min=i[3]-i[3]*percent
            node_max=i[4]+i[4]*percent
            node_re_avg=(i[3]+i[4])/2
            node_re_fangcha=pow((node_min-node_re_avg),2)+pow(node_max-node_re_avg,2)
            result.append([node_name,node_re_avg,node_re_fangcha,node_min,i[3],i[4],node_max])
        print result
        return result

    def init_stage(self):
        self.node_normal_state=self.set_normal_state()
        self.node_ok_state=self.set_ok_state(self.node_normal_state)

    def state_func(self,node):
        state_point=[]
        for i in node:
            #print i
            node_name=i[0]
            node_avg=i[1]
            for j in self.node_normal_state:
                if node_name==j[0]:
                    normal_state_avgdata=j[1]
            if node_avg <= normal_state_avgdata:
                state=0
                state_point.append([node_name,state])
            if node_avg > normal_state_avgdata:
                state=1
                state_point.append([node_name,state])
        return state_point

    def node_status_judge(self,node):
        node_status=[]
        pianchazhi=0.2
        for i in node:
            node_name=i[0]
            node_avg=i[1]
            node_fangcha=i[2]
            for j in self.node_normal_state:
                if node_name==j[0]:
                    normal_state_fangcha=j[2]
                    normal_state_min=j[3]
                    normal_state_max=j[4]
            for j in self.node_ok_state:
                if node_name==j[0]:
                    ok_state_fangcha=j[2]
                    ok_state_range1=j[3]
                    ok_state_range2=j[4]
                    ok_state_range3=j[5]
                    ok_state_range4=j[6]
                    print ok_state_range1,ok_state_range2,ok_state_range3,ok_state_range4
            if node_avg>=normal_state_min and node_avg<=normal_state_max and node_fangcha<=normal_state_fangcha:
                node_s='normal'
            elif node_avg>=ok_state_range1 and node_avg<=ok_state_range2+pianchazhi and node_avg>=ok_state_range3-pianchazhi and node_avg<=ok_state_range4 and node_fangcha<=ok_state_fangcha:
                node_s='ok'
            else:
                print node_avg>=ok_state_range1
                print node_avg<=ok_state_range2
                print node_avg>=ok_state_range3
                print node_avg<=ok_state_range4
                print node_fangcha<=ok_state_fangcha
                node_s='warning'
            node_status.append([node_name,node_s])
        return node_status

    """
    论文上的节点就只有三个，而我一开始设计的是任意一个节点
    但是任意节点的公式不知道怎么推，所以将就一下使用三个节点，虽然其他函数都是任意节点的
    """
    def atc_node_fun(self,state):
        if len(state)==3:
            s1=self._xor_(state[1],state[2])
            s2=self._xnor_(state[0],state[1])
            s3=self._xnor_(state[0],state[2])
            atc_node=self._and_([s1,s2,s3])
            if atc_node==1:
                return atc_node,[s1,s2,s3]
            else:
                return atc_node,[0,0,0]
        else:
            print '该函数暂时不支持3个以上节点'
            sys.exit(0)

    """
    同样这个函数支持多个节点，但算法整体受到atc_node_fun函数影响
    """
    def pl_sec(self,node_status):
        ok_flag=0
        normal_flag=0
        for i in node_status:
            if i[1]=='normal':
                normal_flag=1
            if i[1]=='warning':
                return 'pl warning'
            if i[1]=='ok':
                ok_flag=1
        if ok_flag==0 and normal_flag==1:
            return 'pl normal'
        elif ok_flag==1:
            return 'pl other'
        else:
            return 'unknow[error]'

    def run(self):
        print '[*]Start.......'
        self.init_stage()
        while True:
            print '-------------test-------------'
            time.sleep(self.period+0.2)
            node=self.get_nodedata()
            print node
            print '--'
            node_status=self.node_status_judge(node)
            print node_status
            print '--'
            stage_result=self.state_func(node)
            print stage_result
            print '--'
            atcnode_result1,atcnode_result2=self.atc_node_fun(stage_result)
            print atcnode_result1,atcnode_result2
            print '--'
            plsec_result=self.pl_sec(node_status)
            print plsec_result
            print '-------------test-------------'


def test():
    a=numpy.array([1,2,3,4,5])
    print a.var()

if __name__=='__main__':
    '''
    a=File()
    a.open_file('nodeinformation.info')
    a.get_node_type1()
    '''
    a=ISCAwakenness(5)
    a.run()
