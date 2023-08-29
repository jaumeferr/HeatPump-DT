const url = 'http://127.0.0.1:5000/';

//Solicita registro actividad de los sensores
function getHttpSensorValues(){
    var data = null;
    $.ajax({
        url : url + '/sensor_values',
        type : 'GET',
        async: false,
        crossDomain:true,
        'success' : function(response) {
            data = JSON.parse(response);
        },
        'error' : function(request,error)
        {
            console.log("Request: "+JSON.stringify(request));
        }
    });
    return data;
}

//Carga el estado del sistema
function getHttpSystemStatus(){
    let status = null;

    $.ajax({
        url : url + '/status',
        type : 'GET',
        async: false,
        crossDomain:true,
        'success' : function(response) {
            status = JSON.parse(response);
        },
        'error' : function(request,error)
        {
            console.log("Request: "+JSON.stringify(request));
        }
    });

    return status;
}

//Solicita arranque inteligente programado del sistema
function postHttpBootPrediction(data){
    let res = ""
    $.ajax({
        url : url + '/predict_boot',
        type : 'POST',
        data: {'data': JSON.stringify(data)},
        async: false,
        crossDomain:true,
        'success' : function(response) {
            res = JSON.parse(response);
        },
        'error' : function(request,error)
        {
            console.log("Event trigger failed")
        }
    });
    return res;
}

//Solicita listado de alertas
function getHttpAlertMessages(){
    var alerts = "";
    $.ajax({
        url : url + '/alerts',
        type : 'GET',
        async: false,
        crossDomain:true,
        'success' : function(response) {
            alerts = JSON.parse(response);
        },
        'error' : function(request,error)
        {
            console.log("Request: "+JSON.stringify(request));
        }
    });
    return alerts;
}


//Carga un nuevo eventos en el registro
function postHttpEventMessage(data){
    my_events = ""
    $.ajax({
        url : url + '/events',
        type : 'POST',
        data: {'data': JSON.stringify(data)},
        async: false,
        crossDomain:true,
        'success' : function(response) {
            my_events = JSON.parse(response);
            console.log("Event triggered successfully")
        },
        'error' : function(request,error)
        {
            console.log("Event trigger failed")
        }
    });
    return my_events;
}

//Solicita registro de eventos
function getHttpEventMessages(){
    var events = "";
    $.ajax({
        url : url + '/events',
        type : 'GET',
        async: false,
        crossDomain:true,
        'success' : function(response) {
            events = JSON.parse(response);
        },
        'error' : function(request,error)
        {
            console.log("Request: "+JSON.stringify(request));
        }
    });
    return events;
}

