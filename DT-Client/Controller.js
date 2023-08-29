let gateway;
let model;

function init(){
    getSensorValues();

    getSystemStatus();
    drawConsoleTempSelector();

    getAlertMessages()

    getEventMessages();
}

//EVENTS

//enseñar info de alerta al hacer click sobre aviso el mapa
function onClickSystemWarningIcon(id){
	//enseñar modal de alerta al hacer click
	var alert_info = getAlertInfoByWarnIconId(id);
	setAlertModalInfo(id);
}

//solicitar arranque del sistema
function onClickStartButton(){
	//fetch http de arranque del sistema
	if(home.status==0){
		var my_events = postHttpEventMessage(
			{id: 1,
				tipo:"Sistema",
				msg:"Arranque manual solicitado",
				params: ""});

		if(my_events){
			home.events = my_events
			//Mensaje de información al usuario
			swal("Se ha solicitado el arranque del sistema", {
				icon : "info",
				buttons: {
					confirm: {
						className : 'btn btn-info'
					}
				},
			});
		}

		//Feedback gráfico
		drawEventMessages();
	} else{
		swal("El sistema ya está en funcionamiento", {
			icon : "info",
			buttons: {
				confirm: {
				className : 'btn btn-info'
				}
			},
		});
	}
}

//solicitar apagado del sistema
function onClickShutdownButton(){
	//fetch http de apagado del sistema
	if(home.status==1){
		let my_events = postHttpEventMessage(
			{id: 0,
				tipo:"Sistema",
				msg:"Detención manual solicitada",
				params: ""})

		if(my_events){
			home.events = my_events
			//Mensaje de información al usuario
			swal("Se ha solicitado la detención del sistema", {
			icon : "info",
			buttons: {
				confirm: {
				className : 'btn btn-info'
				}
			},
		});
		}



		//Feedback gráfico
		drawEventMessages();
	
	} else{
		swal("El sistema está actualmente apagado", {
			icon : "info",
			buttons: {
				confirm: {
				className : 'btn btn-info'
				}
			},
		});
	}
	//feedback gráfico
	drawEventMessages();
}

//solicitar cambio de temperatura desde la consola
function onClickSaveConsoleButton(){
	home.consoleConsigTemp =  $("#temperature-console-selector").val().toString();
	setConsoleTemp();
	let my_events = postHttpEventMessage(
			{id: 1,
				tipo:"Temperatura",
				msg:"Ajuste temperatura",
				params: home.consoleConsigTemp});

	getEventMessages()

	//Mensaje de información al usuario
			swal("Se ha solicitado un ajuste de temperatura", {
				icon : "info",
				buttons: {
					confirm: {
						className : 'btn btn-info'
					}
				},
			});
}

//salir de la consola
function onClickExitConsoleButton(){
	$("#temperature-console-selector").val(home.consoleConsigTemp);
}

//solicitar arranque inteligente programado desde la modal de arranque
function onClickSaveBootPredictionModalButton() {
	let sch_time = $("#boot-prediction-time").val(); // formato --> "YYYY-MM-DDTHH:MM"
	let sch_consig_temp = home.consoleConsigTemp;

	//fetch http de programar el encendido
	let event = postHttpBootPrediction(
		{id: 3,
			tipo: "Sistema",
			msg: "Arranque inteligente programado",
			params: sch_time
		});

	if(events){
		//Guardar eventos en el modelo
		home.events = events;
		//Mostrar eventos
		drawEventMessages();
	}
}

//FUNCTIONS

//cargar alertas
function getAlertMessages(){
    var alerts = getHttpAlertMessages();
    if(alerts){
        //Guardar alertas en el modelo
        home.alerts = alerts;
        //Mostrar alertas en la vista
        drawSystemStatus();
        drawAlertMessages();
    }
}

//cargar actividad de los sensores
function getSensorValues(){
    var values = getHttpSensorValues();
    if(values){
        //Guardar alertas en el modelo
        updateValues(values);
        //Mostrar valores en la vista
        drawSensorValues();
        setConsoleTemp();
    }

}

//cargar eventos del sistema
function getEventMessages(){
	let events = getHttpEventMessages();
	if(events){
		//Guardar eventos en el modelo
		home.events = events;
		//Mostrar eventos
		drawEventMessages();
	}
}

//cargar estado del sistema
function getSystemStatus(){
	var status = getHttpSystemStatus();
	if(status){
		//Guardar estado en el modelo
		updateStatus(status);
	}
	drawSystemStatus();
}


//GRAPHICS

