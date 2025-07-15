const vscode = require('vscode');
const axios = require('axios');

function activate(context) {
  vscode.workspace.onDidSaveTextDocument(async (doc) => {
    if (!['cpp', 'py'].includes(doc.languageId)) return;
    const res = await axios.post('http://localhost:5000/complexity', doc.getText());
    const { hotspots } = res.data;
    const diagnostics = hotspots.map(line => new vscode.Diagnostic(new vscode.Range(line-1,0,line-1,1), 'Complexity Hotspot', vscode.DiagnosticSeverity.Warning));
    const collection = vscode.languages.createDiagnosticCollection('quantlint');
    collection.set(doc.uri, diagnostics);
  });

  const fixCmd = vscode.commands.registerCommand('quantlint.fixHotspot', async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;
    const res = await axios.post('http://localhost:5000/suggest', editor.document.getText());
    vscode.window.showInformationMessage(res.data.diff);
  });
  context.subscriptions.push(fixCmd);
}

exports.activate = activate;
