function getCookie(name) {
    const strCookie = document.cookie;
    const arrCookie = strCookie.split("; ");
    for (let i = 0; i < arrCookie.length; i++) {
        const arr = arrCookie[i].split("=");
        if (arr[0] === name) {
            return arr[1]
        }
    }
    return ""
}

function guid() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function set_msg(msg_text) {
    alert(msg_text);
    $('#msg').html(msg_text);
}

function getQueryVariable(variable) {
    const query = window.location.search.substring(1);
    const vars = query.split("&");
    for (let i = 0; i < vars.length; i++) {
        const pair = vars[i].split("=");
        if (pair[0] === variable) {
            return pair[1];
        }
    }
    return false;
}

function assembleQueryString(paramsArr) {
    const q = [];
    for (const k in paramsArr) {
        if (paramsArr.hasOwnProperty(k)) {
            q.push(k + "=" + paramsArr[k]);
        }
    }
    return q.join("&");
}


function redirectWithParams(keepParamsList, addParamsArr) {
    const finalParams = {};
    for (const k of keepParamsList) {
        finalParams[k] = getQueryVariable(k)
    }
    for (const k in addParamsArr) {
        if (addParamsArr.hasOwnProperty(k)) {
            finalParams[k] = addParamsArr[k]
        }
    }

    window.location.href = window.location.pathname + "?" + assembleQueryString(finalParams)
}

function coloring_systolic(input_id) {
    const input_item = $("#" + input_id);
    const s = Number(input_item.val());
    if (s > 90) {
        input_item.addClass("bloodPressureHigh");
    } else if (s < 60) {
        input_item.addClass("bloodPressureLow");
    }
}

function coloring_diastolic(input_id) {
    const input_item = $("#" + input_id);
    const s = Number(input_item.val());
    if (s > 140) {
        input_item.addClass("bloodPressureHigh");
    } else if (s < 90) {
        input_item.addClass("bloodPressureLow");
    }
}
