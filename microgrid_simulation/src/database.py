"""
Database connection and operations module.
"""
import os
from typing import Dict, List, Optional
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Database:
    """Database connection and operations handler."""
    
    def __init__(self):
        """Initialize database connection."""
        # Use environment variable for connection string if available, else use default local
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        self.client = MongoClient(mongodb_uri)
        self.db = self.client.microgrid
        
        # Create indexes
        self.db.users.create_index('user_id', unique=True)
        self.db.transactions.create_index('tx_id', unique=True)
    
    def create_user(self, user_id: str, name: str, 
                   energy_balance: float = 0.0, 
                   credit_balance: float = 0.0) -> Dict:
        """Create a new user in the database."""
        user = {
            'user_id': user_id,
            'name': name,
            'energy_balance': energy_balance,
            'credit_balance': credit_balance
        }
        self.db.users.insert_one(user)
        return user
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Retrieve user by ID."""
        return self.db.users.find_one({'user_id': user_id}, {'_id': 0})
    
    def clear_all_users(self):
        """Remove all users except the microgrid (GRID_001)."""
        self.db.users.delete_many({'user_id': {'$ne': 'GRID_001'}})
    
    def update_user_balance(self, user_id: str, 
                          energy_delta: float = 0.0, 
                          credit_delta: float = 0.0) -> bool:
        """Update user's energy and credit balance."""
        result = self.db.users.update_one(
            {'user_id': user_id},
            {'$inc': {
                'energy_balance': energy_delta,
                'credit_balance': credit_delta
            }}
        )
        return result.modified_count > 0
    
    def log_transaction(self, tx_id: str, sender_id: str, 
                       receiver_id: str, amount: float) -> Dict:
        """Log a new transaction."""
        transaction = {
            'tx_id': tx_id,
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'amount': amount,
            'timestamp': datetime.utcnow()
        }
        self.db.transactions.insert_one(transaction)
        return transaction
    
    def get_all_users(self) -> List[Dict]:
        """Retrieve all users."""
        return list(self.db.users.find({}, {'_id': 0}))
    
    def get_all_transactions(self) -> List[Dict]:
        """Retrieve all transactions."""
        return list(self.db.transactions.find({}, {'_id': 0}))
    
    def get_user_transactions(self, user_id: str) -> List[Dict]:
        """Retrieve all transactions for a specific user."""
        return list(self.db.transactions.find(
            {'$or': [
                {'sender_id': user_id},
                {'receiver_id': user_id}
            ]},
            {'_id': 0}
        ))
    
    def get_summary_statistics(self) -> Dict:
        """Get system-wide summary statistics."""
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'total_energy': {'$sum': '$energy_balance'},
                    'total_credits': {'$sum': '$credit_balance'},
                    'user_count': {'$sum': 1}
                }
            }
        ]
        stats = list(self.db.users.aggregate(pipeline))
        return stats[0] if stats else {}