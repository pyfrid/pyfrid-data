Pyfrid.PlotCanvas = Ext.extend(Ext.BoxComponent, {
	parent : null,
	interval : 1000,
	initComponent : function() {
		Ext.apply(this, {
					id : 'livecomponent' + this.parent.objname,
					autoEl : {
						tag : 'div',
						cls : 'live_container',
						children : [{
									tag : 'canvas',
									id : 'tempCanvas' + this.parent.objname,
									cls : 'cls_live_temp'
								}, {
									tag : 'canvas',
									id : 'imgCanvas' + this.parent.objname,
									cls : 'cls_live_img'
								}]
					}
				});
		this.id = 0;
		this.img = new Image();
		this.update_task = null;
		Pyfrid.PlotCanvas.superclass.initComponent.apply(this, arguments);
	},
	onRender : function(ct, position) {
		Pyfrid.PlotCanvas.superclass.onRender.call(this, ct, position);
		this.temp_canvas = Ext.get('tempCanvas' + this.parent.objname).dom;
		this.canvas = Ext.get("imgCanvas" + this.parent.objname).dom;
		this.ctx = this.canvas.getContext("2d");
		this.temp_ctx = this.temp_canvas.getContext("2d");
		this.updateCanvasSize(this.width, this.height);
		var cvs = this.canvas, ctx = this.ctx, _img = this.img, _this = this;
		this.img.onload = function() {
			try {
				ctx.drawImage(_img, 0, 0, _img.width, _img.height, 0, 0,
						cvs.width, cvs.height);
			} catch (e) {

			}
		}
	},
	onResize : function(aw, ah, w, h) {
		Pyfrid.PlotCanvas.superclass.onResize.call(this, aw, ah, w, h);
		this.parent.router.resize(aw, ah, function(response) {
					this.updateCanvasSize(aw, ah);
					this.updateCanvas(response);
				}, this);
	},
	updateCanvasSize : function(w, h) {
		this.canvas.width = w;
		this.canvas.height = h;
		this.temp_canvas.width = w;
		this.temp_canvas.height = h;
	},
	updatePlot : function() {
		this.parent.router.get_image(this.id, function(response) {
					this.updateCanvas(response);
				}, this);
	},
	updateCanvas : function(response) {
		if (response != null) {
			this.img.src = "data:image/png;base64," + response.image;
			this.id = response.id;
		}
	},
	drawRect : function(x0, y0, x1, y1) {
		var x = Math.min(x1, x0), y = Math.min(y1, y0), w = Math.abs(x1 - x0), h = Math
				.abs(y1 - y0);
		this.temp_ctx.clearRect(0, 0, this.temp_canvas.width,
				this.temp_canvas.height);
		if (!w || !h) {
			return;
		}
		this.temp_ctx.strokeRect(x, y, w, h);
	},
	clearRect : function(x0, y0, x1, y1) {
		this.temp_ctx.clearRect(0, 0, this.temp_canvas.width,
				this.temp_canvas.height);
	},
	start : function() {
		this.parent.router.activate(function() {
					this.update_task = Ext.TaskMgr.start({
								scope : this,
								run : function() {
									this.updatePlot();
								},
								interval : this.interval
							});
				}, this);

	},
	stop : function() {
		this.parent.router.deactivate(function() {
					if (this.update_task !== null)
						Ext.TaskMgr.stop(this.update_task);
				}, this);
	}
});

