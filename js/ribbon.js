// Shouldn't be needing this if using the latest version of WPS
const WPS_Enum = {
    msoCTPDockPositionLeft: 0,
    msoCTPDockPositionRight: 2,
    msoPropertyTypeString: 4,
    wdAlignParagraphJustify: 3,
    wdAlignTabLeft: 0,
    wdCharacter: 1,
    wdCollapseEnd: 0,
    wdCollapseStart: 1,
    wdFieldAddin: 81,
    wdLineBreak: 6,
    wdParagraph: 4
};

// Storing global variables
const GLOBAL_MAP = {};

/**
 * Callback for plugin loading.
**/
function OnAddinLoad(ribbonUI) {
    if (typeof (wps.Enum) !== "object") {
        wps.Enum = WPS_Enum;
        zc_alert('You are using an old version of WPS, this plugin might not work properly!');
    }
    if (typeof (wps.ribbonUI) !== "object"){
        wps.ribbonUI = ribbonUI;
    }

    GLOBAL_MAP.isWin = Boolean(wps.Env.GetProgramDataPath());
    GLOBAL_MAP.osSep = GLOBAL_MAP.isWin ? '\\' : '/';
    GLOBAL_MAP.instDir = GLOBAL_MAP.isWin ?
        wps.Env.GetAppDataPath().replaceAll('/', '\\') + `\\kingsoft\\wps\\jsaddons\\wps-zotero_${VERSION}`:
        wps.Env.GetHomePath() + `/.local/share/Kingsoft/wps/jsaddons/wps-zotero_${VERSION}`;
    GLOBAL_MAP.proxyPath = GLOBAL_MAP.instDir + GLOBAL_MAP.osSep + 'proxy.py';

    // Start http proxy server
    if (GLOBAL_MAP.isWin) {
        wps.OAAssist.ShellExecute('pythonw.exe', GLOBAL_MAP.proxyPath);
    }
    else {
        wps.OAAssist.ShellExecute('python3', GLOBAL_MAP.proxyPath);
    }
    
    // Exit the proxy server when the application quits.
    Application.ApiEvent.AddApiEventListener("ApplicationQuit", () => {
        // NOTE: This event is never received on Windows, so the proxy server can't be stopped and there's nothing I can do.
        postRequestXHR('http://127.0.0.1:21931/stopproxy', null);
    });
    
    return true
}

/**
 * Callback for button clicking events.
**/
function OnAction(control) {
    const eleId = control.Id
    switch (eleId) {
        case "btnAddEditCitation":
            // IMPORTANT: Release references on the document objects!!!
            zc_bind().command('addEditCitation');
            zc_clearRegistry();
            break;
        case "btnAddEditBib":
            zc_bind().command('addEditBibliography');
            zc_clearRegistry();
            break;
        case "btnRefresh":
            zc_bind().import();
            // Must open a new client, since import will not register fields to zc_bind().
            zc_bind().command('refresh');
            zc_clearRegistry();
            break;
        case "btnPref":
            zc_bind().command('setDocPrefs');
            zc_clearRegistry();
            break;
        case "btnExport":
            if (confirm('Convert this document to a format for other word processors to import from? You may want to make a backup first.'))
            {
               zc_bind().export();
            }
            break;
        case "btnUnlink":
            zc_bind().command('removeCodes');
            zc_clearRegistry();
            break;
        case "btnAddNote":
            zc_bind().command('addNote');
            zc_clearRegistry();
            break;
        case "btnAbout":
            alert(`WPS-Zotero (${VERSION})\n\nThis add-on is licensed under GPL-3.0: <http://www.gnu.org/licenses/>, it comes with no warranty.\n\nAuthor: Tang, Kewei\nhttps://github.com/tankwyn/WPS-Zotero`);
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

