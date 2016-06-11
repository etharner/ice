$(function() {
    $(".sea-tab").click(function() {
        var clickedElem = $(this);
        if (!clickedElem.hasClass("sea-tab-active"))
            clickedElem.addClass("sea-tab-active");

        $(".sea-tab").each(function(i) {
            if (!$(this).is(clickedElem[0]))
                if ($(this).hasClass("sea-tab-active"))
                    $(this).removeClass("sea-tab-active");
        });

        $.ajax({
            type: "GET",
            url: window.location.pathname,
            cache: false,
            dataType: "json",
            data: {
                sea_name: $(this).data("sea")
            },
            success: function (data) {
                var gridData = prepGridData(data['data']);

                var grid = $("#list");
                grid.jqGrid("clearGridData");
                grid.jqGrid("setGridParam", {
                    data: gridData
                });
                grid.trigger("reloadGrid");
            },
            error: function (xhr, ajaxOptions, thrownError) {
                alert(xhr.status);
                alert(thrownError);
            }
        });
    });
    
    function prepGridCols() {
        var templ_data = $(".data");
        var cols_loc = templ_data.data("cols-loc");
        var cols = templ_data.data("cols");

        var cols_dict = [
                //{label: 'invid', name: 'invid', width: 55, sorttype: 'int'},
                {label: 'date', name: 'date', width: 90, sorttype: 'date', datefmt: 'Y-m-d'}
            ];
        for (var col in cols) {
            if (cols.hasOwnProperty(col))
                cols_dict.push({
                    label: cols[col],
                    name: cols[col],
                    width: 80,
                    sorttype: 'float'
                })
        }

        return {
            colNames: cols_loc,
            colModel: cols_dict
        };
    }
    
    function prepGridData(gridData) {
        var table_data = [];
        var rowid = 1;
        for (var year in gridData)
                if (gridData.hasOwnProperty(year))
                    for (var month in gridData[year])
                        if (gridData[year].hasOwnProperty(month))
                            for (var day_dec in gridData[year][month])
                                if (gridData[year][month].hasOwnProperty(day_dec)) {
                                    var data_dump = gridData[year][month][day_dec];
                                    var table_row = {
                                       // invid: String(rowid),
                                        date: year + "-" + month + "-" + day_dec
                                    };
                                    for (var key in data_dump)
                                        if (data_dump.hasOwnProperty(key))
                                            table_row[key] = String(data_dump[key]);
                                    table_data.push(table_row);

                                    rowid++;
                                }

        return table_data
    }

    var gridCols = prepGridCols();
    var grid = $("#list");
     grid.jqGrid({
         datatype: "local",
         height: 500,
         width: 1030,
         colNames: gridCols['colNames'],
         colModel: gridCols['colModel'],
         data: [],
         rowNum: 100,
         pager: "#pager",
         viewrecords: true,
         caption: "Данные"
     });
    grid.jqGrid('gridResize', {
        minWidth: 350,
        maxWidth: 1030,
        minHeight: 400,
        maxHeight: 1500
    });
    $(".sea-tab[data-sea='" + 'bering' +"']").trigger("click");
});
