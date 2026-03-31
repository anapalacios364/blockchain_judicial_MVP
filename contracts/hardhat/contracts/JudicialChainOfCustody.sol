// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract JudicialChainOfCustody {
    address public owner;

    struct Record {
        bytes32 documentHash;
        uint256 timestamp;
        address anchoredBy;
        bool exists;
    }

    mapping(bytes32 => Record) private records;
    mapping(address => bool) public authorizedAnchors;

    event HashAnchored(
        bytes32 indexed caseId,
        bytes32 indexed documentHash,
        address indexed anchoredBy,
        uint256 timestamp
    );
    event AnchorAuthorized(address indexed anchor);
    event AnchorRevoked(address indexed anchor);
    event OwnershipTransferred(address indexed oldOwner, address indexed newOwner);

    error NotOwner();
    error NotAuthorized();
    error AlreadyAnchored();
    error InvalidAddress();
    error RecordNotFound();

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    modifier onlyAuthorized() {
        if (!(authorizedAnchors[msg.sender] || msg.sender == owner)) revert NotAuthorized();
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function transferOwnership(address newOwner) external onlyOwner {
        if (newOwner == address(0)) revert InvalidAddress();
        address oldOwner = owner;
        owner = newOwner;
        emit OwnershipTransferred(oldOwner, newOwner);
    }

    function authorizeAnchor(address anchor) external onlyOwner {
        if (anchor == address(0)) revert InvalidAddress();
        authorizedAnchors[anchor] = true;
        emit AnchorAuthorized(anchor);
    }

    function revokeAnchor(address anchor) external onlyOwner {
        authorizedAnchors[anchor] = false;
        emit AnchorRevoked(anchor);
    }

    function anchorHash(bytes32 caseId, bytes32 documentHash) external onlyAuthorized {
        if (records[caseId].exists) revert AlreadyAnchored();

        records[caseId] = Record({
            documentHash: documentHash,
            timestamp: block.timestamp,
            anchoredBy: msg.sender,
            exists: true
        });

        emit HashAnchored(caseId, documentHash, msg.sender, block.timestamp);
    }

    function verifyHash(bytes32 caseId, bytes32 documentHash) external view returns (bool) {
        return records[caseId].exists && records[caseId].documentHash == documentHash;
    }

    function getRecord(bytes32 caseId)
        external
        view
        returns (bytes32 documentHash, uint256 timestamp, address anchoredBy, bool exists)
    {
        Record memory r = records[caseId];
        if (!r.exists) revert RecordNotFound();
        return (r.documentHash, r.timestamp, r.anchoredBy, r.exists);
    }
}
