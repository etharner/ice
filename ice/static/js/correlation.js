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

function build_grid(data, decrange) {
    var colNames = ['Декады'];
    var colModel = [{name:'decs',index:'decs', width:55, sorttype:'int'}];

    for (var col = 0; col < decrange.length; col++) {
        var name = String(decrange[col]);
        colNames.push(name);
        colModel.push({name: name, index: name, width: 55, sorttype: 'int'})
    }

    gridData = [];
    for (var i = 0; i < decrange.length; i++) {
        var row = {'decs': decrange[i]};
        for (var j = 0; j < decrange.length; j++) {
            row[String(decrange[j])] = data[i][j]
        }
        gridData.push(row);
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
        caption: "Корреляционные коэффициенты"
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
            if ($(this).attr("id") == "dec1-choose") {
                var dec2 = $("#dec2-choose");
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
        }
    });

    $('.send').click(function () {
        var sea1 = $("#sea1-choose").find('option:selected').text();
        var sea2 = $("#sea2-choose").find('option:selected').text();
        var year = $("#year-choose").find('option:selected').text();
        var dec1 = $("#dec1-choose").find('option:selected').text();
        var dec2 = $("#dec2-choose").find('option:selected').text();
        var prop = $("#prop-choose").find('option:selected').text();

        var button = $(this);
        var old = button.val();
        button.val("Загрузка..");
        button.prop("disabled", true);

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
                action: "corr",
                csrfmiddlewaretoken: csrftoken
            },
            success: function (data) {
                button.prop("disabled", false);
                button.val(old);

                build_grid(data.coeffs, data.decrange);

                var divimg = $(".hidden-img");
                divimg.find(':first-child').remove();

                var img = $('<object id="corr-field">');
                img.attr("type", "image/svg+xml");
                img.attr("data", data.imgfile);
                img.attr("width", "100%");
                img.attr("height", "100%");
                img.appendTo(".hidden-img");

                divimg.css("display", "block");
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