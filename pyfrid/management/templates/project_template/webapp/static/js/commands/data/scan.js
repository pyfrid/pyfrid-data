Pyfrid.DeviceComboBox = Ext.extend(Ext.form.ComboBox,{
	initComponent:function(){
			Ext.apply(this,{
				fieldLabel: 'Device',
		    	scope: this,
		        displayField:'device',
		        typeAhead: true,
		        mode: 'local',
		        triggerAction: 'all',
		        emptyText:'Choose a device...',
		        selectOnFocus:false,
		        width:200,
		        allowBlank: false
			});
		Pyfrid.DeviceComboBox.superclass.initComponent.apply(this, arguments);
	}
});

Pyfrid.StartTextField = Ext.extend(Ext.form.TextField,{
	initComponent:function() {
		Ext.apply(this,{
			fieldLabel: 'Start',
	        allowBlank: false,
	        width:200,
	        emptyText:'Type a start value...',
		});
		Pyfrid.StartTextField.superclass.initComponent.apply(this, arguments);
	}
});

Pyfrid.StepTextField = Ext.extend(Ext.form.TextField,{
	initComponent:function() {
		Ext.apply(this,{
			fieldLabel: 'Step',
	        allowBlank: false,
	        width:200,
	        emptyText:'Type a step value...',
		});
		Pyfrid.StepTextField.superclass.initComponent.apply(this, arguments);
	}
});

Pyfrid.EndTextField = Ext.extend(Ext.form.TextField,{
	initComponent:function() {
		Ext.apply(this,{
			fieldLabel: 'End',
	        allowBlank: false,
	        width:200,
	        emptyText:'Type an end value...',
		});
		Pyfrid.EndTextField.superclass.initComponent.apply(this, arguments);
	}
});

Pyfrid.TimeTextField = Ext.extend(Ext.form.TextField,{
	initComponent:function() {
		Ext.apply(this,{
			fieldLabel: 'Time',
	        allowBlank: false,
	        width:200,
	        emptyText:'Type a time value...',
		});
		Pyfrid.EndTextField.superclass.initComponent.apply(this, arguments);
	}
});


Pyfrid.RepeatTextField = Ext.extend(Ext.form.TextField,{
	initComponent:function() {
		Ext.apply(this,{
			fieldLabel: 'Repeat',
	        allowBlank: false,
	        width:200,
	        emptyText:'Type a repeat value...',
		});
		Pyfrid.RepeatTextField.superclass.initComponent.apply(this, arguments);
	}
});

Pyfrid.BaseDevFieldSet= Ext.extend(Ext.form.FieldSet, {
	initComponent:function() {
	    Ext.apply(this,{
	    	layout:'form',
	    	anchor: '95%',
	    	collapsed:false,
	    });
		Pyfrid.BaseDevFieldSet.superclass.initComponent.apply(this, arguments);
		this.addEvents("valid");
		for (var i=0;i<this.items.length;i++){
			this.get(i).on("valid",this.onValueValid,this);
		}
	},
	generateCommand: function(){
		var cmd=[this.get(0).getValue(),
		         this.get(1).getValue(),
		         this.get(2).getValue()].join(" ");
		return cmd;
	},
	isValid: function(){
		for (var i=0;i<this.items.length;i++){
			if (!this.get(i).isValid())
				return false;
		}
		return true;
	},
	onValueValid:function(){
		if (this.isValid())
			this.fireEvent("valid")
	}
});


Pyfrid.LoopDevFieldSet= Ext.extend(Pyfrid.BaseDevFieldSet, {
	onAddDeviceClick: function(){
		var obj=new Pyfrid.BaseDevFieldSet({
			scope:this,
			buttonAlign: 'left',
			title: 'Additional device',
			collapsible:true,
			items:[
			    new Pyfrid.DeviceComboBox({store: this.devStore}),
			    new Pyfrid.StartTextField(),
			    new Pyfrid.StepTextField(),
			]
		});
		obj.addButton({text: 'Delete'},function(){
			   this.deleteObject(obj);
		},this);
		obj.on("valid",this.onValueValid,this);
		this.add(obj);
		this.doLayout();
	},
	deleteObject: function(obj){
		this.remove(obj,true);
		this.doLayout();
		this.onValueValid();
	},
	generateCommand: function(){
		var cmd=[this.get(0).getValue(),
				this.get(1).getValue(),
				this.get(2).getValue(),
				this.get(3).getValue()].join(" ");
		var _cmd='';
		if (this.items.length>4){
			items=[];
			for (var i=4;i<this.items.length;i++){
				items.push(this.get(i).generateCommand());
			}
			_cmd='[ '+items.join(" ")+' ]';
		}
		if (_cmd!='')
			cmd+=' '+_cmd;
		return cmd;
	}
});

