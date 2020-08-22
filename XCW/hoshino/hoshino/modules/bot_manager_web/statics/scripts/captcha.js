//短信验证码校验
function checkSmsCode() {
    const phone = $('#phone').val();
    const code = $('#sms_code').val();
    let check_result = false;
    $.ajax({

        async: false,
        type: "get",
        url: "/accounts/sms_check",
        data: "phone=" + phone + "&code=" + code,
        success: function (msg) {
            console.log(msg);
            if (msg.code === 200) {
                check_result = true;
            } else {
                set_msg(msg.message);
            }
        },
        error: function (res) {
            console.log(res.status)
        }
    });
    console.info(check_result);
    return check_result
}


//验证图形验证码
function checkImageCaptcha() {
    let check_result = false;
    const captcha = $('#captcha');
    if (captcha.val().length > 0) {
        const data = {
            "csrfmiddlewaretoken": $('[name="csrfmiddlewaretoken"]').val(),
            "uuid": $('#captcha_uuid').val(),
            "code": captcha.val(),
        };
        $.ajax({
            async: false,
            type: 'POST',
            url: "/captcha/verify/",
            data: data,
            success: function (data) {
                if (data.code === 200) {
                    console.info("image captcha pass");
                    check_result = true;
                    return true;
                } else {
                    addErrorMsg('captcha', "图形验证码错误");
                    alert("图形验证码错误！");
                    console.info("invalid image captcha");
                    $('#captcha').focus();
                }
            },
            error: function () {
                alert("图形验证码验证服务器出错！");
                addErrorMsg('captcha', "图形验证码验证服务器出错");
                console.info("图形验证码验证服务器出错");
                $('#captcha').focus();

            }
        })
    } else {
        addErrorMsg('captcha', "图形验证码不能为空");
        alert("图形验证码不能为空")
    }
    return check_result;
}

function get_sms_code() {
    const image_correct = checkImageCaptcha();
    if (image_correct) {
        $.ajax({
            type: "POST",
            url: "/accounts/sms_send",
            data: {
                "phone": $("#phone").val(),
                "csrfmiddlewaretoken": $('[name="csrfmiddlewaretoken"]').val(),
            },
            success: function (msg) {
                console.info(msg);
                if (msg.message === "OK") {
                    set_msg("验证码发送成功");
                } else {
                    set_msg(msg.message);
                }
            },
            error: function (res) {
                set_msg("手机验证码验证出错，状态 " + res.code);
            }
        });
    }
}

<!-- 动态刷新验证码js -->
$(document).ready(function () {
    $('.captcha').click(function () {
        const uuid = guid();
        $('#captcha_image').attr('src', "/captcha/gen/" + uuid + "/");
        $('#captcha_uuid').val(uuid);
    });
    // $("#captcha").change(function () {
    //     checkImageCaptcha();
    // });
    // $('#sms_code').change(function () {
    //     checkSmsCode();
    // });
    const msg_string = $("#msg").html();
    if (msg_string.length > 0) {
        alert(msg_string);
    }
});
$(document).ready(function () {
    $('.captcha').click();
});