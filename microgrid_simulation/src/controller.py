"""
MicrogridController module for managing energy transfers.
"""
import uuid
from typing import Dict, Optional, Tuple
from database import Database

class MicrogridController:
    """Controller for managing microgrid energy transfers."""
    
    def __init__(self, db: Database):
        """Initialize controller with database connection."""
        self.db = db
        self.MICROGRID_ID = "GRID_001"
        
        # Ensure microgrid exists
        if not self.db.get_user(self.MICROGRID_ID):
            self.db.create_user(
                self.MICROGRID_ID,
                "Central Microgrid",
                energy_balance=1000.0,  # Initial energy pool
                credit_balance=0.0
            )
    
    def validate_transfer(self, sender_id: str, receiver_id: str, 
                         amount: float) -> Tuple[bool, str]:
        """
        Validate a transfer request.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if amount <= 0:
            return False, "Transfer amount must be positive"
        
        if sender_id == receiver_id:
            return False, "Sender and receiver cannot be the same"
        
        sender = self.db.get_user(sender_id)
        if not sender:
            return False, f"Sender {sender_id} not found"
        
        receiver = self.db.get_user(receiver_id)
        if not receiver:
            return False, f"Receiver {receiver_id} not found"
        
        if sender['energy_balance'] < amount and sender_id != self.MICROGRID_ID:
            return False, "Insufficient energy balance"
        
        return True, "Transfer validation successful"
    
    def process_transfer(self, sender_id: str, receiver_id: str, 
                        amount: float) -> Tuple[bool, str, Optional[Dict]]:
        """
        Process an energy transfer between users.
        
        Returns:
            Tuple of (success: bool, message: str, transaction: Optional[Dict])
        """
        # Validate transfer
        valid, message = self.validate_transfer(sender_id, receiver_id, amount)
        if not valid:
            return False, message, None
        
        try:
            # Generate transaction ID
            tx_id = str(uuid.uuid4())
            
            # Update balances
            if not self.db.update_user_balance(sender_id, energy_delta=-amount):
                return False, "Failed to update sender balance", None
            
            if not self.db.update_user_balance(receiver_id, energy_delta=amount):
                # Rollback sender update
                self.db.update_user_balance(sender_id, energy_delta=amount)
                return False, "Failed to update receiver balance", None
            
            # Log transaction
            transaction = self.db.log_transaction(tx_id, sender_id, receiver_id, amount)
            
            return True, "Transfer completed successfully", transaction
            
        except Exception as e:
            # Attempt rollback if partial updates occurred
            try:
                self.db.update_user_balance(sender_id, energy_delta=amount)
                self.db.update_user_balance(receiver_id, energy_delta=-amount)
            except:
                pass
            return False, f"Transfer failed: {str(e)}", None
    
    def get_system_state(self) -> Dict:
        """Get current state of the microgrid system."""
        return {
            'users': self.db.get_all_users(),
            'transactions': self.db.get_all_transactions(),
            'statistics': self.db.get_summary_statistics()
        }