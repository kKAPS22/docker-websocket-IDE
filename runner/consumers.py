import json
import subprocess
import tempfile
import os

from channels.generic.websocket import AsyncWebsocketConsumer


DOCKER_IMAGE = "krishnakapoor1/multi-runner"


class CodeConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

    async def receive(self, text_data):

        data = json.loads(text_data)
        code = data["code"]
        lang = data["language"]
        user_input = data.get("stdin", "")

        ext_map = {
            "python": ".py",
            "javascript": ".js",
            "cpp": ".cpp",
            "c": ".c",
            "java": ".java"
        }

        if lang not in ext_map:
            await self.send(json.dumps({"output": "Unsupported language"}))
            return

        # temp file create
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext_map[lang], mode="w", encoding="utf-8") as f:
            f.write(code)
            filename = f.name

        container_file = {
            "python": "code.py",
            "javascript": "code.js",
            "cpp": "code.cpp",
            "c": "code.c",
            "java": "Main.java"
        }

        run_map = {
            "python": ["python3", "/app/code.py"],
            "javascript": ["node", "/app/code.js"],
            "cpp": ["bash", "-c", "g++ /app/code.cpp -o /app/out && /app/out"],
            "c": ["bash", "-c", "gcc /app/code.c -o /app/out && /app/out"],
            "java": ["bash", "-c", "javac /app/Main.java && java -cp /app Main"]
        }

        cmd = [
            "docker","run","--rm","-i",
            "--memory=256m",
            "--cpus=0.5",
            "-v", f"{filename}:/app/{container_file[lang]}",
            DOCKER_IMAGE
        ] + run_map[lang]

        try:
            result = subprocess.run(
                cmd,
                input=user_input + "\n",
                capture_output=True,
                text=True,
                timeout=15
            )

            output = result.stdout or result.stderr

        except Exception as e:
            output = str(e)

        finally:
            os.remove(filename)

        await self.send(json.dumps({"output": output}))
