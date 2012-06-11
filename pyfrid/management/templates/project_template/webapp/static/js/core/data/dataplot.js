Pyfrid.BasePlot2DDataInterface = Ext.extend(Pyfrid.BasePlotModuleInterface, {
	xdevinfo:[],
	ydevinfo:[],
	xmenu:true,
	ymenu:true,
	initComponent : function() {
		Pyfrid.BasePlot2DDataInterface.superclass.initComponent.apply(this, arguments);
		this.addEvents("setxdev", "setydev");
		if (this.ymenu){
			this.ydevsMenu=new Ext.menu.Menu({});
			this.addMenuItem(this.ydevinfo, this.ydevsMenu, "setydev");
			this.toolbar.insertButton(0, {
				text: "Y axis",
				menu: this.ydevsMenu
			});	
		}
		if (this.xmenu){ 
			this.xdevsMenu=new Ext.menu.Menu({});
			this.addMenuItem(this.xdevinfo, this.xdevsMenu, "setxdev");
			this.toolbar.insertButton(0, {
				text: "X axis",
				menu: this.xdevsMenu
			});
		}
		this.on("setxdev", this.setXDevice);
		this.on("setydev", this.setYDevice);
	},
    addMenuItem:function(info, root_menu, signal){
    	for (var i=0;i<info.length;i++){
    		var item=info[i];
    		if (item.type=="group"){
    			var menu=new Ext.menu.Menu();
    			this.addMenuItem(item.children, menu, signal);
    			root_menu.addItem({text:item.name,iconCls:item.iconCls,menu:menu}); 
    		}else{
    			root_menu.addItem({
					scope:     this,
					text:      item.name,
					iconCls:   item.iconCls,
					item_id:   id,
					item_type: item.type,
					item_name: item.name,
					handler:   function(item){
						this.fireEvent(signal, item.item_name);
					}
    			});
    		}
    	}
    },
    setXDevice:function(name){
    	this.router.set_xdev(name);
    },
    setYDevice:function(name){
    	this.router.set_ydev(name);
    }
});