Pyfrid.MainLoopFieldSet= Ext.extend(Pyfrid.LoopDevFieldSet, {
	generateCommand: function(){
	    var _cmd='';
		var cmd=[this.get(0).getValue(),
				this.get(1).getValue(),
				this.get(2).getValue(),
				this.get(3).getValue(),
				this.get(4).getValue()].join(" ");
			if (this.items.length>5){
				items=[];
				for (var i=5;i<this.items.length;i++){
					items.push(this.get(i).generateCommand());
				}
				_cmd=items.join(" ");
				_cmd=['[',_cmd,']'].join(" ");
			}
			if (_cmd!="")
				cmd+=" "+_cmd;
			return cmd;
	},
	clearCommand:function(){
		this.get(0).setValue("");
		this.get(1).setValue("");
		this.get(2).setValue("");
		this.get(3).setValue("");
		this.get(4).setValue("");
		if (this.items.length>5){
			while (this.items.length>5)
				this.remove(this.get(this.items.length-1),true);
			this.doLayout();
		}
	}
});

Pyfrid.ScanFieldSet= Ext.extend(Pyfrid.LoopDevFieldSet, {
	initComponent:function() {
		Ext.apply(this,{
			collapsible:false,
			buttons:[{
				scope: this,
	        	text: 'Add loop',
	        	handler: this.onAddLoopClick
	        }]
		});
		Pyfrid.ScanFieldSet.superclass.initComponent.apply(this, arguments);
	},
   onAddLoopClick:function(){
	   var obj=new Pyfrid.LoopDevFieldSet({
		   scope:this,
		   parentLoop: this,
		   devStore:this.devStore,
		   collapsible:true,
		   title: 'Additional loop',
		   items:[
				    new Pyfrid.DeviceComboBox({store: this.devStore}),
				    new Pyfrid.StartTextField(),
				    new Pyfrid.StepTextField(),
				    new Pyfrid.EndTextField(),
		   ]
	   });
	   obj.addButton({text: 'Add device'},obj.onAddDeviceClick,obj);
	   obj.addButton({text: 'Delete'},function(){
		   this.deleteObject(obj);
	   },this);
	   obj.on("valid",this.onValueValid,this);
	   this.add(obj);
	   this.doLayout();
   },
   generateCommand:function(){
	   var cmd=this.get(0).generateCommand();
	   var _cmd='';
	   if (this.items.length>1){
		   for (var i=1;i<this.items.length;i++){
			   _cmd+=' (';
			   _cmd+=' '+this.get(i).generateCommand();
		   }
		   for (var i=1;i<this.items.length;i++)
			   _cmd+=') ';
	   }
	   if (_cmd!='')
		   cmd+=_cmd;
	   return cmd;
   },
   clearCommand:function(){
	   this.get(0).clearCommand();
	   if (this.items.length>1){
		   while(this.items.length>1)
			   this.remove(this.get(this.items.length-1),true);
	   }
	   this.doLayout();
}
});


Pyfrid.ScanCmdFieldSet=Ext.extend(Pyfrid.BaseDevFieldSet,{
	initComponent:function() {
		this.devStore=new Ext.data.ArrayStore({
			fields:["device"],
			autoLoad:false,
			autoDestroy: false,
			data:[["dummy1"],["dummy1"]]
		});
		var main_fieldset  = new Pyfrid.MainLoopFieldSet({
	    	devStore: this.devStore,
	    	title: 'Main loop',
	    	items:[
				    new Pyfrid.DeviceComboBox({scope:this,store: this.devStore}),
				    new Pyfrid.StartTextField(),
				    new Pyfrid.StepTextField(),
				    new Pyfrid.EndTextField(),
				    new Pyfrid.TimeTextField()
			]
	    });
	    main_fieldset.addButton({text: 'Add device'},main_fieldset.onAddDeviceClick,main_fieldset);
	    
	    var scanfield=new Pyfrid.ScanFieldSet({
	    	scope:this,
	    	objname: this.objname,
	    	title:'',
	    	devStore: this.devStore,
	    	items: main_fieldset
	    });
	    Ext.apply(this,{
			autoScroll:true,
			collapsible:false,
			items: scanfield,
	        title: ''
		});
		Pyfrid.ScanCmdFieldSet.superclass.initComponent.apply(this, arguments);
	},
	generateCommand:function(cmdname){
		   var cmd=this.get(0).generateCommand();
		   if (cmd!=='')
			cmd=cmdname+ " "+cmd;
		   return cmd;
	},
	clearCommand:function(){
		   this.get(0).clearCommand();
		   this.doLayout();
	}
});


Pyfrid.{{webclass}}=Ext.extend(Pyfrid.BaseCommandInterface,{
	devices:{{devices}},
	initComponent:function() {
	    this.loopscan=new Pyfrid.ScanCmdFieldSet({frame:true});
	    var _data=[];
		for (var i=0;i<this.devices.length;i++)
			_data.push([this.devices[i]]);
		this.loopscan.devStore.loadData(_data);
	    Ext.apply(this,{
	    	monitorValid:true,
			autoScroll:true,
			items: [this.loopscan]
		});
		Pyfrid.{{webclass}}.superclass.initComponent.apply(this, arguments);
		this.addEvents("cmdchanged");
		this.loopscan.on("valid",function(){
	    	this.fireEvent("cmdchanged",this.generateCommand());
	    },this);
	},
	generateCommand:function(){
		return this.loopscan.generateCommand(this.objname);
	},
	clearCommand:function(){
		this.loopscan.clearCommand();
	}
});
