import {defineConfig} from "hardhat/config";
import hardhatToolboxMochaEthers from "@nomicfoundation/hardhat-toolbox-mocha-ethers";
import * as dotenv from "dotenv";

dotenv.config();

export default defineConfig({
    plugins: [hardhatToolboxMochaEthers],
    solidity: "0.8.24",
    networks: {
        localhost: {
            type: "http",
            url: "http://127.0.0.1:8545",
        },
        sepolia: {
            type: "http",
            chainId: 44787,
            url: process.env.SEPOLIA_RPC_URL || "https://eth-sepolia.g.alchemy.com/v2/EtE-B3sAJN4xZBwBuv0HU",
            accounts: process.env.SEPOLIA_PRIVATE_KEY ? [process.env.SEPOLIA_PRIVATE_KEY] : [],
        },
        celoSepolia: {
            type: "http",
            chainId: 11142220,
            url: process.env.CELO_SEPOLIA_RPC_URL || "https://celo-sepolia.g.alchemy.com/v2/lio1rlcUzCF1Q15gxCe8o",
            accounts: process.env.CELO_PRIVATE_KEY ? [process.env.CELO_PRIVATE_KEY] : [],
        }
    },
});
