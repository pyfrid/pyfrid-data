#  Copyright 2012 Denis Korolkov
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from lepl import *

from pyfrid.utils.threadpool import ThreadPool
from pyfrid.modules.system.vm.leplvm import BaseNode, ValidateError

class BaseDeviceNode(BaseNode):
    
    def __init__(self, *args, **kwargs):
        super(BaseDeviceNode, self).__init__(*args, **kwargs)
        self.device=None
        self.current_pos =  None
        self.runtime=0
        
    def validate_move(self, scancmd, pos):
        try:
            if not self.device.validate_move(pos):
                raise ValidateError
            self.runtime+=self.device.runtime_scan(pos, self.current_pos)
        except AttributeError: 
            pass

class DeviceStepNode(BaseDeviceNode):
    
    def __init__(self, *args, **kwargs):
        super(DeviceStepNode, self).__init__(*args, **kwargs)
        self.start_pos=None
        self.step_pos=None
                             
    def move_to_start(self, scancmd, validate=False):
        if scancmd.stopped: return
        if validate:
            self.validate_move(scancmd, self.start_pos)
            self.current_pos = self.start_pos
            return
        scancmd.info("Moving {0} to starting position {1} {2}...".format(self.device.name, self.start_pos, self.device.units))
        self.device.do_move(self.start_pos)
        self.current_pos = self.start_pos
    
    def move_one_step(self, scancmd, validate=False):
        if scancmd.stopped: return
        newpos=self.current_pos+self.step_pos
        if validate:
            self.validate_move(scancmd, newpos)
            self.current_pos=newpos
            return
        scancmd.info("Moving {0} to {1} {2}...".format(self.device.name, newpos, self.device.units))
        self.device.do_move(newpos)
        self.current_pos=newpos
        
    def process(self):
        self.device      =  self[0].process()
        self.start_pos   =  self[1].process()
        self.step_pos    =  self[2].process()
        self.current_pos =  self.device.call_position()
        return self
    
class DeviceListNode(BaseDeviceNode):
    
    def __init__(self, *args, **kwargs):
        super(DeviceListNode, self).__init__(*args, **kwargs)
        self.positions=None
        self.current_index=None
            
    def move_to_start(self, scancmd, validate=False):
        if scancmd.stopped: return
        pos=self.positions[0]
        if validate:
            self.validate_move(scancmd, pos)
            self.current_pos = pos
            self.current_index=0
            return
        scancmd.info("Moving {0} to starting position {1} {2}...".format(self.device.name, pos, self.device.units))
        self.current_pos=self.device.do_move(pos)
        self.current_index=0
    
    def move_one_step(self, scancmd, validate=False):
        if scancmd.stopped: return
        nextidx=self.current_index+1
        newpos=self.positions[nextidx]
        if validate:
            self.validate_move(scancmd, newpos)
            self.current_pos=newpos
            self.current_index=nextidx
            return
        scancmd.info("Moving {0} to {1} {2}...".format(self.device.name, newpos, self.device.units))
        self.device.do_move(newpos)
        self.current_pos=newpos
        self.current_index=nextidx
        
    def process(self):
        self.device      =  self[0].process()
        self.positions   =  self[1].process()
        self.current_pos =  self.device.call_position()
        return self
    
class LoopDeviceStepNode(DeviceStepNode):
    
    def __init__(self, *args, **kwargs):
        super(LoopDeviceStepNode, self).__init__(*args, **kwargs)
        self.simuldevs=[]
        self.atend=False
    
    def calc_runtime(self, scancmd, numthreads):
        rt=[self.runtime]
        rt.extend([item.runtime for item in self.simuldevs])
        lr=len(rt)
        rt=[rt[i*numthreads: min((i+1)*numthreads,lr)]  for i in range(min(numthreads,lr)) ]
        return sum([max(res) for res in rt if res])
    
    def move_to_start(self, scancmd, numthreads=1, validate=False):
        if scancmd.stopped: return
        if validate:
            super(LoopDeviceStepNode, self).move_to_start(scancmd, validate)
            for item in self.simuldevs:
                item.move_to_start(scancmd, validate)
            self.atend=False
            return
        pool=ThreadPool(scancmd, numthreads) 
        pool.add_task( super(LoopDeviceStepNode, self).move_to_start, scancmd, validate)
        for item in self.simuldevs:
            pool.add_task(item.move_to_start, scancmd, validate)
        pool.join_all()
        self.atend=False
    
    def move_one_step(self, scancmd, numthreads=1, validate=False):
        if scancmd.stopped: return
        if validate:
            super(LoopDeviceStepNode, self).move_one_step(scancmd, validate)
            for item in self.simuldevs:
                item.move_one_step(scancmd, validate)
            if not self.check_pos(self.current_pos): self.atend=True
            return
        pool=ThreadPool(scancmd,numthreads) 
        pool.add_task(super(LoopDeviceStepNode, self).move_one_step, scancmd, validate)
        for item in self.simuldevs:
            pool.add_task(item.move_one_step, scancmd, validate)
        pool.join_all()
        if not self.check_pos(self.current_pos): self.atend=True
        
    def process(self):
        super(LoopDeviceStepNode, self).process()
        self.end_pos=self[3].process()
        if len(self)>=5:
            self.simuldevs=[item.process() for item in self[4:]]
        return self
    
    def check_pos(self, pos):
        if (self.step_pos>0 and pos<self.end_pos) or \
           (self.step_pos<0 and pos>self.end_pos):
            return True
        return False
    
