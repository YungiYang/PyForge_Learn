const vscode = require('vscode');
const http = require('http');
const https = require('https');

let diagnosticCollection;
let statusBarItem;
let debounceTimer = null;
let currentDiagnosticsData = [];

/**
 * Активация расширения VS Code
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    console.log('PyForge AI Mentor Extension activated');

    diagnosticCollection = vscode.languages.createDiagnosticCollection('pyforge');
    context.subscriptions.push(diagnosticCollection);

    // Статус-бар
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.command = 'pyforge.inspectFile';
    statusBarItem.text = '$(sparkle) PyForge: Наставник';
    statusBarItem.tooltip = 'PyForge AI: Нажмите для инспекции текущего Python файла';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // Регистрация команд
    context.subscriptions.push(
        vscode.commands.registerCommand('pyforge.inspectFile', () => {
            const editor = vscode.window.activeTextEditor;
            if (editor && editor.document.languageId === 'python') {
                runInspection(editor.document, true);
            } else {
                vscode.window.showInformationMessage('Откройте Python (.py) файл для анализа в PyForge.');
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('pyforge.openWebUI', () => {
            const config = vscode.workspace.getConfiguration('pyforge');
            const url = config.get('serverUrl') || 'http://127.0.0.1:8000';
            vscode.env.openExternal(vscode.Uri.parse(url));
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('pyforge.randomTask', async () => {
            const config = vscode.workspace.getConfiguration('pyforge');
            const serverUrl = config.get('serverUrl') || 'http://127.0.0.1:8000';
            
            const libs = ['re', 'fastapi', 'kivy', 'openpyxl', 'pathlib', 'requests', 'sqlite3', 'json', 'pandas', 'pydantic', 'collections', 'datetime', 'customtkinter'];
            const chosen = await vscode.window.showQuickPick(libs, {
                placeHolder: 'Выберите библиотеку для генерации случайной задачи'
            });
            if (!chosen) return;

            try {
                const res = await postJson(`${serverUrl}/api/practice/random-by-library`, { library: chosen });
                if (res && res.task) {
                    const doc = await vscode.workspace.openTextDocument({
                        content: `# PyForge Практика: ${res.task.title}\n# Сложность: ${res.task.difficulty} | Награда: ⭐ ${res.task.reward_stars} звезд\n\n"""\n${res.task.description}\n"""\n\n${res.task.starter_code}`,
                        language: 'python'
                    });
                    await vscode.window.showTextDocument(doc);
                    vscode.window.showInformationMessage(`🎲 Задача по ${chosen} сгенерирована! Награда: ⭐ ${res.task.reward_stars} звезд.`);
                }
            } catch (err) {
                vscode.window.showErrorMessage(`Ошибка связи с сервером PyForge: ${err.message}. Убедитесь, что run.py запущен на порту 8000.`);
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('pyforge.syncWithPyForge', () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) return;
            const config = vscode.workspace.getConfiguration('pyforge');
            const url = config.get('serverUrl') || 'http://127.0.0.1:8000';
            vscode.env.openExternal(vscode.Uri.parse(`${url}/#sandbox`));
            vscode.window.showInformationMessage('Код готов к синхронизации с PyForge Studio');
        })
    );

    // CodeAction Provider для быстрого исправления (Quick Fixes)
    context.subscriptions.push(
        vscode.languages.registerCodeActionsProvider('python', new PyForgeActionProvider(), {
            providedCodeActionKinds: [vscode.CodeActionKind.QuickFix]
        })
    );

    // Слушатели событий редактора
    context.subscriptions.push(
        vscode.workspace.onDidChangeTextDocument(event => {
            const config = vscode.workspace.getConfiguration('pyforge');
            if (!config.get('enableLiveDiagnostics')) return;

            if (event.document.languageId === 'python') {
                const debounceMs = config.get('debounceMs') || 350;
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    runInspection(event.document, false);
                }, debounceMs);
            }
        })
    );

    context.subscriptions.push(
        vscode.window.onDidChangeActiveTextEditor(editor => {
            if (editor && editor.document.languageId === 'python') {
                runInspection(editor.document, false);
            }
        })
    );

    // Начальная инспекция при старте
    if (vscode.window.activeTextEditor && vscode.window.activeTextEditor.document.languageId === 'python') {
        runInspection(vscode.window.activeTextEditor.document, false);
    }
}

/**
 * Запуск ИИ-инспекции документа через PyForge Backend
 */