//mostrar alertas
function drawAlertMessages(){
    //Limpiar cuadro de alertas
    $("#alerts-card").empty();
    for (let i = 0; i < home.alerts.length; i++) {
        //Dibujar alerta
        var alert_info = getAlertInfoByDesc(home.alerts[i].alert_desc);
        var alert_datetime = formatDatetime(home.alerts[i].datetime);

        var alert = ""

        switch(alert_info.risk) {
            case "Alto":
                alert = '<div class="d-flex"><div class="flex-1 ml-3 pt-1">' +
                    '<h6 class="text-uppercase fw-bold mb-1">' + alert_info.component +
                    '<span class="text-danger pl-3">' + alert_info.risk + '</span></h6>' +
                    '<span class="text-muted">' + alert_info.msg + '</div><div class="float-right pt-1">' +
                    '<small class="text-muted">' + alert_datetime + '</small></div></div>' +
                    '<div class="separator-dashed"></div>';
                break;

            case "Medio":
                alert = '<div class="d-flex"><div class="flex-1 ml-3 pt-1">' +
                    '<h6 class="text-uppercase fw-bold mb-1">' + alert_info.component +
                    '<span class="text-warning pl-3">' + alert_info.risk + '</span></h6>' +
                    '<span class="text-muted">' + alert_info.msg + '</div><div class="float-right pt-1">' +
                    '<small class="text-muted">' + alert_datetime + '</small></div></div>' +
                    '<div class="separator-dashed"></div>';
                break;

            case "Bajo":
                break;
        }

        $("#alerts-card").append(alert)
    }

    if(home.alerts.length == 0){
        let alert = '<div class="d-flex"><div class="flex-1 ml-3 pt-1">' +
                    '<span class="text-muted"> No hay alertas </div></div>'

        $("#alerts-card").append(alert)
    }
}

//mostrar actividad de los sensores
function drawSensorValues(){
    var pb_temp = Math.round(parseFloat(home.sensorValues.tempPB.replace(',','.')) * 10) / 10;
    Circles.create({
			id:'circles-1',
			radius:45,
			value: pb_temp+20,
			maxValue:55,
            minValue: 0,
			width:7,
			text: pb_temp,
			colors:['#00cde8', '#ab0505'],
			duration:400,
			wrpClass:'circles-wrp',
			textClass:'circles-text',
			styleWrapper:true,
			styleText:true
		})

    var p1_temp = Math.round(parseFloat(home.sensorValues.tempP1.replace(',','.')) * 10) / 10;
    Circles.create({
			id:'circles-2',
			radius:45,
			value: p1_temp+20,
			maxValue:55,
            minValue: 0,
			width:7,
			text: p1_temp,
			colors:['#00cde8', '#ab0505'],
			duration:400,
			wrpClass:'circles-wrp',
			textClass:'circles-text',
			styleWrapper:true,
			styleText:true
		})

    var env_temp = Math.round(parseFloat(home.sensorValues.tempExt.replace(',','.')) * 10) / 10;
    Circles.create({
			id:'circles-3',
			radius:45,
			value: env_temp+20,
			maxValue:55,
            minValue:0,
			width:7,
			text: env_temp,
			colors:['#00cde8', '#ab0505'],
			duration:400,
			wrpClass:'circles-wrp',
			textClass:'circles-text',
			styleWrapper:true,
			styleText:true
		})


    //ACS Temperatures
    var consig_temp = Math.round(parseFloat(home.sensorValues.tempConsig.replace(',','.')) * 10) / 10;
    Circles.create({
			id:'circles-4',
			radius:45,
			value: consig_temp,
			maxValue:55,
            minValue:20,
			width:7,
			text: consig_temp,
			colors:['#00cde8', '#ab0505'],
			duration:400,
			wrpClass:'circles-wrp',
			textClass:'circles-text',
			styleWrapper:true,
			styleText:true
		})

    var pulse_temp = Math.round(parseFloat(home.sensorValues.tempPulse.replace(',','.')) * 10) / 10;
    Circles.create({
			id:'circles-5',
			radius:45,
			value: pulse_temp,
			maxValue:35,
            minValue: -20,
			width:7,
			text: pulse_temp,
			colors:['#00cde8', '#ab0505'],
			duration:400,
			wrpClass:'circles-wrp',
			textClass:'circles-text',
			styleWrapper:true,
			styleText:true
		})

    var ret_temp = Math.round(parseFloat(home.sensorValues.tempReturn.replace(',','.')) * 10) / 10;
    Circles.create({
			id:'circles-6',
			radius:45,
			value: ret_temp,
			maxValue:35,
            minValue: -20,
			width:7,
			text: ret_temp,
			colors:['#00cde8', '#ab0505'],
			duration:400,
			wrpClass:'circles-wrp',
			textClass:'circles-text',
			styleWrapper:true,
			styleText:true
		})

    //Consumption
    var cons = Math.round(parseFloat(home.sensorValues.consumption.replace(',','.')) * 10) / 10;
    if(cons=="0"){
    	cons="0.1";
	}
    Circles.create({
			id:'circles-7',
			radius:45,
			value: cons,
			maxValue:2.54,
            minValue: 0.005,
			width:7,
			text: cons,
			colors:['#00cf1f', '#ab0505'],
			duration:400,
			wrpClass:'circles-wrp',
			textClass:'circles-text',
			styleWrapper:true,
			styleText:true
		})
}

