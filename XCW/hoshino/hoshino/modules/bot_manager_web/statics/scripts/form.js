function addErrorMsg(elementNameId, msg) {
    $("[for=" + elementNameId + "]").after("<span class='errorMsg'>" + msg + "</span>")
}

function checkText(id) {
    if ($("#" + id + "").val()) {
        return true
    } else {
        addErrorMsg(id, "不能为空");
        return false
    }
}

function checkTextNumber(id) {
    if (/^\d+$/.test(($("#" + id + "").val()))) {
        return true
    } else {
        addErrorMsg(id, "必须填写数字");
        return false
    }
}

function checkTextEmail(id) {
    if (/^([a-zA-Z]|[0-9])(\w|-)+@[a-zA-Z0-9]+\.([a-zA-Z]{2,4})$/.test(($("#" + id + "").val()))) {
        return true
    } else {
        addErrorMsg(id, "请正确填写邮箱");
        return false
    }
}

function checkRadio(radioName) {
    let check_result = false;
    const obj = $("input[name=" + radioName + "]");
    for (let i = 0; i < obj.length; i++) {
        if (obj[i].checked) {
            check_result = true;
        }
    }
    if (!check_result) {
        addErrorMsg(radioName, "必选");
    }
    return check_result
}

function cleanErrorMsg() {
    $(".errorMsg").remove();
}
