//Caché de datos
var home = {
    alerts : [],
    sensorValues : {
        tempExt : "",
        tempPB : "",
        tempP1 : "",
        tempConsig : "",
        tempPulse : "",
        tempReturn : "",
        consumption: ""
    },
    status: 0,
    events:[],
    consoleConsigTemp: ""
}

//actualizacion de valores de caché
function updateValues(values){
    home.sensorValues.tempExt = values["Temperatura exterior (AEMET)"];
    home.sensorValues.tempPB = values["Temperatura PB"];
    home.sensorValues.tempP1 = values["Temperatura P1"];
    home.sensorValues.tempConsig = values["Temperatura consigna"];
    home.sensorValues.tempPulse = values["Temperatura aigua impuls"];
    home.sensorValues.tempReturn = values["Temperatura aigua retorn"];
    home.sensorValues.consumption = values["Bomba de calor"];
    home.consoleConsigTemp = values["Temperatura consigna"];
}

function updateStatus(status){
    home.status = status["status"];
    home.sensorValues.tempConsig = status["consigTemp"];
}

function valuesToJSON(){
    return JSON.stringify(home)
}

//formatado de fechas cargadas
function formatDatetime(value){
    var datetime = value.replace(":00+0100","");
    datetime = datetime.replace("T", " | ");
    return datetime;
}

//devolver informacion de alerta según icono clicado
function getAlertInfoByWarnIconId(id){
    switch(id){
        case "warn_icon0":
            return {
                component: "Bomba de calor",
                risk: "Alto",
                msg: "Error en la entrada eléctrica"
            }

        case "warn_icon1":
            return {
                component: "Bomba de calor",
                risk: "Alto",
                msg: "Máx. potencia alcanzada"
            }

        case "warn_icon2":
            return {
                component: "Tanque ACS",
                risk: "Medio",
                msg: "Temperatura de impulso baja"
            }

        case "warn_icon3":
            return {
                component: "Tanque ACS",
                risk: "Medio",
                msg: "Temperatura consignada superada"
            }

        case "warn_icon4":
            return {
                component: "Temperatura",
                risk: "Medio",
                msg: "Temperatura exterior muy baja"
            }

        case "warn_icon5":
            return {
                component: "Temperatura",
                risk: "Medio",
                msg: "Temperatura exterior muy alta"
            }

        case "warn_icon6":
            return {
                component: "Tanque ACS",
                risk: "Medio",
                msg: "Temperatura inferior a la recomendada"
            }

        case "warn_icon7":
            return {
                component: "Tanque ACS",
                risk: "Medio",
                msg: "Temperatura superior a la recomendada"
            }
    }
}

//devolver informacion del alerta según descripcion
function getAlertInfoByDesc(desc){
    switch(desc){
        case "no_tension":
            return {
                component: "Bomba de calor",
                risk: "Alto",
                msg: "Error en la entrada eléctrica"
            }

        case "max_potencia":
            return {
                component: "Bomba de calor",
                risk: "Alto",
                msg: "Máx. potencia alcanzada"
            }

        case "impulso_frio":
            return {
                component: "Tanque ACS",
                risk: "Medio",
                msg: "Temperatura de impulso baja"
            }

        case "sobrecalentamiento_tanque":
            return {
                component: "Tanque ACS",
                risk: "Medio",
                msg: "Temperatura consignada superada"
            }

        case "exterior_frio":
            return {
                component: "Temperatura",
                risk: "Medio",
                msg: "Temperatura exterior muy baja"
            }

        case "exterior_caliente":
            return {
                component: "Temperatura",
                risk: "Medio",
                msg: "Temperatura exterior muy alta"
            }

        case "tanque_frio":
            return {
                component: "Tanque ACS",
                risk: "Medio",
                msg: "Temperatura inferior a la recomendada"
            }

        case "tanque_caliente":
            return {
                component: "Tanque ACS",
                risk: "Medio",
                msg: "Temperatura superior a la recomendada"
            }
    }
}
