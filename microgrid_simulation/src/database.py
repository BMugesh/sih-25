"""
In-memory database implementation using Python dictionaries.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import uuid

class Database:
    """In-memory database handler using dictionaries."""
    
    def __init__(self):
        """Initialize in-memory storage."""
        self._users: Dict[str, Dict[str, Any]] = {}
        self._transactions: Dict[str, Dict[str, Any]] = {}
        
        # Create indexes (not needed for in-memory but kept for API compatibility)
        self.create_index('user_id')
        self.create_index('tx_id')
    
    def create_index(self, field_name: str) -> None:
        """Simulate index creation (not needed for in-memory but kept for compatibility)."""
        pass
    
    def create_user(self, user_id: str, name: str, 
                   energy_balance: float = 0.0, 
                   credit_balance: float = 0.0) -> Dict[str, Any]:
        """Create a new user in the in-memory store."""
        if user_id in self._users:
            raise ValueError(f"Duplicate user_id: {user_id}")
            
        user = {
            'user_id': user_id,
            'name': name,
            'energy_balance': energy_balance,
            'credit_balance': credit_balance
        }
        self._users[user_id] = user
        return user
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user by ID."""
        return self._users.get(user_id)
    
    def clear_all_users(self) -> None:
        """Remove all users except the microgrid (GRID_001)."""
        grid_user = self._users.get('GRID_001')
        self._users.clear()
        if grid_user:
            self._users['GRID_001'] = grid_user
    
    def update_user_balance(self, user_id: str, 
                          energy_delta: float = 0.0, 
                          credit_delta: float = 0.0) -> bool:
        """Update user's energy and credit balance."""
        if user_id not in self._users:
            return False
            
        user = self._users[user_id]
        user['energy_balance'] += energy_delta
        user['credit_balance'] += credit_delta
        return True
    
    def log_transaction(self, tx_id: str, sender_id: str, 
                       receiver_id: str, amount: float) -> Dict[str, Any]:
        """Log a new transaction."""
        transaction = {
            'tx_id': tx_id,
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'amount': amount,
            'timestamp': datetime.now(timezone.utc)
        }
        self._transactions[tx_id] = transaction
        return transaction
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Retrieve all users."""
        return list(self._users.values())
    
    def get_all_transactions(self) -> List[Dict[str, Any]]:
        """Retrieve all transactions."""
        return list(self._transactions.values())
    
    def get_user_transactions(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve all transactions for a specific user."""
        return [
            tx for tx in self._transactions.values()
            if tx['sender_id'] == user_id or tx['receiver_id'] == user_id
        ]
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get system-wide summary statistics."""
        total_energy = sum(user['energy_balance'] for user in self._users.values())
        total_credits = sum(user['credit_balance'] for user in self._users.values())
        user_count = len(self._users)
        
        return {
            'total_energy': total_energy,
            'total_credits': total_credits,
            'user_count': user_count
        }
