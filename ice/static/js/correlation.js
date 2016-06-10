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
    var colNames = ['Декады'];
    var colModel = [{name:'decs',index:'decs', width:55, sorttype:'int'}];

    for (var i = 0; i < data.length; i++) {
        colNames.push(String(i + 1));
        colModel.push({name:String(i + 1),index:String(i + 1), width:55, sorttype:'int'})
    }

    gridData = [];
    for (var i = 0; i < data.length; i++) {
        var row = {'decs': i + 1};
        for (var j = 0; j < data.length; j++)
            row[String(j + 1)] = data[i][j]
        gridData.push(row);
    }

    $.jgrid.gridUnload("#list");
    var grid = $("#list");
    grid.jqGrid({
        datatype: "local",
        height: 500,
        width: 950,
        colNames: colNames,
        colModel: colModel,
        data: gridData,
        rowNum: 100,
        pager: "#pager",
        viewrecords: true,
        caption: "Ice Data"
    });
    grid.jqGrid("clearGridData");
    grid.jqGrid("setGridParam", {
        data: gridData
    });
    grid.trigger("reloadGrid");
}

$(function () {
    $('select').selectric({
            maxWidth: 30,
        onInit: function() {

        }
    });

    $('.send').click(function () {
        sea1 = $("#sea1-choose").find('option:selected').text();
        sea2 = $("#sea2-choose").find('option:selected').text();
        year = $("#year-choose").find('option:selected').text();
        dec1 = $("#dec1-choose").find('option:selected').text();
        dec2 = $("#dec2-choose").find('option:selected').text();
        prop = $("#prop-choose").find('option:selected').text();

        $.ajax({
            type: "GET",
            url: window.location.pathname,
            data: {
                sea1: sea1,
                sea2: sea2,
                year: year,
                dec1: dec1,
                dec2: dec2,
                prop: prop,
                action: 'corr',
                csrfmiddlewaretoken: csrftoken
            },
            success: function (data) {
                console.log(data);
                alert(data.coeffs);
                build_grid(data.coeffs);
            },
            error: function (xhr, ajaxOptions, thrownError) {
                alert(xhr.status);
                alert(thrownError);
            }
        });
    });
});