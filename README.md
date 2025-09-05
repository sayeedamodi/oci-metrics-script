
# OCI Metrics Script

A Python script to fetch Oracle Cloud Infrastructure (OCI) compute instance metrics using the **OCI Python SDK**. While OCI CLI can be used, this script automates metric collection and outputs both JSON and Excel reports.

---

## 1. Prerequisites

### 1.1 OCI Configuration

Create a folder for OCI configuration:

| OS | Path |
|----|------|
| Linux/macOS | `~/.oci/` |
| Windows | `C:\Users\<username>\.oci\` |

Create a `config` file inside this folder. Example:

```ini
[DEFAULT]
user=ocid1.user.oc1..aaaaaaaaexample
fingerprint=20:3b:97:13:55:1c:aa:bb:cc:dd:ee:ff:gg:hh:ii
key_file=/home/username/.oci/oci_api_key.pem
tenancy=ocid1.tenancy.oc1..aaaaaaaaexample
region=ap-mumbai-1 

[JEDDAH]
user=ocid1.user.oc1..aaaaaaaaexample   
fingerprint=20:3b:97:13:55:1c:aa:bb:cc:dd:ee:ff:gg:hh:ii 
key_file=/home/username/.oci/oci_api_key.pem
tenancy=ocid1.tenancy.oc1..aaaaaaaaexample
region=m-jeddah-1 
````

Set correct permissions for the private key:

```bash
chmod 600 ~/.oci/oci_api_key.pem
```

---

### 1.2 Get User OCID and Fingerprint

1. **Get your User OCID** from the OCI console and paste it in the `user` field:

![User OCID Screenshot](https://github.com/user-attachments/assets/d8a10bb6-2fd9-4f11-9d31-d164c77c1562)

2. **Get API Key Fingerprint**:

* Select your profile → Go to **User Settings → API Keys**
* Add an API key → Generate API Key → Download the private key and keep it safe

![API Key Screenshot](https://github.com/user-attachments/assets/76fbd73c-878a-4e51-a6ea-fa390de0265a)

3. Copy the fingerprint and all details into your `config` file. For multiple regions, add a new section after `[DEFAULT]` and ensure the `key_file` path is correct.

---

### 1.3 Python & OCI SDK

#### Check Python

```bash
python --version
```

#### Install Python (if needed)

1. Download latest Python 3.x from [Python Downloads](https://www.python.org/downloads/)
2. During installation:

   * Check **Add Python to PATH**
   * Choose **Install Now**

#### Install OCI SDK

```bash
pip install oci
```

Verify installation:

```bash
python -c "import oci; print(oci.__version__)"
```

---

## 2. Setup

1. Clone the repository or download `oci_metrics.py`.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

`requirements.txt` contains:

```
oci
```

3. Create a file `all_jeddah_instances.txt` with the OCIDs of target instances (one per line).

---

## 3. Features

| Feature    | Description                                          |
| ---------- | ---------------------------------------------------- |
| Output     | JSON and Excel (.xlsx)                               |
| Profiles   | Supports multiple OCI profiles                       |
| Accuracy   | Handles Compute Instance Monitoring states correctly |
| Timestamps | UTC timestamps consistent with OCI Console           |

---

## 4. Usage

Run the script for Jeddah region:

```bash
python3 oci_metrics.py -c JEDDAH -i all_jeddah_instances.txt -o output.json -x output.xlsx
```

Windows:

```cmd
python oci_metrics.py -c JEDDAH -i all_jeddah_instances.txt -o output.json -x output.xlsx
```

The script generates `output.json` and `output.xlsx` in the current directory.

---

## 5. Notes

* Ensure the private key exists and permissions are set correctly.
* For multiple regions, duplicate the `[REGION_NAME]` section in the config file.
* Keep your private keys secure at all times.


