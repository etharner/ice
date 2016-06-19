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

$(function () {
    $('select').selectric({
        maxWidth: 30,
        onInit: function() {

        },
        onChange: function () {
        }
    });

    $('.send').click(function () {
        var sea_selects = {};
        var checkboxes = {
            'Исходные данные': 'source',
            'Усредненные данные': 'mean',
            'Поля корреляций': 'corr',
            'Квартальный прогноз': 'forecast'
        };
        var seas = ['bering', 'chukchi', 'japan', 'okhotsk'];
        var checked = {};
        for (var i = 0; i < seas.length; i++) {
            checked[seas[i]] = {};
            $("." + seas[i] + "-checks label").each(function () {
                checked[seas[i]][checkboxes[$(this).text()]] = $(this).children().prop( "checked") == true ? 1 : 0;
            });
        }

        var quater = $("#quater-choose").find('option:selected').text();
        var year = $("#year-choose").find('option:selected').text();

        var button = $(this);
        var old = button.val();
        button.val("Загрузка..");
        button.prop("disabled", true);

        var pdf_button = $('#pdf-download');
        var tex_button = $('#tex-download');
        if (pdf_button)
            pdf_button.text("Загрузка..");
        if (tex_button)
            tex_button.text("Загрузка..", true);

        $.ajax({
            type: "GET",
            url: window.location.pathname,
            data: {
                quater: quater,
                year: year,
                checked: checked,
                action: "report",
                csrfmiddlewaretoken: csrftoken
            },
            success: function (data) {
                button.prop("disabled", false);
                button.val(old);

                $("#pdf-download").remove();
                var zip = $('<a id="pdf-download">');
                zip.attr("href", data.pdf);
                zip.text("Скачать .pdf");
                zip.appendTo("form");

                $("#tex-download").remove();
                var zip = $('<a id="tex-download">');
                zip.attr("href", data.tex);
                zip.text("Скачать .tex");
                zip.appendTo("form");
            },
            error: function (xhr, ajaxOptions, thrownError) {
                button.prop("disabled", false);
                button.val("Ошибка");

                $("#pdf-download").remove();
                $("#tex-download").remove();

                console.log(xhr.status);
                console.log(thrownError);
            }
        });
    });
});
