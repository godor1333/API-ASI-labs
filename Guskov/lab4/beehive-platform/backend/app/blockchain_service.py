from web3 import Web3
from .database import get_web3
import json

class BlockchainService:
    def __init__(self):
        self.w3 = get_web3()
        self.check_connection()
    
    def check_connection(self):
        if self.w3.is_connected():
            print("✅ Connected to blockchain")
            print(f"📦 Latest block: {self.w3.eth.block_number}")
        else:
            print("❌ Failed to connect to blockchain")
    
    def get_accounts(self):
        """Get available accounts from the blockchain"""
        return self.w3.eth.accounts
    
    def get_balance(self, address):
        """Get balance of an address"""
        balance = self.w3.eth.get_balance(address)
        return self.w3.from_wei(balance, 'ether')
    
    def create_test_transaction(self, from_address, to_address, amount_eth):
        """Create a test transaction"""
        try:
            transaction = {
                'from': from_address,
                'to': to_address,
                'value': self.w3.to_wei(amount_eth, 'ether'),
                'gas': 21000,
                'gasPrice': self.w3.to_wei('50', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(from_address)
            }
            
            # Note: In real implementation, you'd sign and send the transaction
            # For demo, we just return the transaction object
            return transaction
        except Exception as e:
            print(f"Error creating transaction: {e}")
            return None

# Singleton instance
blockchain_service = BlockchainService()