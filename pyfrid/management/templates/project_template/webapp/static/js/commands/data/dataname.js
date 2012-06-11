Pyfrid.{{webclass}}= Ext.extend(Ext.FormPanel, {
	initComponent:function() {
	    this.name_field = new Ext.form.TextField({
	    	fieldLabel: "Data name",
	        emptyText:'Type a name...',
	        allowBlank: false,
	        width: 300
	    });
	    this.comment_field = new Ext.form.TextField({
	    	fieldLabel: 'Comment',
	    	emptyText:'Type a comment...',
	    	width: 300
	    });
		Ext.apply(this,{
		    bodyStyle:'padding:5px 5px 0',
			items:[this.name_field,this.comment_field]
		});
		Pyfrid.{{webclass}}.superclass.initComponent.apply(this, arguments);
		this.name_field.on("valid",function(form,field){this.fireEvent("cmdchanged",this.generateCommand());},this);
		this.comment_field.on("valid",function(form,field){this.fireEvent("cmdchanged",this.generateCommand());},this);
   },
   generateCommand:function(){
	   var expname=this.name_field.getValue();
	   var comment=this.comment_field.getValue();
	   if (expname=='')
		   return ''
	   if (comment=='')
		   cmd=this.objname+' \"'+expname+'\"';
	   else
		   cmd=this.objname+' \"'+expname+'\" '+' \"'+comment+'\"';
	   return cmd;
   },
   updateData:function(){},
   clearCommand:function(){
   		this.name_field.setValue('');
   		this.comment_field.setValue('');
   }
});