//mostrar mapa del sistema
function drawSystemStatus(){

	function drawWarningIcon(id){
		var css_class_icon = "#" + id;
		alert = '<img id="'+ id + '" class="warning-btn" src="images/warning-icon.png" data-toggle="modal" data-target="#alert-modal" onclick="onClickSystemWarningIcon(this.id)">'

        $("#system-map-container").append(alert);
	}

	function drawConsoleIcon(){
		let console_icon = '<button type="button" class="btn btn-default" style="position: absolute; left: 0px; right: 0px;" data-toggle="modal" data-target="#console-modal">' +
			'Consola' +
			'</button>';
		$("#system-map-container").append(console_icon);
	}

	function showHideSystemStatusButtons(){
		debugger;
		if(home.status == 1){
			//El sistema está encendido
			$("#StartButton").hide();
			$("#ShutdownButton").show();
		} else{
			//El sistema está apagado
			$("#StartButton").show();
			$("#ShutdownButton").hide();
		}
	}

	//Dibujar iconos de alertas en el mapa
	for(let i=0; i<home.alerts.length; i++){
		switch(home.alerts[i].alert_desc){
			case "no_tension":
				//Dibujar img warning
				drawWarningIcon("warn_icon0");
				break;

        	case "max_potencia":
            //Dibujar img warning
				drawWarningIcon("warn_icon1");
				break;

        	case "impulso_frio":
            //Dibujar img warning
				drawWarningIcon("warn_icon2");
				break;

        	case "sobrecalentamiento_tanque":
            //Dibujar img warning
				drawWarningIcon("warn_icon3");
				break;

        	case "exterior_frio":
            //Dibujar img warning
				drawWarningIcon("warn_icon4");
				break;

        	case "exterior_caliente":
            //Dibujar img warning
				drawWarningIcon("warn_icon5");
				break;

        	case "tanque_frio":
            //Dibujar img warning
				drawWarningIcon("warn_icon6");
				break;

        	case "tanque_caliente":
            //Dibujar img warning
				drawWarningIcon("warn_icon7");
				break;
		}
	}

	//Show/Hide botones estado del sistema
	showHideSystemStatusButtons();

	//Consola del sistema
	drawConsoleIcon();
}

//mostrar info de la alerta seleccionada en ventana modal
function setAlertModalInfo(id){
	var alert_info = getAlertInfoByWarnIconId(id);

	$("#alert-modal-title").text("Advertencia:  " + alert_info.component);
	$("#alert-modal-body").text(alert_info.msg);
}

//mostrar eventos del sistema
function drawEventMessages() {
	$("#events-card").empty();
	debugger;
	let feed = "";

	if (home.events.length > 0) {
		for (let i = 0; i < home.events.length; i++) {
			let event = home.events[home.events.length - 1 - i]; //Dibujamos los eventos de der a izq
			event.datetime = formatDatetime(event.datetime);
			let aux = '<li class=\"feed-item feed-item-info\">' +
				'<time class=\"date\" datetime=\"9-24\">' + event.datetime + '</time>' +
				'<span class=\"text\">' + event.msg + '</a></span>' +
				'</li>';
			feed += aux;
		}
		$("#events-card").append('<ol class="activity-feed" id="events-card-feed">' + feed + '</ol>');
	}

	if (home.events.length == 0) {
		let event = '<div class="d-flex"><div class="flex-1 ml-3 pt-1">' +
			'<span class="text-muted"> No hay eventos </div></div>';

		$("#events-card").append(event);
	}
}

//dibujar selector de temperatura en la consola
function drawConsoleTempSelector(){
	    jQuery('<div class="quantity-nav"><div class="quantity-button quantity-up">+</div><div class="quantity-button quantity-down">-</div></div>').insertAfter('.quantity input');
    jQuery('.quantity').each(function() {
      var spinner = jQuery(this),
        input = spinner.find('input[type="number"]'),
        btnUp = spinner.find('.quantity-up'),
        btnDown = spinner.find('.quantity-down'),
        min = input.attr('min'),
        max = input.attr('max');

      btnUp.click(function() {
        var oldValue = parseFloat(input.val());
        if (oldValue >= max) {
          var newVal = oldValue;
        } else {
          var newVal = oldValue + 1;
        }
        spinner.find("input").val(newVal);
        spinner.find("input").trigger("change");
      });

      btnDown.click(function() {
        var oldValue = parseFloat(input.val());
        if (oldValue <= min) {
          var newVal = oldValue;
        } else {
          var newVal = oldValue - 1;
        }
        spinner.find("input").val(newVal);
        spinner.find("input").trigger("change");
      });

    });
}

//mostrar temperatura consignada actual en el selector de temperatura de la consola
function setConsoleTemp(){
	$("#temperature-console-selector").val(home.consoleConsigTemp);
}
