// ⭐ Default templates
const templates = {
python: `print("Hello Krishna-Kapoor 🚀")`,

javascript: `console.log("Hello Krishna-Kapoor 🚀");`,

cpp: `#include <iostream>
using namespace std;

int main(){
    cout << "Hello Krishna-Kapoor";
}`,

c: `#include <stdio.h>

int main(){
    printf("Hello Krishna-Kapoor");
}`,

java: `public class Main {
    public static void main(String[] args){
        System.out.println("Hello Krishna-Kapoor");
    }
}`
};


// =========================
// GLOBAL STATE
// =========================
let selectedLang = "python";
let socket = null;


// =========================
// SAFE DOM HELPERS
// =========================
function showInputBox(show){
    const el = document.getElementById("inputBox");
    if(el) el.style.display = show ? "block" : "none";
}

function setOutput(text){
    const el = document.getElementById("output");
    if(el) el.innerText = text;
}


// =========================
// WEBSOCKET CONNECT
// =========================
function connectSocket() {

    socket = new WebSocket("ws://127.0.0.1:8000/ws/code/");

    socket.onopen = () => {
        console.log("WebSocket Connected ✅");
    };

    socket.onmessage = (event) => {
        let data = {};
        try {
            data = JSON.parse(event.data);
        } catch {
            console.log("Invalid JSON from server");
            return;
        }

        if(data.status === "need_input"){
            showInputBox(true);
        }

        if(data.output){
            setOutput(data.output);
        }

        if(data.error){
            setOutput(data.error);
        }
    };

    socket.onclose = () => {
        console.log("Socket closed — reconnecting...");
        setTimeout(connectSocket, 1500);
    };

    socket.onerror = (e) => {
        console.log("Socket error", e);
    };
}


// =========================
// LANGUAGE SWITCH
// =========================
function setLang(e, lang) {

    selectedLang = lang;

    document.querySelectorAll(".lang-btn")
        .forEach(btn => btn.classList.remove("active"));

    e.target.classList.add("active");

    const monacoLangMap = {
        python: "python",
        javascript: "javascript",
        cpp: "cpp",
        c: "c",
        java: "java"
    };

    monaco.editor.setModelLanguage(
        window.editor.getModel(),
        monacoLangMap[lang]
    );

    window.editor.setValue(templates[lang]);
}



// =========================
// RUN CODE
// =========================
function runCode() {

    if(!window.editor) return;

    const code = window.editor.getValue();
    const stdinEl = document.getElementById("stdin");
    const userInput = stdinEl ? stdinEl.value : "";

    setOutput("Running...");

    if(socket && socket.readyState === WebSocket.OPEN){
        socket.send(JSON.stringify({
            action: "run",
            code,
            language: selectedLang,
            stdin: userInput
        }));
    }
    else{
        setOutput("WebSocket not connected ❌");
    }
}



// =========================
// INPUT DETECTION
// =========================
function detectInputNeeded(){

    if(!window.editor) return;

    const code = window.editor.getValue();

    const needsInput =
        /cin\s*>>/.test(code) ||
        /scanf\s*\(/.test(code) ||
        /input\s*\(/.test(code) ||
        /Scanner/.test(code);

    showInputBox(needsInput);
}



// =========================
// MONACO LISTENER
// =========================
function attachEditorListener(){

    if(!window.editor) return;

    window.editor.onDidChangeModelContent(() => {
        detectInputNeeded();
    });
}



// =========================
// INIT (WAIT FOR MONACO)
// =========================
window.onload = () => {

    connectSocket();

    // Monaco async load hota hai — wait loop
    const waitEditor = setInterval(() => {

        if(window.editor){

            clearInterval(waitEditor);

            window.editor.setValue(templates["python"]);
            attachEditorListener();
            detectInputNeeded();

            console.log("Editor Ready ✅");
        }

    }, 100);
};
