from pyfrid.utils import format_status
from pyfrid.core import BaseCommand

class BaseDataNameCommand(BaseCommand):
    
    data_module=None
    
    def __init__(self, *args, **kwargs):
        super(BaseDataNameCommand,self).__init__(*args, **kwargs)
        assert self.data_module!=None, "data_module is None"

    def grammar(self):
        from pyfrid.modules.system.vm.leplvm import STRCONST
        return (STRCONST, 0, 2)
        
    def execute(self, *args, **kwargs):
        ln=len(args)            
        if ln==1:
            name, comment=args[0], ""
        elif ln==2:
            name, comment=args
        self.data_module.set_dataname(name, comment)
        self.info("Current status of {0} {1}".format(self.data_module.name,format_status(self.data_module.call_status(),(30,15,5))))
        
    def validate(self,*args, **kwargs):
        res=self.data_module.validate_name(*args)
        if res: self.data_module._name_preset=True
        return res
    
    def runtime(self, *args, **kwargs):
        return 0.0
                 
        
