require.config({
    paths: {
        vs: "https://unpkg.com/monaco-editor@0.45.0/min/vs"
    }
});

require(["vs/editor/editor.main"], function () {

    window.editor = monaco.editor.create(
        document.getElementById("editor"),
        {
            value: `print("Hello Krishna 🚀")`,
            language: "python",
            theme: "vs-dark",
            fontSize: 15,
            automaticLayout: true
        }
    );

});
