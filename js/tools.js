// Element types
const zc_etype = {
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
 * Make a post request (blocked by CORS).
**/
async function postRequestNative(url, payload) {
    console.debug('>>>>> request:', url, payload);
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-type': 'application/json; charset=utf-8' },
        body: JSON.stringify(payload)
    });
    const ret = { status: res.status, payload: res.json() };
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