# syntax=docker/dockerfile:1.7
FROM ubuntu:22.04 AS builder
ENV DEBIAN_FRONTEND=noninteractive \
    CARGO_HOME=/opt/cargo \
    RUSTUP_HOME=/opt/rustup \
    PATH=/opt/cargo/bin:/usr/local/bin:/usr/bin:/bin
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl wget file ca-certificates pkg-config \
    libwebkit2gtk-4.1-dev libssl-dev libayatana-appindicator3-dev \
    librsvg2-dev librsvg2-bin libxdo-dev patchelf libgtk-3-dev libfuse2 \
    && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get update && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain 1.86.0
WORKDIR /workspace
COPY package.json ./
RUN npm install --no-audit --no-fund
COPY . .
RUN mkdir -p src-tauri/icons \
    && rsvg-convert -w 512 -h 512 src-tauri/icons/icon.svg -o src-tauri/icons/icon.png \
    && npm run tauri:build
FROM scratch AS artifact
COPY --from=builder /workspace/src-tauri/target/release/bundle/appimage/*.AppImage /
