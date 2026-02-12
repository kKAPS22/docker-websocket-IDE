import subprocess#system ke commands run karne ke Liye [hum Docker run kar rahe ho isse]
import tempfile#temporary file banane ke liye
import json#frontend JSON data read/parse karne ke liye 
import os#operating system se related Kaam 
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


DOCKER_IMAGE = "krishnakapoor1/multi-runner"


def home(request):
    return render(request, "index.html")


@csrf_exempt
def run_code(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST only"})

    data = json.loads(request.body)

    code = data.get("code", "")
    lang = data.get("language", "").lower()
    user_input = data.get("stdin", "")

    #File-Extension-Map
    ext_map = {
        "python": ".py",
        "javascript": ".js",
        "cpp": ".cpp",
        "c": ".c",
        "java": ".java"
    }
    
    #Unsupported Language Check
    if lang not in ext_map:
        return JsonResponse({"error": "Unsupported language"})

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext_map[lang]) as f:
        f.write(code.encode())
        filename = f.name

    try:

        run_map = {
            "python": ["python3", "/app/code.py"],
            "javascript": ["node", "/app/code.js"],
            "cpp": ["bash", "-c", "g++ /app/code.cpp -o /app/out && /app/out"],
            "c": ["bash", "-c", "gcc /app/code.c -o /app/out && /app/out"],
            "java": ["bash", "-c", "javac /app/Main.java && java -cp /app Main"]
        }

        container_file = {
            "python": "code.py",
            "javascript": "code.js",
            "cpp": "code.cpp",
            "c": "code.c",
            "java": "Main.java"
        }

        cmd = [
            "docker", "run", "--rm", "-i",
            "--memory=256m",
            "--cpus=0.5",
            "-v", f"{filename}:/app/{container_file[lang]}",
            DOCKER_IMAGE
        ] + run_map[lang]

        result = subprocess.run(
            cmd,
            input=user_input + "\n",     # ⭐ IMPORTANT FIX
            capture_output=True,         # ⭐ CAPTURE OUTPUT
            text=True,
            timeout=20
        )

        return JsonResponse({
            "output": result.stdout,
            "error": result.stderr
        })

    except subprocess.TimeoutExpired:
        return JsonResponse({"error": "Execution timed out"})

    except Exception as e:
        return JsonResponse({"error": str(e)})

    finally:
        os.remove(filename)
