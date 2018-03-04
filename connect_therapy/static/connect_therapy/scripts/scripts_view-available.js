
        //Hides the Django's Default DatePicker widget in Patient's Appointment Booking page
        var hide_id_date_month= document.getElementById('id_date_month');
        var hide_id_date_day=document.getElementById('id_date_day');
        var hide_id_date_year=document.getElementById('id_date_year');
        var hide_label = document.getElementsByTagName('label')[0];
        var jQuery_Date_Picker = document.getElementById("date_picker"); //Only used to check if it is in DOM
        hide_id_date_month.style.display = 'none';
        hide_id_date_day.style.display = 'none';
        hide_id_date_year.style.display = 'none';
        hide_label.style.display = 'none';



    $(document).ready(function () {

        $("#date_picker").datepicker( {
                                changeMonth: false,
                                changeYear:false,
                                showOtherMonths: true,
                                minDate: new Date(),
                                maxDate: new Date().getDay()+27,
                                dateFormat: "dd-mm-yy",
                                numberOfMonths: [1,2],
                                onSelect: function (dateText, inst) {
                                    var d = $(this).datepicker('getDate'),
                                        day = d.getDate(),
                                        month = d.getMonth() + 1, //months starts from Zero (Zero based index)
                                        year = d.getFullYear();

                                    /**
                                     *
                                     * Iterates through the date selector(Django Datepicker widget)
                                     * and compares to see if the current date is an option in the
                                     * date selector, if so, it selects the date in the django's
                                     * date picker widget
                                     *
                                     */
                                    var dateSelector = document.getElementById("id_date_day");
                                    setSelectedDate(dateSelector, day);
                                    function setSelectedDate(selectDate, dateToSelect) {
                                        for (var i = 0; i < selectDate.options.length; i++) {
                                            if (selectDate.options[i].text == dateToSelect){

                                                selectDate.options[i].selected = true;
                                                return;
                                            }
                                        }

                                    }
                                    /**
                                     *
                                     * Iterates through the date selector(Django Datepicker widget)
                                     * and compares to see if the current year is an option in the
                                     * date selector, if so, it selects the year in the django's
                                     * date picker widget
                                     *
                                     */
                                    var yearSelector = document.getElementById("id_date_year");
                                    setSelectedMonth(yearSelector, year);
                                    function setSelectedMonth(selectYear, yearToSelect) {
                                        for (var i = 0; i < selectYear.options.length; i++) {
                                            if (selectYear.options[i].text == yearToSelect){

                                                selectYear.options[i].selected = true;
                                                return;
                                            }
                                        }
                                    }

                                    /**
                                     *
                                     * Iterates through the date selector(Django Datepicker widget)
                                     * and compares to see if the current month is an option in the
                                     * date selector, if so, it selects the month in the django's
                                     * date picker widget
                                     *
                                     */
                                    var monthSelector = document.getElementById("id_date_month");
                                    setSelectedMonth(monthSelector, month);
                                    function setSelectedMonth(selectmonth, monthToSelect) {
                                        for (var i = 0; i < selectmonth.options.length; i++) {
                                            if (selectmonth.options[i].value == monthToSelect){

                                                selectmonth.options[i].selected = true;
                                                return;
                                            }
                                        }
                                    }
                                }});

        if (jQuery_Date_Picker.offsetParent === null) {
            hide_id_date_month.style.display = 'inline';
            hide_id_date_day.style.display = 'inline';
            hide_id_date_year.style.display = 'inline';
            hide_label.style.display = 'inline';
        }

    });
