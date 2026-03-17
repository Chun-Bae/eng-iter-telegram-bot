#!/bin/bash

# chmod +x scripts/setup_sudoers.sh && ./scripts/setup_sudoers.sh

USER_NAME="ubuntu"
PROJECT_NAME="eng-iter-telegram-bot"
SERVICE_NAME="studybot"
SUDOERS_FILE="/etc/sudoers.d/${SERVICE_NAME}_deploy"

echo "[INFO] Setting up sudoers permissions for ${USER_NAME}..."

# 서비스 재시작, 설정 리로드, 서비스 파일 복사에 대해 패스워드 없이 허용
PERMISSION_CMD="${USER_NAME} ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart ${SERVICE_NAME}, /usr/bin/systemctl daemon-reload, /usr/bin/cp /home/${USER_NAME}/${PROJECT_NAME}/scripts/${SERVICE_NAME}.service /etc/systemd/system/${SERVICE_NAME}.service"

# /etc/sudoers.d/ 에 파일 생성
echo "$PERMISSION_CMD" | sudo tee $SUDOERS_FILE > /dev/null

# 파일 권한
sudo chmod 0440 $SUDOERS_FILE

echo "[SUCCESS] Permissions set in $SUDOERS_FILE"
echo "[INFO] Now GitHub Actions can deploy without a password."