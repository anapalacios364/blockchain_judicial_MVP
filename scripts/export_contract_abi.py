import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
artifact = root / "contracts" / "hardhat" / "artifacts" / "contracts" / "JudicialChainOfCustody.sol" / "JudicialChainOfCustody.json"

if not artifact.exists():
    raise SystemExit(f"No se encontró artifact en: {artifact}")

content = json.loads(artifact.read_text(encoding="utf-8"))
abi = json.dumps(content["abi"], ensure_ascii=False)
out = root / "contracts" / "hardhat" / "deployed" / "abi.min.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(abi, encoding="utf-8")
print(out)
