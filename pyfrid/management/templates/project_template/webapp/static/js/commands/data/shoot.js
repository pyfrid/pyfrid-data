Pyfrid.TimeScanFieldSet= Ext.extend(Ext.form.FieldSet, {
	initComponent:function() {
	    this.time_field=new Pyfrid.TimeTextField();
	    this.repeat_field=new Pyfrid.RepeatTextField();
		Ext.apply(this,{
			layout:'form',
			title: '',
			collapsible:false,
			items:[this.time_field,this.repeat_field]
		});
		Pyfrid.TimeScanFieldSet.superclass.initComponent.apply(this, arguments);
		this.addEvents("valid");
		this.time_field.on("valid",this.onValueValid,this);
		this.repeat_field.on("valid",this.onValueValid,this);
	},
    generateCommand:function(cmdname){
	   var t=this.time_field.getValue();
	   var r=this.repeat_field.getValue();
	   if (t=="" && r=="")
		   return "";
	   return cmdname+" "+t+' '+r;
   },
   isValid:function(){
        if (this.time_field.isValid() && this.repeat_field.isValid())
            return true;
        return false;
   },
   clearCommand:function(){
		this.time_field.setValue('');
		this.repeat_field.setValue('');
   },
   onValueValid:function(){
	if (this.isValid())
		this.fireEvent("valid");
   }
});


Pyfrid.{{webclass}}=Ext.extend(Pyfrid.BaseCommandInterface,{
	initComponent:function() {
	    this.timescan=new Pyfrid.TimeScanFieldSet({frame:true});
	    Ext.apply(this,{
	    	monitorValid:true,
			autoScroll:true,
			items: [this.timescan]
		});
		Pyfrid.{{webclass}}.superclass.initComponent.apply(this, arguments);
		this.addEvents("cmdchanged");
		this.timescan.on("valid",function(){
	    	this.fireEvent("cmdchanged",this.generateCommand());
	    },this);
	},
	generateCommand:function(){
		if (this.timescan.isValid())
			return this.timescan.generateCommand(this.objname);
		return '';
	},
	updateData:function(data){
	},
	clearCommand:function(){
		this.timescan.clearCommand();
	}
});