Pyfrid.PlotSettingsWindow = Ext.extend(Pyfrid.CascadeWindow, {
	parent : null,
	initComponent : function() {
		var fm = Ext.form;
		var store = new Ext.data.ArrayStore({
			fields : [{
						name : 'name'
					}, {
						name : 'value'
					}, {
						name : 'units'
					}, {
						name : 'descr'
					}, {
						name : 'expected'
					}, {
						name : 'type'
					}]
		});
		// the column model has information about grid columns
		// dataIndex maps the column to the specific data field in
		// the data store (created below)
		var cm = new Ext.grid.ColumnModel({
			// specify any defaults for each column
			defaults : {
				sortable : false
				// columns are not sortable by default
			},
			columns : [{
						header : 'Setting',
						dataIndex : 'name',
						width : 120,
						css: "font-weight: bold; font-size: 16px"
					}, {
						header : 'Value',
						dataIndex : 'value',
						width : 50,
						editor : new Ext.form.TextField()
					}, {
						header : 'Units',
						dataIndex : 'units',
						width : 50
					}, {
						header : 'Description',
						dataIndex : 'descr',
						width : 100
					}],
			editors : {
				'default' : new Ext.grid.GridEditor(new Ext.form.TextField({})),
				'string' : new Ext.grid.GridEditor(new Ext.form.TextField({})),
				'int' : new Ext.grid.GridEditor(new Ext.form.NumberField({})),
				'float' : new Ext.grid.GridEditor(new Ext.form.NumberField({})),
			    'boolean': new Ext.grid.GridEditor(new
					 Ext.form.ComboBox({
					 	typeAhead: true,
    					triggerAction: 'all',
    					lazyRender:true,
   	 					mode: 'local',
					 	valueField:'value',
    					displayField:'name',
    					store: new Ext.data.ArrayStore({
        					fields: [
            					'value',
            					'name'],
        					data: [[true, 'true'], [false, 'false']]
    					})
					 }))
			},
			getCellEditor : function(colIndex, rowIndex) {
				var field = this.getDataIndex(colIndex);
				if (field == 'value') {
					var rec = store.getAt(rowIndex);
					var expected=rec.get('expected');
					var type = rec.get('type');
					if (!expected) expected=[];
					if (!type) type='default';
					if (expected.length!=0){
						var data=new Array();
						for (var i=0;i<expected.length;i++)
							data.push([expected[i], expected[i]]);
						return new Ext.grid.GridEditor(new Ext.form.ComboBox({
						 	typeAhead: true,
	    					triggerAction: 'all',
	    					lazyRender:true,
	   	 					mode: 'local',
						 	valueField:'value',
	    					displayField:'name',
	    					store: new Ext.data.ArrayStore({
	        					fields: ['value','name'],
	        					data: data
	    					})
					 	}));
					 	
					}
					return this.editors[type];
				}
				return Ext.grid.ColumnModel.prototype.getCellEditor.call(this,
						colIndex, rowIndex);
			}
		});
		// create the editor grid
		this.grid = new Ext.grid.EditorGridPanel({
			store : store,
			cm : cm
		});
		var applyBtn = new Ext.Button({
			scope : this,
			text : "Apply",
			handler : function() {
				var mr=this.grid.getStore().getModifiedRecords();
				var output=new Array();
				for (var i=0;i<mr.length;i++){
					output.push(mr[i].data)
				}
				this.parent.router.set_settings(output, function(data){
					this.grid.store.loadData(data);
				}, this);
			}
		});
		var reloadBtn = new Ext.Button({
			scope : this,
			text : "Reload",
			handler : function() {
				this.updateSettings();
			}
		});
		var cancelBtn = new Ext.Button({
			scope : this,
			text : "Cancel",
			handler : function() {
				this.close()
			}
		});
		Ext.apply(this, {
			layout : 'fit',
			cascadeOnFirstShow : true,
			items : this.grid,
			width : 400,
			height : 400,
			closeAction : 'hide',
			buttons : [applyBtn, reloadBtn, cancelBtn]
		});
		Pyfrid.PlotSettingsWindow.superclass.initComponent.apply(this, arguments);
	},
	updateSettings : function(settings) {
		this.parent.router.get_settings(function(data) {
					this.grid.store.loadData(data);
				}, this);
	}
});

