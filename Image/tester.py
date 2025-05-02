import subprocess
import os
import hashlib
import shutil
import yaml

from comparison_page_generator import *

class CompileCommand:
    def __init__(self, parameters):
        self.run = parameters["run"]
        self.runCondition = parameters["runCondition"]

        if "compile" in parameters.keys():
            self.compile = parameters["compile"]
        else:
            self.compile = None

    def getCompileCommand(self, filename):
        if self.compile is None:
            return None

        cmd = self.compile.replace("{FILENAME}", filename)
        return list(cmd.split())

    def getRunCommand(self, filename, sudo = False):
        cmd = self.run.replace("{FILENAME}", filename)

        if sudo:
            return list(cmd.split())
        else:
            tmp = ["sudo", "-u", "user"]
            tmp.extend(list(cmd.split()))
            return tmp

    def getRunCondition(self, filename):
        return self.runCondition.replace("{FILENAME}", filename)

class Tester:
    def __init__(self):
        with open("./iterations.txt") as f:
            try:
                self.iterations = int(f.readline())
            except ValueError:
                with open("./protocol.txt", "w") as protocol:
                    protocol.write(f"error\nrunning\nInvalid iterations count")
                exit(1)

        if not (1 <= self.iterations <= 300):
            with open("./protocol.txt", "w") as protocol:
                protocol.write(f"error\nrunning\nInvalid iterations count")

            exit(1)

        with open("compile.yaml") as f:
            cmds = yaml.safe_load(f)
            self.compileCommands = {}

            for key in cmds.keys():
                self.compileCommands[key] = CompileCommand(cmds[key])


    def protectFiles(self):
        subprocess.run(["chmod", "755", "."])
        subprocess.run(["chmod", "500", "testgen." + self.getLanguage("testgen")])
        subprocess.run(["chmod", "500", "reference." + self.getLanguage("reference")])
        subprocess.run(["chmod", "500", "tester." + self.getLanguage("tester")])
        subprocess.run(["chmod", "544", "iterations.txt"])
        subprocess.run(["chmod", "500", "java_compile.py"])
        subprocess.run(["chmod", "500", "compile.yaml"])
        subprocess.run(["chmod", "500", "comparison_page_generator.py"])
        subprocess.run(["chmod", "600", "protocol.txt"])
        subprocess.run(["chmod", "555", "probe." + self.getLanguage("probe")])

    def getLanguage(self, filename):
        for file in os.listdir("."):
            if "." in file and ".exe" not in file:
                name = file.split(".")[0]
                extension = file.split(".")[-1]

                if filename == name:
                    return extension

        return "undefined"

    def performFile(self, filename: str, timeout=None, runCompiler=True, io=True, sudo=False):
        try:
            lang = self.getLanguage(filename)

            if lang == "undefined":
                return "error", f"Can not identify programming language of the {filename} program"

            if runCompiler:
                compileCommand = self.compileCommands[lang].getCompileCommand(filename)

                if compileCommand is not None:
                    subprocess.run(compileCommand, stderr=subprocess.PIPE, check=True)

            if os.path.exists(self.compileCommands[lang].getRunCondition(filename)):
                if io:
                    with open('input.txt', 'r') as input_file, open('output.txt', 'w') as output_file:
                        subprocess.run(self.compileCommands[lang].getRunCommand(filename, sudo), timeout=timeout, check=True,
                                       stdin=input_file, stdout=output_file)

                else:
                    subprocess.run(self.compileCommands[lang].getRunCommand(filename, sudo), timeout=timeout, check=True)

            return "ok", None
        except subprocess.TimeoutExpired:
            return "timedOut", f"Timed out. Process execution took more than {timeout} seconds"
        except subprocess.CalledProcessError as e:
            return "error", e.stderr.decode() if e.stderr is not None else e.returncode

    def runTestGen(self):
        status, error = self.performFile("testgen", 15, io=False, sudo=True)

        if status == "error" or status == "timedOut":
            with open("./protocol.txt", "w") as protocol:
                protocol.write(f"error\ntestgen\n{error}")

        return status != "error"

    def runReference(self, timeout=None, runCompiler=True):
        status, error = self.performFile("reference", timeout, runCompiler, sudo=True)

        if status == "error" or status == "timedOut":
            with open("./protocol.txt", "w") as protocol:
                protocol.write(f"error\nreference\n{error}")

        return status != "error"

    def runProbe(self, timeout=None, runCompiler=True):
        status, error = self.performFile("probe", timeout, runCompiler)

        if status == "error" or status == "timedOut":
            with open("./protocol.txt", "w") as protocol:
                if f"{error}" == "-11":
                    referenceOutputContent = self.getFileContent('./referenceOutput.txt')
                    testContent = self.getFileContent('./input.txt')
                    protocol.write(f"error\nprobe\nSegmentation fault ({error}) on test:\n{testContent}\n\nReference output:\n{referenceOutputContent}")
                else:
                    referenceOutputContent = self.getFileContent('./referenceOutput.txt')
                    testContent = self.getFileContent('./input.txt')
                    protocol.write(f"error\nprobe\n{error}\n\nTest:\n{testContent}\n\nReference output:\n{referenceOutputContent}")

        return status != "error"

    def getFileHash(self, filename):
        sha256_hash = hashlib.sha256()
        with open(filename, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
            return str(sha256_hash.hexdigest())

    def moveReferenceOutput(self):
        if not os.path.exists("./output.txt"):
            with open("./protocol.txt", "w") as protocol:
                protocol.write(f"error\ntesting\nIt seems reference program did not create output.txt file.")

            exit(1)

        shutil.copy("./output.txt", "referenceOutput.txt")

    def getFileContent(self, filename):
        f = open(filename)
        ret = ''.join(f.readlines())
        f.close()

        return ret

    def compareResults(self):
        if not os.path.exists("./output.txt"):
            with open("./protocol.txt", "w") as protocol:
                protocol.write(f"error\ntesting\nIt seems probe program did not create output.txt file.")

            exit(1)

        if self.getFileHash("./referenceOutput.txt") != self.getFileHash("./output.txt"):
            with open("./protocol.txt", "w") as protocol:
                referenceOutputContent = self.getFileContent('./referenceOutput.txt')
                probeOutputContent = self.getFileContent('./output.txt')
                testContent = self.getFileContent('./input.txt')
                protocol.write(f"error\nanswer\nExpected output:\n{referenceOutputContent}\n\nGot:\n{probeOutputContent}\n\nTest:\n{testContent}\n")
                create_comparison_page(referenceOutputContent, probeOutputContent, testContent)

            return False
        return True

    def start(self):
        self.protectFiles()
        for i in range(self.iterations):
            if not self.runTestGen():
                exit()

            if not self.runReference(runCompiler=i == 0):
                exit()

            self.moveReferenceOutput()

            if not self.runProbe(runCompiler=i == 0):
                exit()

            if not self.compareResults():
                exit()

        with open("./protocol.txt", "w") as protocol:
            protocol.write(f"ok\n")



tester = Tester()
tester.start()