async function runInspection(document, showNotification = false) {
    const config = vscode.workspace.getConfiguration('pyforge');
    const serverUrl = config.get('serverUrl') || 'http://127.0.0.1:8000';
    const code = document.getText();

    try {
        const response = await postJson(`${serverUrl}/api/mentor/inspect`, { code: code });
        const diagnostics = [];
        currentDiagnosticsData = [];

        if (response && response.issues && response.issues.length > 0) {
            currentDiagnosticsData = response.issues;

            for (const issue of response.issues) {
                const line = Math.max(0, (issue.line || 1) - 1);
                const col = Math.max(0, (issue.column || 1) - 1);
                const lineText = document.lineAt(Math.min(line, document.lineCount - 1)).text;
                
                const range = new vscode.Range(line, col, line, Math.max(col + 1, lineText.length));

                let severity = vscode.DiagnosticSeverity.Warning;
                if (issue.severity === 'error') severity = vscode.DiagnosticSeverity.Error;
                if (issue.severity === 'info') severity = vscode.DiagnosticSeverity.Information;

                const diag = new vscode.Diagnostic(
                    range,
                    `[PyForge AI] ${issue.title}: ${issue.message}\n💡 Совет: ${issue.advice}`,
                    severity
                );
                diag.source = 'PyForge AI';
                diag.code = issue.fix_code ? 'pyforge-fix' : undefined;
                diag.customFix = issue.fix_code;
                diagnostics.push(diag);
            }

            statusBarItem.text = `$(error) PyForge: ${response.issues.length} замечаний`;
            statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
        } else {
            statusBarItem.text = `$(check) PyForge: Ошибок нет ✨`;
            statusBarItem.backgroundColor = undefined;
        }

        diagnosticCollection.set(document.uri, diagnostics);

        if (showNotification) {
            if (diagnostics.length === 0) {
                vscode.window.showInformationMessage('✨ PyForge AI: Ошибок в коде не обнаружено. Отличный код!');
            } else {
                vscode.window.showWarningMessage(`PyForge AI обнаружил ${diagnostics.length} потенциальных проблем в коде.`);
            }
        }
    } catch (err) {
        statusBarItem.text = `$(plug) PyForge: Офлайн`;
        statusBarItem.backgroundColor = undefined;
    }
}

/**
 * Провайдер Quick Fix действий в VS Code
 */
class PyForgeActionProvider {
    provideCodeActions(document, range, context, token) {
        const actions = [];
        for (const diagnostic of context.diagnostics) {
            if (diagnostic.source === 'PyForge AI' && diagnostic.customFix) {
                const action = new vscode.CodeAction(`💡 Применить исправление от PyForge AI`, vscode.CodeActionKind.QuickFix);
                action.edit = new vscode.WorkspaceEdit();
                const fullRange = new vscode.Range(0, 0, document.lineCount, 0);
                action.edit.replace(document.uri, fullRange, diagnostic.customFix);
                action.isPreferred = true;
                action.diagnostics = [diagnostic];
                actions.push(action);
            }
        }
        return actions;
    }
}

/**
 * Хелпер отправки HTTP POST запроса
 */
function postJson(urlStr, data) {
    return new Promise((resolve, reject) => {
        const url = new URL(urlStr);
        const postData = JSON.stringify(data);

        const options = {
            hostname: url.hostname,
            port: url.port || (url.protocol === 'https:' ? 443 : 80),
            path: url.pathname,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
            },
            timeout: 3000
        };

        const client = url.protocol === 'https:' ? https : http;
        const req = client.request(options, res => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => {
                try {
                    const parsed = JSON.parse(body);
                    resolve(parsed);
                } catch (e) {
                    reject(new Error('Некорректный JSON от сервера'));
                }
            });
        });

        req.on('error', err => reject(err));
        req.on('timeout', () => {
            req.destroy();
            reject(new Error('Таймаут соединения с сервером PyForge'));
        });

        req.write(postData);
        req.end();
    });
}

function deactivate() {
    if (diagnosticCollection) {
        diagnosticCollection.clear();
        diagnosticCollection.dispose();
    }
}

module.exports = {
    activate,
    deactivate
};