Pyfrid.BasePlotModuleInterface = Ext.extend(Pyfrid.CascadeWindow, {
			router : null,
			initComponent : function() {
				this.area_selector = false;
				this.selection_on = false;
				this.x0y0 = [0.0, 0.0];
				this.zoomMenu = new Ext.menu.Menu({
					scope : this,
					items : [{
								text : 'Set',
								scope : this,
								handler : function(){
									this.startSelectionMonitoring(this.onZoomSelected, this);
								}
							}, '-', {
								text : 'Clear',
								scope : this,
								handler : this.onZoomClearClick
							}]
				});
				this.maskMenu = new Ext.menu.Menu({
					scope : this,
					items : [{
								text : 'Set',
								scope : this,
								handler : function(){
									this.startSelectionMonitoring(this.onMaskSelected, this);
								}
							}, '-', {
								text : 'Clear last',
								scope : this,
								handler : this.onMaskClearLastClick
							}, '-', {
								text : 'Clear all',
								scope : this,
								handler : this.onMaskClearAllClick
							}]
				});
				this.dataCoordItem = new Ext.Toolbar.TextItem('Coord.: 0, 0');
				this.optionsWindow = new Pyfrid.PlotSettingsWindow({
					parent : this,
					title : "Settings"
				});	
				this.imgbox = new Pyfrid.PlotCanvas({
					region : 'center',
					parent : this
				});	
				this.toolbar = new Ext.Toolbar({
					items : [{
								text : "Zoom",
								iconCls : 'zoom-menu-icon',
								menu : this.zoomMenu,
								scope : this
							},
							{
								text : "Mask",
								iconCls : 'mask-menu-icon',
								menu : this.maskMenu,
								scope : this
							},
							{
								text : "Options",
								iconCls : 'plot-options-menu-icon',
								handler : this.onOptionsClick,
								scope : this
							}, "->", this.dataCoordItem]
				});
				Ext.apply(this, {
					tbar : this.toolbar,
					title: this.objname,
					closeAction : 'hide',
					layout : 'border',
					maximizable : true,
					minimizable : true,
					height : 480,
					width : 640,
					minHeight : 400,
					minWidth : 400,
					items : [this.imgbox]
				});
				Pyfrid.BasePlotModuleInterface.superclass.initComponent.apply(
						this, arguments);
				this.addEvents("selectionactive", "selectionactive", "selectionend");
			},
			onHide : function() {
				Pyfrid.BasePlotModuleInterface.superclass.onHide.call(this);
				this.imgbox.stop();
			},
			onShow : function() {
				Pyfrid.BasePlotModuleInterface.superclass.onShow.call(this);
				this.imgbox.el.on("mousedown", function(e, t) {
					var mouse_x = e.getPageX(), mouse_y = e.getPageY();
					var coord_x = mouse_x - this.imgbox.getBox().x;
					var coord_y = mouse_y - this.imgbox.getBox().y;
					this.fireEvent("selectionstart", coord_x, coord_y);
					this.showCoord(mouse_x, mouse_y);
				}, this);
				this.imgbox.el.on("mousemove", function(e, t) {
					var mouse_x = e.getPageX(), mouse_y = e.getPageY();
					var coord_x = mouse_x - this.imgbox.getBox().x;
					var coord_y = mouse_y - this.imgbox.getBox().y;
					this.fireEvent("selectionactive", coord_x, coord_y);
				}, this);
				this.imgbox.el.on("mouseup", function(e, t) {
					var mouse_x = e.getPageX(), mouse_y = e.getPageY();
					var coord_x = mouse_x - this.imgbox.getBox().x;
					var coord_y = mouse_y - this.imgbox.getBox().y;
					var X1 = Math.min(this.x0y0[0], coord_x);
					var Y1 = Math.min(this.imgbox.getBox().height
									- this.x0y0[1], this.imgbox
									.getBox().height
									- coord_y);
					var X2 = Math.max(this.x0y0[0], coord_x);
					var Y2 = Math.max(this.imgbox.getBox().height
									- this.x0y0[1], this.imgbox
									.getBox().height
									- coord_y);
					this.fireEvent("selectionend", X1, Y1, X2, Y2);
				}, this);
				this.imgbox.start();
			},
			minimize : function() {
				this.setSize(this.minWidth, this.minHeight);
			},
			onOptionsClick : function() {
				this.optionsWindow.updateSettings();
				this.optionsWindow.show();
			},
			showCoord : function(mouse_x, mouse_y) {
				var coord_x = mouse_x - this.imgbox.getBox().x;
				var coord_y = this.imgbox.getBox().height - mouse_y
						+ this.imgbox.getBox().y;
				this.router.get_coordinates(coord_x, coord_y, function(resp) {
							this.dataCoordItem.getEl().update("Coord.: "
									+ resp[0].toFixed(2) + ', ' + resp[1].toFixed(2));
						}, this);
			},
			activateSelection:function(coord_x, coord_y){
				this.x0y0[0]=coord_x;this.x0y0[1]=coord_y;
				this.draw_active=true;
			},
			
			drawSelection:function(coord_x, coord_y){
				if (this.draw_active)
					this.imgbox.drawRect(this.x0y0[0], this.x0y0[1], coord_x, coord_y);
			},
			
			clearSelection:function(coord_x, coord_y){
				this.imgbox.clearRect(this.x0y0[0], this.x0y0[1], coord_x, coord_y);
				this.draw_active=false;
			},
			
			startSelectionMonitoring:function(callback, scope){
				this.clearSelectionListeners();
				this.on("selectionstart",  this.activateSelection, this);
				this.on("selectionactive", this.drawSelection, this);
				this.on("selectionend",    this.clearSelection, this);
				this.on("selectionend",    callback, scope);
			},
			
			stopSelectionMonitoring:function(callback){
				this.un("selectionstart",  this.activateSelection, this);
				this.un("selectionactive", this.drawSelection)
				this.un("selectionend", this.clearSelection, this);
				this.un("selectionend", callback)
			},
			
			removeListeners:function(eventName, fn, scope){
				var ce = this.events[eventName.toLowerCase()];
				if (typeof ce == "object"){
  					if (typeof fn == "function")
     					ce.removeListener(fn, scope);
  					else
     					ce.clearListeners();
					} 
			},
			
			clearSelectionListeners:function(){
				this.removeListeners("selectionstart");
				this.removeListeners("selectionactive");
				this.removeListeners("selectionend");
			},
			
			startClickMonitoring:function(callback, scope){
				this.clearSelectionListeners();
				this.on("selectionstart",  callback, scope);
			},
			
			stopClickMonitoring:function(callback){
				this.un("selectionstart",  callback, this);
			},
			
			onZoomSelected:function(X1, Y1, X2, Y2){
				this.router.set_zoom(X1, Y1, X2, Y2, function(){
					this.imgbox.updateCanvas();
				},this);
				this.stopSelectionMonitoring(this.onZoomSelected);
			},
			
			onZoomClearClick : function(item) {
				this.router.clear_zoom(function(){
					this.imgbox.updateCanvas();
				},this);
			},
			
			onMaskSelected:function(X1, Y1, X2, Y2){
				this.router.add_mask(X1, Y1, X2, Y2, function(){
					this.imgbox.updateCanvas();
				},this);
				this.stopSelectionMonitoring(this.onMaskSelected);
			},
			
			onMaskClearLastClick : function(item) {
				this.router.clear_last_mask(function(){
					this.imgbox.updateCanvas();
				},this);
			},
			
			onMaskClearAllClick : function(item) {
				this.router.clear_mask(function(){
					this.imgbox.updateCanvas();
				},this);
			}
			
		});
