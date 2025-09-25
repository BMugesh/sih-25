"""
Simulation module for microgrid energy transfers.
"""
import random
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
from database import Database
from controller import MicrogridController

class MicrogridSimulation:
    """Simulation handler for microgrid energy transfers."""
    
    def __init__(self):
        """Initialize simulation with database and controller."""
        self.db = Database()
        self.controller = MicrogridController(self.db)
        
    def create_user(self, name: str, initial_energy: float = 100.0,
                   initial_credits: float = 100.0) -> Optional[Dict[str, Any]]:
        """Create a new user with initial balances."""
        max_attempts = 5
        last_error = None
        
        for attempt in range(max_attempts):
            try:
                # Add random 6-digit suffix and attempt number to ensure uniqueness
                random_suffix = str(random.randint(100000, 999999))
                timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
                user_id = f"USER_{timestamp}_{random_suffix}_{attempt}"
                
                user = self.db.create_user(
                    user_id=user_id,
                    name=name,
                    energy_balance=initial_energy,
                    credit_balance=initial_credits
                )
                return user
            except Exception as e:
                last_error = str(e)
                if attempt == max_attempts - 1:
                    print(f"Failed to create user after {max_attempts} attempts: {last_error}")
                    return None

    def request_energy(self, sender_id: str, receiver_id: str,
                      amount: float) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Request energy transfer between users."""
        return self.controller.process_transfer(sender_id, receiver_id, amount)

    def get_user_balance(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's current balance."""
        return self.db.get_user(user_id)

    def get_all_transactions(self) -> List[Dict[str, Any]]:
        """Get all recorded transactions."""
        return self.db.get_all_transactions()

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users in the system."""
        return self.db.get_all_users()
    
    def clear_all_users(self) -> None:
        """Clear all users from the system except the microgrid."""
        self.db.clear_all_users()

    def simulate_random_transfers(self, num_transfers: int = 5) -> List[Dict[str, Any]]:
        """
        Simulate random energy transfers between users.
        
        Args:
            num_transfers: Number of random transfers to simulate
            
        Returns:
            List of completed transactions
        """
        users = self.get_all_users()
        if len(users) < 2:
            return []
        
        completed_transfers = []
        for _ in range(num_transfers):
            # Select random sender and receiver
            sender = random.choice(users)
            receiver = random.choice([u for u in users if u['user_id'] != sender['user_id']])
            
            # Random amount between 1 and sender's balance (or 10 if microgrid)
            max_amount = 10 if sender['user_id'] == self.controller.MICROGRID_ID else sender['energy_balance']
            amount = round(random.uniform(1, max(1, max_amount)), 2)
            
            # Process transfer
            success, message, transaction = self.request_energy(
                sender['user_id'],
                receiver['user_id'],
                amount
            )
            
            if success and transaction:
                completed_transfers.append(transaction)
            
        return completed_transfers
        
        return completed_transfers

    def get_summary_statistics(self) -> Dict:
        """Get system summary statistics."""
        stats = self.db.get_summary_statistics()
        
        # Add most active users
        transactions = self.get_all_transactions()
        user_activity = {}
        
        for tx in transactions:
            user_activity[tx['sender_id']] = user_activity.get(tx['sender_id'], 0) + 1
            user_activity[tx['receiver_id']] = user_activity.get(tx['receiver_id'], 0) + 1
        
        if user_activity:
            most_active = max(user_activity.items(), key=lambda x: x[1])
            stats['most_active_user'] = {
                'user_id': most_active[0],
                'transaction_count': most_active[1]
            }
        
        return stats