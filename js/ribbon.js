// NOTE: Shouldn't be needing this if using the latest version of WPS
var WPS_Enum = {
    msoCTPDockPositionLeft: 0,
    msoCTPDockPositionRight: 2,
    msoPropertyTypeString: 4,
    wdCollapseStart: 1,
    wdCollapseEnd: 0,
    wdCharacter: 1,
}

const HOME = wps.Env.GetHomePath();

function zc_alert(msg) {
    alert(`WPS-Zotero: ${msg}`);
}

/**
 * Callback for plugin loading
 */
function OnAddinLoad(ribbonUI) {
    if (typeof (wps.Enum) !== "object") {
        wps.Enum = WPS_Enum;
        alert('You are using an old version of WPS, this plugin might not work properly!');
    }
    if (typeof (wps.ribbonUI) !== "object"){
        wps.ribbonUI = ribbonUI;
    }

    // Application.ApiEvent.AddApiEventListener("DocumentAfterClose", (doc) => {
    //     zc_registryRemove(doc);
    // });

    // Start request agent
    wps.OAAssist.ShellExecute(HOME + '/.wps-zotero/agent.py');
    
    // Exit the request agent when the application quits.
    Application.ApiEvent.AddApiEventListener("ApplicationQuit", () => {
        wps.OAAssist.ShellExecute(HOME + '/.wps-zotero/agent.py', 'kill');
    });
    
    return true
}

function OnAction(control) {
    const eleId = control.Id
    let client = null;
    switch (eleId) {
        case "btnAddEditCitation":
            client = zc_bind();
            client.command('addEditCitation');
            // IMPORTANT: Release references on the document objects!!!
            zc_clearRegistry();
            // Assert(Object.keys(zc_registry.doc_client).length === 0);
            break;
        case "btnAddEditBib":
            client = zc_bind();
            client.command('addEditBibliography');
            zc_clearRegistry();
            break;
        case "btnRefresh":
            client = zc_bind();
            client.import();
            zc_clearRegistry();
            // Must open a new client, since import will not register fields to client.
            client = zc_bind();
            client.command('refresh');
            zc_clearRegistry();
            break;
        case "btnPref":
            client = zc_bind();
            client.command('setDocPrefs');
            zc_clearRegistry();
            break;
        case "btnExport":
            client = zc_bind(zc_getDocumentInDocuments());
             if (confirm('Confirm to convert this document into a style to let other processors import from? You may want to make a backup first.')) client.export();
            zc_clearRegistry();
            break;
        case "btnUnlink":
            client = zc_bind(zc_getDocumentInDocuments());
            client.command('removeCodes');
            zc_clearRegistry();
            break;
        case "btnAddNote":
            client = zc_bind(zc_getDocumentInDocuments());
            client.command('addNote');
            zc_clearRegistry();
            break;
        case "btnTest":
            // const commandUrl = 'http://127.0.0.1:23119/connector/document/execCommand';
            // const respondUrl = 'http://127.0.0.1:23119/connector/document/respond';
            // const req = (async () => {
            //     return postRequestNative(commandUrl, {
            //         command: 'addEditCitation',
            //         docId: 'askldfjwoiquerowqiaslkdfjlskajeiow'
            //     });
            // })();
            // console.log(req);
            // break;
            
            // const req = new XMLHttpRequest();
            // req.open("POST", commandUrl, false);
            // req.setRequestHeader('Content-type', 'application/json; charset=utf-8');
            // req.send({
            //     command: 'addEditCitation',
            //     docId: 'sakljdfoiwueroiwqulkasjfdl'
            // });
            // console.log(req.responseText);

            // wps.OAAssist.ShellExecute("/usr/bin/touch", "/home/tkw/test.txt");
            break;
        default:
            break
    }
    return true
}

function GetImage(control) {
    const eleId = control.Id
    switch (eleId) {
        case "btnAddEditCitation":
            return "images/addEditCitation.svg";
        case "btnAddEditBib":
            return "images/addEditBib.svg";
        case "btnRefresh":
            return "images/refresh.svg";
        case "btnPref":
            return "images/pref.svg";
        case "btnAddNote":
            return "images/addNote.svg";
        case "btnUnlink":
            return "images/unlink.svg";
        case "btnExport":
            return "images/export.svg";
        default:
            break;
    }
    return "images/default.svg";
}