class LoopDeviceListNode(DeviceStepNode):
    
    def __init__(self, *args, **kwargs):
        super(LoopDeviceListNode, self).__init__(*args, **kwargs)
        
        
    def move_to_start(self, scancmd, numthreads=1, validate=False):
        if scancmd.stopped: return
        pool=ThreadPool(scancmd, numthreads) 
        pool.add_task( super(LoopDeviceStepNode, self).move_to_start, scancmd, validate)
        for item in self.simuldevs:
            pool.add_task(item.move_to_start, scancmd, validate)
        pool.join_all()
        self.atend=False
    
    def move_one_step(self, scancmd, numthreads=1, validate=False):
        if scancmd.stopped: return
        pool=ThreadPool(scancmd,numthreads) 
        pool.add_task(super(LoopDeviceStepNode, self).move_one_step, scancmd, validate)
        for item in self.simuldevs:
            pool.add_task(item.move_one_step, scancmd, validate)
        pool.join_all()
        if self.current_index==len(self.positions)-1: self.atend=True
        
    def process(self):
        super(LoopDeviceStepNode, self).process()
        if len(self)>=3:
            self.simuldevs=[item.process() for item in self[2:]]
        return self
          
class MainLoopDeviceStepNode(LoopDeviceStepNode):
    
    def process(self):
        self.device      =  self[0].process()
        self.start_pos   =  self[1].process()
        self.step_pos    =  self[2].process()
        self.end_pos     =  self[3].process()
        self.shoot_time  =  self[4].process()
        self.simuldevs=[]
        if len(self)>=6:
            self.simuldevs=[item.process() for item in self[5:]]
        return self
    
class MainLoopDeviceListNode(LoopDeviceStepNode):
    
    def process(self):
        self.device      =  self[0].process()
        self.positions   =  self[1].process()
        self.shoot_time  =  self[2].process()
        self.simuldevs=[]
        if len(self)>=4:
            self.simuldevs=[item.process() for item in self[3:]]
        return self

class LoopScanNode(BaseNode):
    
    def __init__(self, *args, **kwargs):
        super(LoopScanNode, self).__init__(*args, **kwargs)
        self.runtime=0
        
    def scan(self, scancmd, shoot_time, numthreads=1, validate=False):
        if scancmd.stopped: return
        self.litem.move_to_start(scancmd,numthreads,validate)
        while not scancmd.stopped:
            self.shoot(scancmd, shoot_time, numthreads, validate)
            self.litem.move_one_step(scancmd, numthreads, validate)
            if self.litem.atend: break
        self.shoot(scancmd, shoot_time, numthreads, validate)
                
    def process(self):
        self.litem=self[0].process()
        self.ritem=self[1].process() if len(self)>1 else None
        return self
    
    def shoot(self, scancmd, tm, numthreads, validate=False):
        if scancmd.stopped: return
        if self.ritem!=None:
            self.ritem.scan(scancmd, tm, numthreads, validate)
        else:
            if validate:
                self.runtime+=tm
            else: scancmd.acquire_data(tm)
    
    def calc_runtime(self, scancmd, numthreads):
        runtime=self.runtime+self.litem.calc_runtime(scancmd, numthreads)
        if self.ritem!=None: runtime+=self.ritem.calc_runtime(scancmd, numthreads)
        return runtime

class MainLoopScanNode(LoopScanNode):
        
    def scan(self, scancmd, numthreads=1, validate=False):
        super(MainLoopScanNode, self).scan(scancmd, self.litem.shoot_time, numthreads, validate)