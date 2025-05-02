# ITP Helper Bot: Tester for Assignments

![Logo](logo.jpg)

The ITP Helper Bot is a Telegram bot that is able to test solutions for assignments in various subjects. A reference solution and a test generator are loaded into the bot. After that, the students send their solution as an attached file to the bot, and the bot generates from 0 to 300 random tests (depending on how many the student specified) and submits them to the reference program. The reference program gives the correct answer, after which the same tests are passed through the solution being tested. Next, the results are compared, and if there is any difference, the student is sent a test protocol and a web page on which there is a comparison of the answers of the reference program and the probe program. All student solutions are run in their own separate Docker container. The bot keeps a log so that the maintainer can track usage statistics and any issues. You can easily add new programming language to the bot at any time. To do this, add a command to install the language you need in the Dockerfile, as well as commands to compile and run in the `compile.yaml` file, then restart the bot with the new Docker image.


### Setup:
Required system: Any GNU/Linux distribution or MacOS. For simplicity, the following instructions suppose that you use Ubuntu 20.04. For other distros ans MacOS steps are simillar.

Required Python version: 3.12 or above

1. Install python 3.12:
   ```
   sudo add-apt-repository ppa:deadsnakes/ppa
   sudo apt update
   sudo apt install python3.12
   ```

2. Install Docker:
   ```
   sudo apt-get install ca-certificates curl
   sudo install -m 0755 -d /etc/apt/keyrings
   sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
   sudo chmod a+r /etc/apt/keyrings/docker.asc
   echo \
   "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
   $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
   sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   sudo apt update
   sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
   ```
3. Clone this repository: `git clone https://github.com/Delta-Software-Innopolis/ITPHelperBot.git`
4. Move to the directory of the bot: `cd ITPHelperBot`
5. Create new screen for the bot: `screen -S bot`
6. Create virtual environment: `python3.12 -m venv venv`
7. Activate virtual environment: `source venv/bin/activate`
8. Install all requirements: `pip install -r requirements.txt`
9. Go to the Image directory: `cd Image`
10. Build docker image: `docker image build .`
11. Copy ID of the docker image
12. Go back to the root directory: `cd ..`
13. Open `token.yaml` file and insert your token in the quotes
14. Run bot via `python3.12 main.py INSERT_ID_OF_DOCKER_IMAGE`
15. Leave bot screen via `^A+D`. To connect the screen again use `screen -r bot`.
