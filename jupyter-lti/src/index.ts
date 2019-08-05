import { IDisposable, DisposableDelegate } from '@phosphor/disposable';

import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ToolbarButton, showDialog, Dialog } from '@jupyterlab/apputils';

import { DocumentRegistry } from '@jupyterlab/docregistry';

import { NotebookPanel, INotebookModel } from '@jupyterlab/notebook';

/**
 * The plugin registration information.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  activate,
  id: 'jupyter-lti:buttonPlugin',
  autoStart: true
};

let getUrl = (assignment_id: string) => {
  let proto = window.location.protocol;
  let parts = window.location.pathname.split('/');
  let version = parts[1];
  let serverName = parts[6];
  let projectName = parts[4];
  let accountName = parts[2];
  return `${proto}//${
    window.location.host
  }/${version}/${accountName}/projects/${projectName}/servers/${serverName}/lti/assignment/${assignment_id}/`;
};

let sendCallback = (
  assignment_id: string,
  context: DocumentRegistry.IContext<INotebookModel>
) => () => {
  let url = getUrl(assignment_id);
  let buttons = [Dialog.okButton()];
  let errorDialog = {
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
    .then(res => {
      if (!res.ok) {
        console.log(res);
        showDialog(errorDialog);
      } else {
        showDialog({
          title: 'Success',
          body: 'Your assignment was sent to Canvas',
          buttons: buttons
        });
      }
    })
    .catch(error => {
      showDialog(errorDialog);
      console.error(error);
    });
};

let resetCallback = (
  assignment_id: string,
  context: DocumentRegistry.IContext<INotebookModel>
) => () => {
  let sendUrl = getUrl(assignment_id);
  let url = `${sendUrl}reset/`;
  let buttons = [Dialog.okButton()];
  let errorDialog = {
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
    .then(res => {
      if (!res.ok) {
        console.log(res);
        showDialog(errorDialog);
      } else {
        showDialog({
          title: 'Success',
          body: 'Your assignment file was reset',
          buttons: buttons
        });
      }
    })
    .catch(error => {
      showDialog(errorDialog);
      console.error(error);
    });
};

/**
 * A notebook widget extension that adds a button to the toolbar.
 */
export class ButtonExtension
  implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel> {
  assignment_id: string;
  constructor(assignment_id: string) {
    this.assignment_id = assignment_id;
  }
  /**
   * Create a new extension object.
   */
  createNew(
    panel: NotebookPanel,
    context: DocumentRegistry.IContext<INotebookModel>
  ): IDisposable {
    let self = this;
    let sendButton = new ToolbarButton({
      className: 'mySendButton',
      iconClassName: 'fa fa-share-square',
      onClick: sendCallback(self.assignment_id, context),
      tooltip: 'Submit to Canvas'
    });
    let resetButton = new ToolbarButton({
      className: 'myResetButton',
      iconClassName: 'fa fa-undo',
      onClick: () => {
        showDialog({
          title: 'Reset assignment file',
          body: 'Are you sure you want to reset assignment file?',
          buttons: [Dialog.cancelButton(), Dialog.okButton()]
        }).then(result => {
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
    return new DisposableDelegate(() => {
      sendButton.dispose();
      resetButton.dispose();
    });
  }
}

/**
 * Activate the extension.
 */
function activate(app: JupyterFrontEnd) {
  let query = new URLSearchParams(window.location.search);
  let assignment_id = query.get('assignment_id');
  if (!!assignment_id) {
    app.docRegistry.addWidgetExtension(
      'Notebook',
      new ButtonExtension(query.get('assignment_id'))
    );
  }
}

/**
 * Export the plugin as default.
 */
export default plugin;
