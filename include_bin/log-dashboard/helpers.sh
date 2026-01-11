#!/usr/bin/env bash

info() {
    echo "[INFO] $*"
}

warn() {
    echo "[WARN] $*"
}

die() {
    echo "[ERROR] $*"
    exit 1
}
