#!/bin/bash

# chmod +x scripts/setup_sudoers.sh && ./scripts/setup_sudoers.sh

USER_NAME="ubuntu"
PROJECT_NAME="eng-iter-telegram-bot"
SUDOERS_FILE="/etc/sudoers.d/bots_deploy"

echo "[INFO] Setting up sudoers permissions for ${USER_NAME}..."

PERMISSION_CMD="${USER_NAME} ALL=(ALL) NOPASSWD: \
/usr/bin/systemctl restart convbot, \
/usr/bin/systemctl restart toeicbot, \
/usr/bin/systemctl enable convbot, \
/usr/bin/systemctl enable toeicbot, \
/usr/bin/systemctl daemon-reload, \
/usr/bin/cp /home/${USER_NAME}/${PROJECT_NAME}/scripts/convbot.service /etc/systemd/system/convbot.service, \
/usr/bin/cp /home/${USER_NAME}/${PROJECT_NAME}/scripts/toeicbot.service /etc/systemd/system/toeicbot.service"

echo "$PERMISSION_CMD" | sudo tee $SUDOERS_FILE > /dev/null

sudo chmod 0440 $SUDOERS_FILE

echo "[SUCCESS] Permissions set in $SUDOERS_FILE"
echo "[INFO] Now GitHub Actions can deploy without a password."
