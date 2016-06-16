function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function build_grid(data) {
    var colNames = ['Год-месяц-декада', 'Значение'];
    var colModel = [
        {label: 'date', name: 'date', width: 90, sorttype: 'date', datefmt: 'Y-m-d'},
        {label: 'val', name: 'val', width: 80, sorttype: 'string'}
    ];
    
    var gridData = [];
    for (var year in data)
        if (data.hasOwnProperty(year))
            for (var month in data[year])
                if (data[year].hasOwnProperty(month))
                    for (var day_dec in data[year][month])
                        if (data[year][month].hasOwnProperty(day_dec)) {
                            var data_dump = data[year][month][day_dec];
                            var table_row = {
                                date: year + "-" + month + "-" + day_dec
                            };
                            table_row['val'] = String(data_dump[0] + ":" + data_dump[1]);
                            gridData.push(table_row);
                        }
    $.jgrid.gridUnload("#list");
    var grid = $("#list");
    grid.jqGrid({
        datatype: "local",
        height: 500,
        width: 1030,
        colNames: colNames,
        colModel: colModel,
        data: gridData,
        rowNum: 100,
        pager: "#pager",
        viewrecords: true,
        caption: "Прогнозируемые значения"
    });
    grid.jqGrid('gridResize', {
        minWidth: 350,
        maxWidth: 1500,
        minHeight: 400,
        maxHeight: 1000
    });
    grid.trigger("reloadGrid");
}

$(function () {
    $('select').selectric({
        maxWidth: 30,
        onInit: function() {

        },
        onChange: function () {
            if ($(this).attr("id") == "date1-dec-choose") {
                var dec2 = $("#date2-dec-choose");
                var dec1Val = parseInt($(this).val());
                var dec2Val = parseInt(dec2.find('option:selected').text());

                dec2.find('option').remove();
                for (var i = dec1Val == 36 ? dec1Val : dec1Val + 1; i <= 36; i++)
                    dec2.append($("<option>", {
                        text: String(i)
                    })).selectric('refresh');

                if (dec2Val > dec1Val == 36 ? dec1Val - 1 : dec1Val) {
                    dec2.val(dec2Val);
                    dec2.selectric('refresh');
                }
            }
            else if ($(this).attr("id") == "date1-year-choose") {
                var year2 = $("#date2-year-choose");
                var year1Val = parseInt($(this).val());
                var year2Val = parseInt(year2.find('option:selected').text());

                year2.find('option').remove();
                for (var i = year1Val; i <= 2020; i++)
                    year2.append($("<option>", {
                        text: String(i)
                    })).selectric('refresh');

                if (year2Val > year1Val) {
                    year2.val(year2Val);
                    year2.selectric('refresh');
                }
            }
        }
    });

    $('.send').click(function () {
        var sea = $("#sea-choose").find('option:selected').text();
        var year1 = $("#date1-year-choose").find('option:selected').text();
        var dec1 = $("#date1-dec-choose").find('option:selected').text();
        var year2 = $("#date2-year-choose").find('option:selected').text();
        var dec2 = $("#date2-dec-choose").find('option:selected').text();
        var prop = $("#prop-choose").find('option:selected').text();

        var button = $(this);
        var old = button.val();
        button.val("Загрузка..");
        button.prop("disabled", true);

        $.ajax({
            type: "GET",
            url: window.location.pathname,
            data: {
                sea: sea,
                year1: year1,
                dec1: dec1,
                year2: year2,
                dec2: dec2,
                prop: prop,
                action: "forecast",
                csrfmiddlewaretoken: csrftoken
            },
            success: function (data) {
                button.prop("disabled", false);
                button.val(old);

                build_grid(data.data);
            },
            error: function (xhr, ajaxOptions, thrownError) {
                button.prop("disabled", false);
                button.val(old);

                console.log(xhr.status);
                console.log(thrownError);
            }
        });
    });
});
