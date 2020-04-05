import os

if __name__ == "__main__":
    os.system("sudo /home/shazhubusha/.local/bin/pipenv install")
    os.system("sudo mv ./rec_adio.service /etc/systemd/system/")
    os.system("sudo systemctl daemon-reload")
    os.system("sudo systemctl enable rec_adio.service")
    os.system("sudo systemctl start rec_adio.service")
