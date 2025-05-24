import os
import sys
import yaml

from aiogram.utils.formatting import Text, Code


if len(sys.argv) == 1:
    print("Docker image file is not specified", file=sys.stderr)
    sys.exit(0)

dockerImageNum = sys.argv[1]


def createTemplateIfNotExists(
    file_path: str,
    template: str
):
    """ 
    Ensures that file exists (in `file_path`) \\
    If not:
    - creates file
    - writes `template` into it
    """
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write(template)


if not os.path.exists("resources"):
    os.mkdir("resources")


createTemplateIfNotExists("resources/token.yaml",
    "token: \"\""
)

createTemplateIfNotExists("resources/banlist.yaml",
    "banned:\n"
    "- \"user-id\""
)

createTemplateIfNotExists("resources/moderators.txt",
    "user-id @username"
)


# Prepared resources (saved in repository)

with open("resources/compile.yaml") as f:
    compileCommands = yaml.safe_load(f)

with open("resources/messages.yaml") as f:
    messages = yaml.safe_load(f)


# Dynamic resources (created only in production)

with open("resources/token.yaml") as f:
    token = yaml.safe_load(f)["token"]
    if not token:
        print("Set token for your bot (./resources/token)")
        quit(1)

with open("resources/moderators.txt") as f:
    first_moder = f.readline()
    if first_moder == "user-id @username":
        print("Set main moderator (./resources/moderators.txt)")
        quit(1)

with open("resources/banlist.yaml") as f:
    banlist = yaml.safe_load(f)['banned']
    if "user-id" in banlist:
        banlist.remove("user-id")


def getLanguage(filename, dir = "."):
    for file in os.listdir(dir):
        name = file.split(".")[0]
        extension = file.split(".")[-1]

        if filename == name:
            return extension

    return "undefined"


def errorHandler(protocol, testCount: int):
    match (protocol[0].strip("\n")):
        case "ok":
            return Text(
                f"All {testCount} tests have been passed successfully."
                "This does not mean at all that your program 100% will pass all Codeforces tests."
                "We recommend running a few more checks to make sure that the program is really working correctly."
            )
        case "error":
            match (protocol[1].strip("\n")):
                case "running":
                    return Text(f"An error occurred when starting the tester. Message: {''.join(protocol[2::])}")
                case "testgen":
                    return Text(f"An error occurred when generating the test. Message: {''.join(protocol[2::])}")
                case "reference":
                    return Text(f"An error occurred when running the reference. Message: {''.join(protocol[2::])}")
                case "probe":
                    return Text(f"An error occurred when running the probe. Message: {''.join(protocol[2::])}")
                case "testing":
                    return Text(f"An error occurred during the testing process. Message: {''.join(protocol[2::])}")
                case "answer":
                    return Text("Got invalid answer from probe program. Message:\n") + Code(''.join(protocol[2::]))
