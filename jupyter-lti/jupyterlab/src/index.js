"use strict";
exports.__esModule = true;
var disposable_1 = require("@phosphor/disposable");
var apputils_1 = require("@jupyterlab/apputils");
/**
 * The plugin registration information.
 */
var plugin = {
    activate: activate,
    id: 'jupyter-lti:buttonPlugin',
    autoStart: true
};
var getUrl = function (assignment_id) {
    var proto = window.location.protocol;
    var parts = window.location.pathname.split('/');
    var version = parts[1];
    var serverName = parts[6];
    var projectName = parts[4];
    var accountName = parts[2];
    return proto + "//" + window.location.host + "/" + version + "/" + accountName + "/projects/" + projectName + "/servers/" + serverName + "/lti/assignment/" + assignment_id + "/";
};
var sendCallback = function (assignment_id, context) { return function () {
    var url = getUrl(assignment_id);
    var buttons = [apputils_1.Dialog.okButton()];
    var errorDialog = {
        title: 'Error',
        body: 'There was an error while sending submission',
        buttons: buttons
    };
    context.save();
    fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json;charset=utf-8' },
        referrerPolicy: 'no-referrer'
    })
        .then(function (res) {
        if (!res.ok) {
            console.log(res);
            apputils_1.showDialog(errorDialog);
        }
        else {
            apputils_1.showDialog({
                title: 'Success',
                body: 'Your assignment was sent to Canvas',
                buttons: buttons
            });
        }
    })["catch"](function (error) {
        apputils_1.showDialog(errorDialog);
        console.error(error);
    });
}; };
var resetCallback = function (assignment_id, context) { return function () {
    var sendUrl = getUrl(assignment_id);
    var url = sendUrl + "reset/";
    var buttons = [apputils_1.Dialog.okButton()];
    var errorDialog = {
        title: 'Error',
        body: 'There was an error while reseting assignment file',
        buttons: buttons
    };
    context.save();
    fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json;charset=utf-8' },
        referrerPolicy: 'no-referrer'
    })
        .then(function (res) {
        if (!res.ok) {
            console.log(res);
            apputils_1.showDialog(errorDialog);
        }
        else {
            apputils_1.showDialog({
                title: 'Success',
                body: 'Your assignment file was reset',
                buttons: buttons
            });
        }
    })["catch"](function (error) {
        apputils_1.showDialog(errorDialog);
        console.error(error);
    });
}; };
/**
 * A notebook widget extension that adds a button to the toolbar.
 */
var ButtonExtension = /** @class */ (function () {
    function ButtonExtension(assignment_id) {
        this.assignment_id = assignment_id;
    }
    /**
     * Create a new extension object.
     */
    ButtonExtension.prototype.createNew = function (panel, context) {
        var self = this;
        var sendButton = new apputils_1.ToolbarButton({
            className: 'mySendButton',
            iconClassName: 'fa fa-share-square',
            onClick: sendCallback(self.assignment_id, context),
            tooltip: 'Submit to Canvas'
        });
        var resetButton = new apputils_1.ToolbarButton({
            className: 'myResetButton',
            iconClassName: 'fa fa-undo',
            onClick: function () {
                apputils_1.showDialog({
                    title: 'Reset assignment file',
                    body: 'Are you sure you want to reset assignment file?',
                    buttons: [apputils_1.Dialog.cancelButton(), apputils_1.Dialog.okButton()]
                }).then(function (result) {
                    console.log(result);
                    if (result.button.accept) {
                        resetCallback(self.assignment_id, context)();
                    }
                });
            },
            tooltip: 'Reset assignment file'
        });
        panel.toolbar.insertItem(0, 'send', sendButton);
        panel.toolbar.insertItem(0, 'reset', resetButton);
        return new disposable_1.DisposableDelegate(function () {
            sendButton.dispose();
            resetButton.dispose();
        });
    };
    return ButtonExtension;
}());
exports.ButtonExtension = ButtonExtension;
/**
 * Activate the extension.
 */
function activate(app) {
    var query = new URLSearchParams(window.location.search);
    var assignment_id = query.get('assignment_id');
    if (!!assignment_id) {
        app.docRegistry.addWidgetExtension('Notebook', new ButtonExtension(query.get('assignment_id')));
    }
}
/**
 * Export the plugin as default.
 */
exports["default"] = plugin;
