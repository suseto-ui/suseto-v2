#!/bin/bash
set -e
cd suseto-v2

# 1. services/aidc_core.py — opravit SVGWritery -> SVGWriter + smazat duplikátní import
python3 -c "
import re
with open('services/aidc_core.py', 'r') as f:
    content = f.read()
# Fix typo
content = content.replace('SVGWritery', 'SVGWriter')
# Remove any duplicate 'from services.config import CONFIG' lines (keep first)
lines = content.split('\n')
seen_config = False
new_lines = []
for line in lines:
    if line.strip() == 'from services.config import CONFIG':
        if seen_config:
            continue  # skip duplicate
        seen_config = True
    new_lines.append(line)
with open('services/aidc_core.py', 'w') as f:
    f.write('\n'.join(new_lines))
print('aidc_core.py: OK')
"

# 2. routes/admin_routes.py — E401: import csv, io -> 2 řádky
sed -i 's/^import csv, io$/import csv\nimport io/' routes/admin_routes.py
echo "admin_routes.py: OK"

# 3. routes/timeline_routes.py — E401 + E722
sed -i 's/^import csv, io, datetime$/import csv\nimport io\nimport datetime/' routes/timeline_routes.py
sed -i 's/^        except:$/        except Exception:/' routes/timeline_routes.py
echo "timeline_routes.py: OK"

# 4. routes/core_routes.py — E302: prázdné řádky před funkcemi
python3 -c "
import re
with open('routes/core_routes.py', 'r') as f:
    content = f.read()
# Ensure 2 blank lines before each @... or def at module level
content = re.sub(r'\n(@\S)', r'\n\n\n\1', content)
content = re.sub(r'\n\n\n\n+(@)', r'\n\n\n\1', content)
with open('routes/core_routes.py', 'w') as f:
    f.write(content)
print('core_routes.py: OK')
"

# 5. services/workbench_modules.py — E401
python3 -c "
with open('services/workbench_modules.py', 'r') as f:
    content = f.read()
content = content.replace('import re, math, base64, json, csv, io', 'import re\nimport math\nimport base64\nimport json\nimport csv\nimport io')
with open('services/workbench_modules.py', 'w') as f:
    f.write(content)
print('workbench_modules.py: OK')
"

# 6. services/decode_service.py — E401
python3 -c "
with open('services/decode_service.py', 'r') as f:
    content = f.read()
content = content.replace('import base64, binascii, re, urllib.parse, math, logging', 'import base64\nimport binascii\nimport re\nimport urllib.parse\nimport math\nimport logging')
with open('services/decode_service.py', 'w') as f:
    f.write(content)
print('decode_service.py: OK')
"

# Commit
git add services/aidc_core.py routes/admin_routes.py routes/timeline_routes.py routes/core_routes.py services/workbench_modules.py services/decode_service.py
git commit -m "fix(lint): E401 multi-imports, E722 bare except, E302 blank lines, aidc_core typo [S105]"
git push origin main
echo ""
echo "=== HOTOVO ==="
