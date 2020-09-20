// Copyright (c) 2020, SHS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Item Availability Estimate', {
    // en: we use the before load form event to preload the week for this date.
    // es-GT: Usamos el evento del formulato "Before Load" para pre-cargar el titulo de la semana.
    before_load: function(frm) {
        // en: Create a new date object using now's date and time.
        // es-GT: Creamos un nuevo objeto de fecha usando la fecha y hora de este momento.
        var today_date = new Date();
        // en: we set the title of the new Item Availability Estimate to be the week.
        // es-GT: Asignamos el titulo del documento de Estimado de Disponibilidad.
        var title_text = __('Week') + (' ') + today_date.getWeek().toString()
        frm.set_value('title', title_text);
        // en: Now we set the posting date value to today's date.
        // es-GT: Asignamos la fecha de posteo a la fecha de hoy.
        frm.set_value('posting_date', today_date);
    },
    posting_date: function(frm) {
        // en: We get the value in Posting Date field.
        // es-GT: Obtenemos el valor en el campo de Posting Date.
        var posting_date_value = new Date(cur_frm.doc.posting_date);
        // en: We estimate what the date of the nearest monday is.
        // es-GT: Estimamos cual es la fecha del lunes mas cercano
        var set_start_date = monday(posting_date_value,1);
        // en: We assign the start date as the monday closest to the pre-loaded posting_date.
        // es-GT: Asignamos la fecha inicial basado en el lunes mas cercano a la fecha de posteo automaticamente seleccionada.
        frm.set_value('start_date', set_start_date);
    },
    
    start_date: function(frm) {
        // en: When the start date is assigned, we need to calculate what the end date will be. (+7 days including the start date)
        // es-GT: Cuando se asigna la fecha de inicio, necesitamos calcular cual va ser la fecha final (+7 días incluyendo la fecha de inicio)
        var curr_start_date = new Date(cur_frm.doc.start_date);
        var end_of_week_date = addDays(curr_start_date,7);
        frm.set_value('end_date', end_of_week_date);
    },
    end_date: function(frm) {
        // en: When the start date is assigned, we need to calculate what the end date will be. (+7 days including the start date)
        // es-GT: Cuando se asigna la fecha de inicio, necesitamos calcular cual va ser la fecha final (+7 días incluyendo la fecha de inicio)
        var curr_start_date = new Date(cur_frm.doc.start_date);
        var end_of_week_date = new Date(cur_frm.doc.end_date);
        var Difference_In_Time = end_of_week_date.getTime() - curr_start_date.getTime();
        var Difference_In_Days = Difference_In_Time / (1000 * 3600 * 24);
        frm.set_value('days', (Difference_In_Days+1));
    },
    onload: function (frm) {
        cur_frm.fields_dict["estimated_available_items"].grid.get_field("item_code").get_query = function(doc){
            return {
                filters:{
                       "is_sales_item": 0,
                       "include_in_estimations": 1
               }
            }
        }
    }
});

/* SOURCE: https://stackoverflow.com/questions/1579010/get-next-date-from-weekday-in-javascript */

//takes dayIndex from monday(0) to saturday(6)
function monday(d,dayIndex) {
    var monday = d;
    monday.setDate(monday.getDate() + (dayIndex - 1 - monday.getDay() + 7) % 7 + 1);
    return monday;
}

function addDays(date, days) {
  var result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

/**
 * Returns the week number for this date.  dowOffset is the day of week the week
 * "starts" on for your locale - it can be from 0 to 6. If dowOffset is 1 (Monday),
 * the week returned is the ISO 8601 week number.
 * @param int dowOffset
 * @return int
 */
Date.prototype.getWeek = function (dowOffset) {
/*getWeek() was developed by Nick Baicoianu at MeanFreePath: http://www.meanfreepath.com */

    dowOffset = typeof(dowOffset) == 'int' ? dowOffset : 0; //default dowOffset to zero
    var newYear = new Date(this.getFullYear(),0,1);
    var day = newYear.getDay() - dowOffset; //the day of week the year begins on
    day = (day >= 0 ? day : day + 7);
    var daynum = Math.floor((this.getTime() - newYear.getTime() - 
    (this.getTimezoneOffset()-newYear.getTimezoneOffset())*60000)/86400000) + 1;
    var weeknum;
    //if the year starts before the middle of a week
    if(day < 4) {
        weeknum = Math.floor((daynum+day-1)/7) + 1;
        if(weeknum > 52) {
            nYear = new Date(this.getFullYear() + 1,0,1);
            nday = nYear.getDay() - dowOffset;
            nday = nday >= 0 ? nday : nday + 7;
            /*if the next year starts before the middle of
              the week, it is week #1 of that year*/
            weeknum = nday < 4 ? 1 : 53;
        }
    }
    else {
        weeknum = Math.floor((daynum+day-1)/7);
    }
    return weeknum;
};

var mydate = new Date(2020,8,19); // month number starts from 0
// or like this
var mydate = new Date('September 19, 2020');
// alert(mydate.getWeek());



/** Consulted: https://www.w3schools.com/js/js_date_methods.asp */