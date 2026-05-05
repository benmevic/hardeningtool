#!/bin/bash

# Global OS Detection Script
# Her işletim sistemi için DETECTED_OS değeri belirler

DETECTED_OS="unknown"

# /etc/os-release varsa oku
if [ -f /etc/os-release ]; then
    source /etc/os-release
    ID_LOWER=$(echo "$ID" | tr '[:upper:]' '[:lower:]')
    VERSION_ID="$VERSION_ID"
    
    # Metasploitable2 (Ubuntu 8.04 eski sürümü)
    if [[ "$ID_LOWER" == "ubuntu" && "$VERSION_ID" == "8.04" ]]; then
        DETECTED_OS="metasploitable2"
    # Ubuntu / Debian / Kali
    elif [[ "$ID_LOWER" == "ubuntu" || "$ID_LOWER" == "debian" || "$ID_LOWER" == "kali" ]]; then
        DETECTED_OS="ubuntu"
    # RHEL / CentOS
    elif [[ "$ID_LOWER" == "rhel" || "$ID_LOWER" == "centos" ]]; then
        DETECTED_OS="rhel_centos"
    # Fedora
    elif [[ "$ID_LOWER" == "fedora" ]]; then
        DETECTED_OS="fedora"
    # Arch Linux
    elif [[ "$ID_LOWER" == "arch" || "$ID_LOWER" == "archlinux" ]]; then
        DETECTED_OS="arch"
    fi
else
    # Fallback: /etc/issue'ye bak
    if [ -f /etc/issue ]; then
        issue=$(cat /etc/issue | head -1 | tr '[:upper:]' '[:lower:]')
        [[ "$issue" == *"ubuntu"* ]] && DETECTED_OS="ubuntu"
        [[ "$issue" == *"debian"* ]] && DETECTED_OS="ubuntu"
        [[ "$issue" == *"metasploitable"* ]] && DETECTED_OS="metasploitable2"
        [[ "$issue" == *"centos"* ]] && DETECTED_OS="rhel_centos"
        [[ "$issue" == *"fedora"* ]] && DETECTED_OS="fedora"
        [[ "$issue" == *"arch"* ]] && DETECTED_OS="arch"
    fi
fi

echo "DETECTED_OS=$DETECTED_OS"
