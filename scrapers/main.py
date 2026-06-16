import subprocess
import sys

scripts = ["didi.py", "rappi.py", "uber_eats.py"]

for script in scripts:
    print(f"\n🚀 Corriendo {script}...")
    subprocess.run([sys.executable, script])
    print(f"✅ {script} terminado")

print("\n🎉 Todos los scripts terminados")