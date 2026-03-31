import { expect } from "chai";
import { ethers } from "hardhat";

describe("JudicialChainOfCustody", function () {
  it("anchors a hash and verifies it", async function () {
    const [owner, anchor] = await ethers.getSigners();
    const Factory = await ethers.getContractFactory("JudicialChainOfCustody");
    const contract = await Factory.deploy();
    await contract.waitForDeployment();

    await contract.authorizeAnchor(anchor.address);

    const caseId = ethers.keccak256(ethers.toUtf8Bytes("CASE-001"));
    const documentHash = ethers.keccak256(ethers.toUtf8Bytes("doc payload"));
    await contract.connect(anchor).anchorHash(caseId, documentHash);

    expect(await contract.verifyHash(caseId, documentHash)).to.equal(true);

    const record = await contract.getRecord(caseId);
    expect(record[0]).to.equal(documentHash);
    expect(record[2]).to.equal(anchor.address);
  });

  it("prevents duplicate anchors", async function () {
    const [owner] = await ethers.getSigners();
    const Factory = await ethers.getContractFactory("JudicialChainOfCustody");
    const contract = await Factory.deploy();
    await contract.waitForDeployment();

    const caseId = ethers.keccak256(ethers.toUtf8Bytes("CASE-002"));
    const documentHash = ethers.keccak256(ethers.toUtf8Bytes("doc payload 2"));

    await contract.anchorHash(caseId, documentHash);
    await expect(contract.anchorHash(caseId, documentHash)).to.be.reverted;
  });
});
