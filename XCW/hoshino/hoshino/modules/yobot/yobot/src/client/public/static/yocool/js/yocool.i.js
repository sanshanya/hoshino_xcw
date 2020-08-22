var link = [];
link[0] = "../assets/yocool/css/colors/scheme-01.css";
link[1] = "../assets/yocool/css/colors/scheme-02.css";
link[2] = "../assets/yocool/css/colors/scheme-03.css";
link[3] = "../assets/yocool/css/colors/scheme-04.css";
link[4] = "../assets/yocool/css/colors/scheme-05.css";
link[5] = "../assets/yocool/css/colors/scheme-06.css";
link[6] = "../assets/yocool/css/colors/scheme-07.css";
link[7] = "../assets/yocool/css/colors/scheme-08.css";
link[8] = "../assets/yocool/css/colors/scheme-09.css";
$(function() {
    var style = link[Math.floor(Math.random() * link.length)];
    if (document.createStyleSheet) {
        document.createStyleSheet(style)
    }
    else {
        $('<link />', {
            rel: 'stylesheet',
            href: style
        }).appendTo('head')
    }
});
document.writeln("<div id=\'bottomToolbar\'>Powered by <a href=\'https://github.com/pcrbot/yobot\'>Yobot</a> | Themes by <a href=\'https://github.com/A-kirami/YoCool\'>YoCool</a> | Customed by Lost</div>");
$(function() {
    $(window).scroll(function() {
        var topToolbar = $("#topToolbar");
        var headerH = $("#header").outerHeight();
        var scrollTop = $(document).scrollTop()
    })
});
