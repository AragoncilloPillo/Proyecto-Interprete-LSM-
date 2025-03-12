#Instalar Requerimientos 

import pkg_resources
import subprocess
import sys

required_packages = {
    #"gTTS": "2.5.1",
    #"keras": "2.10.0",
    #"mediapipe": "0.10.11",
    #"numpy": "1.26.4",
    #"opencv_contrib_python": "4.9.0.80",
    #"pandas": "2.2.2",
    #"pygame": "2.5.2",
    #"tensorflow": "2.10.1",
    #"Flask": "3.0.2",
    "protobuf": "3.20.3",
    "mediapipe": "0.10.8",
    #"tables": "3.9.2",
    #"PyQt5": "5.15.9",
    #"scikit-learn": "1.3.1"
}

def install_package(package_name, version):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", f"{package_name}=={version}", "--timeout", "300"])
        print(f"Se instaló {package_name}=={version}.")
    except subprocess.CalledProcessError as e:
        print(f"Error al instalar {package_name}=={version}. Error: {e}")
    except Exception as e:
        print(f"Ocurrió un error en {package_name}=={version}. Error: {e}")

installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}

for pkg, req_version in required_packages.items():
    installed_version = installed_packages.get(pkg, "No instalado")
    if installed_version == req_version:
        print(f"{pkg} esta pero requiere esta versión {req_version}.")
    else:
        if installed_version == "No instalado":
            print(f"{pkg} no instalado pero se instalara {req_version}.")
        else:
            print(f"{pkg} es {installed_version} (requiere {req_version})")
        install_package(pkg, req_version)