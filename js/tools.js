// Element types
const domElmType = {
    ELEMENT_NODE:	1,
    ATTRIBUTE_NODE:	2,
    TEXT_NODE:	3,
    CDATA_SECTION_NODE:	4,
    PROCESSING_INSTRUCTION_NODE:	7,
    COMMENT_NODE:	8,
    DOCUMENT_NODE:	9,
    DOCUMENT_TYPE_NODE:	10,
    DOCUMENT_FRAGMENT_NODE:	11,
};

/**
 * Create a random ID.
**/
function makeId(length) {
    let result = '';
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const charactersLength = characters.length;
    let counter = 0;
    while (counter < length) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
      counter += 1;
    }
    return result;
}

/**
 * Make a decent post request using XMLHttpRequest.
**/
function postRequestXHR(url, payload) {
    console.debug('>>>>> request:', url, payload);
    const req = new XMLHttpRequest();
    req.open('POST', url, false);
    req.setRequestHeader('Content-type', 'application/json; charset=utf-8');
    req.send(JSON.stringify(payload));
    let json = undefined;
    try {
        json = JSON.parse(req.responseText);
    }
    catch (error) {
        // Swallow any errors
    }
    const ret = { status: req.status, payload: json };
    console.debug('<<<<< response: ', ret);
    return ret;
}

/**
 * Make a post request using fetch.
 * Async/await bullshit, too slow.
**/
async function postRequestBS(url, payload) {
    console.debug('>>>>> request:', url, payload);
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-type': 'application/json; charset=utf-8' },
        body: JSON.stringify(payload)
    });
    const ret = { status: res.status, payload: await res.json() };
    console.debug('<<<<< response: ', ret);
    return ret;
}

/**
 * Does the string represents a numeric value?
**/
function isNumeric(str) {
    if (typeof str != "string") return false
    return !isNaN(str) && !isNaN(parseFloat(str))
}

/**
 * Assert a condition, throw an error message if the assertion failed.
**/
function assert(condition, message) {
    if (!condition) {
        throw new Error(message || "Assertion failed");
    }
}

function twip2pt(twip) {
    return twip * 0.05;
}

function pt2twip(pt) {
    return pt * 20;
}

function cm2pt(cm) {
    return cm * 28.3465;
}

/**
 * Parse a xml string in a safe manner.
**/
function parseXML(xmlStr) {
    if (xmlStr) {
        const parser = new DOMParser();
        const xml = parser.parseFromString(xmlStr, 'text/xml');
        return xml.getElementsByTagName('parsererror').length > 0 ? null : xml;
    }
}

/**
 * Parse a html string in a safe manner.
**/
function parseHTML(htmlStr) {
    if (htmlStr) {
        const parser = new DOMParser();
        const html = parser.parseFromString(htmlStr, 'text/html');
        return html.getElementsByTagName('parsererror').length > 0 ? null : html;
    }
}

/**
 * Turn a color string into hex RGB color code.
 * If reverse, BGR.
**/
function parseColor(colorStr, reverse) {
    let color = null;
    if (colorStr.indexOf('#') === 0) {
        const colorStr_ = reverse ? '#' + colorStr.substr(5, 2) + colorStr.substr(3, 2) + colorStr.substr(1, 2) : colorStr;
        color = parseInt(colorStr_.replace('#', '0x'))
    }
    else if (colorStr.indexOf('rgb(' === 0)) {
        tmp = colorStr.match(new RegExp('\\d+,\\s*\\d+,\\s*\\d+'))[0].split(',');
        assert(tmp.length === 3);
        if (reverse) {
            tmp.reverse();
        }
        color = parseInt(tmp[2])*256*256 + parseInt(tmp[1])*256 + parseInt(tmp[0]);
    }
    return color;
}

/**
 * Find a color from a given color set that is most close to a hex RGB color
**/
function matchColor(targetColor, colors) {
    const idx = colors.indexOf(targetColor);
    if (idx >= 0) {
        return colors[idx];
    }
    const cStr = targetColor.toString(16);
    const r = parseInt('0x' + cStr.substr(0, 2));
    const g = parseInt('0x' + cStr.substr(2, 2));
    const b = parseInt('0x' + cStr.substr(4, 2));
    function diff(_color) {
        const _cStr = _color.toString(16);
        const _r = parseInt('0x' + _cStr.substr(0, 2));
        const _g = parseInt('0x' + _cStr.substr(2, 2));
        const _b = parseInt('0x' + _cStr.substr(4, 2));
        return (r - _r)**2 + (g - _g)**2 + (b - _b)**2;
    }
    let d1 = 3 * 1000**2;
    let res = null;
    for (let c of colors) {
        let d = diff(c);
        if (d < d1) {
            d1 = d;
            res = c;
        }
    }
    return res;
}