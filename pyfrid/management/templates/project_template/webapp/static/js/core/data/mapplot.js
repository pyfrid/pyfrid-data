
Pyfrid.BaseMapModuleInterface = Ext.extend(Pyfrid.BasePlotModuleInterface, {
			initComponent : function() {
				this.center=[null, null];
				this.centerMenu = new Ext.menu.Menu({
					scope : this,
					items : [{
								text : 'Set',
								scope : this,
								handler : function(){
									this.startClickMonitoring(this.onCenterChosen, this);
								}
							}, '-', {
								text : 'Reset',
								scope : this,
								handler : this.onResetCenterClick
							}]
				});	
				Pyfrid.BaseMapModuleInterface.superclass.initComponent.apply(this, arguments);
				this.toolbar.insertButton(0,{
								text : "Center",
								iconCls : 'center-menu-icon',
								menu : this.centerMenu,
								scope : this
				});
				this.toolbar.doLayout();
			},
			
			onResetCenterClick : function(item) {
				this.router.reset_center(function(){
					this.imgbox.updateCanvas();
				},this);
			},
			
			onCenterChosen:function(coord_x, coord_y){
				console.log([coord_x, coord_y]);
				coord_y=this.imgbox.getBox().height - coord_y;
				console.log([coord_x, coord_y]);
				this.center=[coord_x, coord_y];
				this.router.set_center(coord_x, coord_y, function(){
					this.imgbox.updateCanvas();
				},this);
				this.stopClickMonitoring(this.onCenterChosen)
			}
		});
