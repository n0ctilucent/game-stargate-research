# Lab Monorepo - GEMINI.md

This repository is a comprehensive monorepo for managing a personal or development lab infrastructure. It utilizes a mix of infrastructure-as-code (IaC) tools and a GNU-style build system.

## 🛠 Core Technologies

- **Ansible:** The primary configuration management tool. It manages various operating systems including Debian, Ubuntu, OpenBSD, and Raspberry Pi OS. 
    - **Testing:** Uses [Molecule](https://molecule.readthedocs.io/) for testing Ansible roles.
- **Terraform:** Used for infrastructure provisioning on **Google Cloud (GCP)** and **Digital Ocean**.
- **Docker & Podman:** Orchestrates various containerized services:
    - Kerberos (KDC) and SSH-enabled KDC servers.
    - Jupyter notebooks.
    - Golang development environments.
    - Website hosting.
- **Autotools (autoconf, automake):** An unusual but powerful choice for an IaC repo, used to:
    - Check for system dependencies (Python, Ansible, Podman, etc.).
    - Manage environment-specific configurations.
    - Automate the setup of Ansible configurations.

## 🚀 Key Workflows

### 1. Bootstrapping
The `bootstrap.sh` script is the entry point for new environments. It:
- Detects the OS and hardware (e.g., Raspberry Pi).
- Installs necessary system packages (`apt`, `brew`, `dnf`, `pkg_add`).
- Initializes the Autotools build system (`aclocal`, `autoreconf`, `automake`).
- Runs `./configure` to generate Makefiles.

### 2. Configuration & Build
Standard GNU workflow:
```bash
./bootstrap.sh
./configure
make
```

### 3. Ansible Management
The `ansible/` directory contains its own `Makefile.am` which handles:
- Creating `/etc/ansible`.
- Symlinking roles and group variables.
- Copying `ansible.cfg` and `hosts` to system paths.

### 4. Testing & Security
- `make test`: Sets up a Python virtual environment and runs Molecule tests.
- `make security`: Runs security scans and checks.

## 📌 Notable Features
- **Multi-OS Support:** Tailored installation and configuration for Linux, OpenBSD, and macOS.
- **Hardware Awareness:** Specific logic for Raspberry Pi and Nvidia-based nodes.
- **Environment Management:** Uses `direnv` (`.envrc`) for seamless environment variable loading.
- **Kerberos Integration:** Experimental support for Kerberos tickets for authentication.

## 📁 Directory Structure
- `ansible/`: Playbooks, roles, and inventory.
- `container/`: Dockerfiles and compose files for various services.
- `terraform/`: Cloud infrastructure definitions.
- `docs/`: Documentation in LaTeX and Markdown.
- `test/`: Scripts for testing the cluster and collections.
