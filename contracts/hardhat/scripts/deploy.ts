import { network } from "hardhat";
import * as fs from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

async function main() {
  const { ethers } = await network.connect();

  const contract = await ethers.deployContract("JudicialChainOfCustody");
  await contract.waitForDeployment();

  const address = await contract.getAddress();
  const deployed = {
    network: process.env.HARDHAT_NETWORK || "unknown",
    contract: "JudicialChainOfCustody",
    address,
  };

  const __filename = fileURLToPath(import.meta.url);
  const __dirname = path.dirname(__filename);

  const outDir = path.resolve(__dirname, "../deployed");
  fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(
    path.join(outDir, "JudicialChainOfCustody.json"),
    JSON.stringify(deployed, null, 2)
  );

  console.log("JudicialChainOfCustody deployed to:", address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});