 function ip2num(ip) {
    var ret, val;
    if (!(ret = ip.match(/^(\d+)\.(\d+)\.(\d+)\.(\d+)$/))) return false;
    for (var i = 1, val = 0; i <= 4; i++) {
        if (parseInt(ret[i], 10) > 255) return false;
        val = (val << 8) + parseInt(ret[i], 10);
    }
    return val;
}

