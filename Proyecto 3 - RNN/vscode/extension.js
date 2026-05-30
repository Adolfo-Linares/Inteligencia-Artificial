const vscode = require("vscode");
const http = require("http");

function llamarFlask(endpoint, payload) {
    return new Promise((resolve, reject) => {
        const data = JSON.stringify(payload);

        const options = {
            hostname: "127.0.0.1",
            port: 5000,
            path: `/api/${endpoint}`,
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Content-Length": Buffer.byteLength(data)
            },
            timeout: 60000
        };

        const req = http.request(options, (res) => {
            let body = "";

            res.on("data", (chunk) => {
                body += chunk;
            });

            res.on("end", () => {
                try {
                    resolve(JSON.parse(body));
                } catch (e) {
                    reject(new Error("Respuesta invalida del servidor"));
                }
            });
        });

        req.on("error", (err) => {
            reject(new Error("No se pudo conectar con Flask: " + err.message));
        });

        req.on("timeout", () => {
            req.destroy();
            reject(new Error("Tiempo agotado conectando con Flask"));
        });

        req.write(data);
        req.end();
    });
}

async function autocompletarLinea() {
    const editor = vscode.window.activeTextEditor;

    if (!editor) {
        return;
    }

    const position = editor.selection.active;
    const currentLine = editor.document.lineAt(position.line).text;
    const prefix = currentLine.slice(0, position.character);

    if (!prefix.trim()) {
        return;
    }

    vscode.window.setStatusBarMessage("RNN generando sugerencia...", 2000);

    try {
        const response = await llamarFlask("complete", {
            prefix: prefix,
            max_new: 120,
            temperature: 0.25
        });

        if (response.ok && response.suffix) {
            await editor.edit((editBuilder) => {
                editBuilder.insert(position, response.suffix);
            });
        } else {
            vscode.window.showErrorMessage("La RNN no genero sugerencia");
        }

    } catch (error) {
        vscode.window.showErrorMessage("Error: " + error.message);
    }
}

function activate(context) {
    console.log("Extension RNN activa");

    const comando = vscode.commands.registerCommand(
        "rnnKeras.complete",
        autocompletarLinea
    );

    context.subscriptions.push(comando);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};