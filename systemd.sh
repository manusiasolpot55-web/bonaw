#!/bin/bash

SERVICE_NAME=$(basename "$(pwd)")
REPO_DIR="$(pwd)"
VENV_DIR="$REPO_DIR/venv"
ENV_FILE="$REPO_DIR/.env"

echo "📦 Mengecek dependensi sistem (unzip)..."
if ! command -v unzip &> /dev/null; then
    echo "⚠️ Unzip tidak ditemukan. Menginstall unzip..."
    sudo apt-get update && sudo apt-get install unzip -y
    echo "✅ Unzip berhasil diinstall."
else
    echo "✅ Unzip sudah ada."
fi

echo "🦕 Mengecek JS Runtime (Deno)..."
if ! command -v deno &> /dev/null; then
    echo "⚠️ Deno tidak ditemukan. Memulai instalasi..."
    
    curl -fsSL https://deno.land/install.sh | sh
    
    if [ -f "$HOME/.deno/bin/deno" ]; then
        sudo cp "$HOME/.deno/bin/deno" /usr/local/bin/
        echo "✅ Deno berhasil diinstal ke /usr/local/bin/deno"
    else
        echo "❌ Gagal menginstal Deno. Pastikan curl dan unzip tersedia."
        exit 1
    fi
else
    echo "✅ Deno sudah terinstal di: $(which deno)"
fi
# --------------------------------------

echo "📦 Menyiapkan virtual environment untuk $SERVICE_NAME..."

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "✅ Virtual environment dibuat."
else
    echo "ℹ️ Virtual environment sudah ada."
fi

source "$VENV_DIR/bin/activate"
pip install --upgrade pip
if [ -f "$REPO_DIR/requirements.txt" ]; then
    pip install -r "$REPO_DIR/requirements.txt"
else
    echo "⚠️ requirements.txt tidak ditemukan, melewati instalasi pip."
fi

echo "🔧 Membuat systemd service untuk $SERVICE_NAME..."

if [ -f "$ENV_FILE" ]; then
    ENV_LINE="EnvironmentFile=$ENV_FILE"
    echo "📄 File .env ditemukan, akan dimuat oleh systemd."
else
    ENV_LINE=""
    echo "⚠️ File .env tidak ditemukan, bagian EnvironmentFile dilewati."
fi

CURRENT_PATH=$PATH

sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=Ubot $SERVICE_NAME
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$REPO_DIR
$ENV_LINE

Environment="PATH=$VENV_DIR/bin:$CURRENT_PATH:/usr/local/bin"
Environment=PYTHONUNBUFFERED=1
ExecStart=/bin/bash -c 'source $VENV_DIR/bin/activate && bash start.sh'
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "🔄 Reload systemd dan mengaktifkan service $SERVICE_NAME..."

sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

echo "✅ Service '$SERVICE_NAME' berhasil dibuat dan dijalankan!"
sudo systemctl status $SERVICE_NAME --no-pager
