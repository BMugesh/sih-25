"""
Streamlit frontend for the Microgrid Controller Credit Transfer Simulation.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from simulation import MicrogridSimulation

# Page config must be the first Streamlit command
st.set_page_config(
    page_title="Microgrid Controller Credit Transfer Simulation", 
    page_icon="⚡", 
    layout="wide"
)

# Initialize simulation
def get_simulation():
    """Get or create simulation instance."""
    sim = MicrogridSimulation()
    
    # First, clear all existing users to ensure a clean state
    sim.clear_all_users()
    
    # Create default users
    users = sim.get_all_users()
    if len(users) <= 1:  # Only grid user exists or no users exist
        # Create default houses with some initial energy and credits
        default_users = [
            # Residential users
            ("HouseA", 150.0, 100.0),
            ("HouseB", 120.0, 100.0),
            ("HouseC", 180.0, 100.0),
            ("HouseD", 200.0, 150.0),
            ("HouseE", 160.0, 120.0),
            # Commercial users
            ("Shop1", 300.0, 250.0),
            ("Shop2", 280.0, 200.0),
            ("Office1", 400.0, 300.0),
            # Industrial users
            ("Factory1", 800.0, 600.0),
            ("Factory2", 1000.0, 800.0),
            # Green energy producers
            ("SolarFarm1", 1500.0, 1000.0),
            ("WindMill1", 1200.0, 900.0)
        ]
        
        for name, energy, credits in default_users:
            sim.create_user(name, energy, credits)
        
        st.success("Created default users including residential, commercial, industrial, and green energy producers")
    
    return sim

sim = get_simulation()

# Add custom CSS
st.markdown("""
<style>
.transfer-card {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.energy-stats {
    background-color: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    margin: 10px 0;
    border: 1px solid #e9ecef;
}
.section-title {
    color: #1a1a1a;
    font-size: 1.2em;
    font-weight: 600;
    margin-bottom: 15px;
}
.balance-text {
    color: #2c3e50;
    font-size: 1.1em;
    font-weight: 500;
    margin: 5px 0;
}
.recent-transfer-item {
    background-color: #ffffff;
    padding: 12px;
    margin: 8px 0;
    border-radius: 6px;
    border: 1px solid #e9ecef;
    color: #2c3e50;
}
.transfer-amount {
    color: #2ecc71;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# Title
st.title("⚡ Microgrid Controller Credit Transfer Simulation")

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["User Dashboard", "Transfer Credits", "Transaction Log", "Run Simulation", "Summary Statistics"]
)

# User Dashboard
if page == "User Dashboard":
    st.header("User Dashboard")
    
    # Create New User
    with st.expander("Create New User"):
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("Name")
        with col2:
            initial_energy = st.number_input("Initial Energy Balance", value=100.0, min_value=0.0)
        with col3:
            initial_credits = st.number_input("Initial Credit Balance", value=100.0, min_value=0.0)
        
        if st.button("Create User"):
            if name:
                user = sim.create_user(name, initial_energy, initial_credits)
                if user:
                    st.success(f"Created user {user['name']} with ID {user['user_id']}")
                else:
                    st.error("Failed to create user")
            else:
                st.warning("Please enter a name")
    
    # Reset Users Button
    if st.button("Reset All Users"):
        # Clear database and recreate users
        sim.clear_all_users()
        st.rerun()
        
    # Display Users Table
    st.subheader("Current Users")
    users = sim.get_all_users()
    if users:
        df = pd.DataFrame(users)
        st.dataframe(
            df.style.format({
                'energy_balance': '{:.2f}',
                'credit_balance': '{:.2f}'
            }),
            use_container_width=True
        )
    else:
        st.info("No users found in the system")

# Transfer Credits
elif page == "Transfer Credits":
    st.markdown("## 🔄 Smart Energy Transfer System")
    
    users = sim.get_all_users()
    if len(users) < 2:
        st.warning("Need at least 2 users to perform transfers")
    else:
        # Create two main sections
        transfer_col, info_col = st.columns([2, 1])
        
        with transfer_col:
            with st.container():
                st.markdown('<div class="transfer-card">', unsafe_allow_html=True)
                st.subheader("🏠 Transfer Details")
                
                # Select sender with current balance display
                sender_id = st.selectbox(
                    "From (Sender)",
                    options=[u['user_id'] for u in users],
                    format_func=lambda x: f"{next(u['name'] for u in users if u['user_id'] == x)} ({x})"
                )
                sender = next(u for u in users if u['user_id'] == sender_id)
                
                st.write(f"💡 Available Energy: {sender['energy_balance']:.2f} units")
                st.write(f"💰 Credit Balance: {sender['credit_balance']:.2f} units")
                
                # Select receiver with current balance display
                receiver_options = [u['user_id'] for u in users if u['user_id'] != sender_id]
                receiver_id = st.selectbox(
                    "To (Receiver)",
                    options=receiver_options,
                    format_func=lambda x: f"{next(u['name'] for u in users if u['user_id'] == x)} ({x})"
                )
                receiver = next(u for u in users if u['user_id'] == receiver_id)
                
                st.write(f"💡 Current Energy: {receiver['energy_balance']:.2f} units")
                st.write(f"💰 Credit Balance: {receiver['credit_balance']:.2f} units")
                
                # Amount selection with slider and precise input
                st.subheader("🔋 Energy Amount")
                max_amount = sender['energy_balance'] if sender_id != sim.controller.MICROGRID_ID else 1000.0
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    amount = st.slider(
                        "Select amount",
                        min_value=0.0,
                        max_value=float(max_amount),
                        value=min(1.0, max_amount),
                        step=0.1
                    )
                
                with col2:
                    amount = st.number_input(
                        "Precise amount",
                        min_value=0.1,
                        max_value=float(max_amount),
                        value=amount,
                        step=0.1
                    )
                
                # Transfer button with confirmation
                if st.button("🚀 Initiate Transfer", use_container_width=True):
                    with st.spinner("Processing transfer..."):
                        success, message, transaction = sim.request_energy(sender_id, receiver_id, amount)
                        if success:
                            st.balloons()
                            st.success(f"Transfer successful! Transaction ID: {transaction['tx_id']}")
                            
                            # Show updated balances
                            st.markdown("### Updated Balances")
                            col1, col2 = st.columns(2)
                            
                            # Get updated user data
                            updated_sender = sim.get_user_balance(sender_id)
                            updated_receiver = sim.get_user_balance(receiver_id)
                            
                            with col1:
                                st.markdown(f"""
                                **Sender ({updated_sender['name']}):**
                                - Energy: {updated_sender['energy_balance']:.2f} units
                                - Credits: {updated_sender['credit_balance']:.2f} units
                                """)
                            
                            with col2:
                                st.markdown(f"""
                                **Receiver ({updated_receiver['name']}):**
                                - Energy: {updated_receiver['energy_balance']:.2f} units
                                - Credits: {updated_receiver['credit_balance']:.2f} units
                                """)
                        else:
                            st.error(f"❌ Transfer failed: {message}")
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Information and History Panel
        with info_col:
            st.markdown('<div class="transfer-card">', unsafe_allow_html=True)
            st.subheader("📊 Recent Transfers")
            
            # Get recent transactions for the selected users
            transactions = sim.get_all_transactions()
            relevant_transactions = [
                tx for tx in transactions 
                if tx['sender_id'] in [sender_id, receiver_id] 
                or tx['receiver_id'] in [sender_id, receiver_id]
            ]
            
            if relevant_transactions:
                for tx in sorted(relevant_transactions, key=lambda x: x['timestamp'], reverse=True)[:5]:
                    # Get user names safely with defaults
                    sender_name = next((u['name'] for u in users if u['user_id'] == tx['sender_id']), "Unknown User")
                    receiver_name = next((u['name'] for u in users if u['user_id'] == tx['receiver_id']), "Unknown User")
                    
                    st.markdown(f"""
                    <div class="recent-transfer-item">
                        🕒 {tx['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}<br>
                        From: {sender_name}<br>
                        To: {receiver_name}<br>
                        Amount: {tx['amount']:.2f} units
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No recent transfers between selected users")
                
            # Transfer Tips
            st.markdown("""
            ### 💡 Transfer Tips
            - Ensure sufficient energy balance
            - Verify recipient details
            - Check transaction history
            - Monitor credit balance
            """)
            st.markdown('</div>', unsafe_allow_html=True)

# Transaction Log
elif page == "Transaction Log":
    st.header("Transaction Log")
    
    transactions = sim.get_all_transactions()
    if transactions:
        df = pd.DataFrame(transactions)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp', ascending=False)
        
        st.dataframe(
            df.style.format({
                'amount': '{:.2f}',
                'timestamp': lambda x: x.strftime('%Y-%m-%d %H:%M:%S')
            }),
            use_container_width=True
        )
    else:
        st.info("No transactions recorded yet")

# Run Simulation
elif page == "Run Simulation":
    st.header("Run Simulation")
    
    num_transfers = st.slider(
        "Number of Random Transfers",
        min_value=1,
        max_value=20,
        value=5
    )
    
    if st.button("Run Simulation"):
        with st.spinner("Running simulation..."):
            transactions = sim.simulate_random_transfers(num_transfers)
            
            if transactions:
                st.success(f"Completed {len(transactions)} random transfers!")
                
                df = pd.DataFrame(transactions)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp', ascending=False)
                
                st.subheader("Simulation Transactions")
                st.dataframe(
                    df.style.format({
                        'amount': '{:.2f}',
                        'timestamp': lambda x: x.strftime('%Y-%m-%d %H:%M:%S')
                    }),
                    use_container_width=True
                )
            else:
                st.warning("No transfers completed. Ensure there are enough users in the system.")

# Summary Statistics
else:
    st.header("Summary Statistics")
    
    stats = sim.get_summary_statistics()
    if stats:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Energy in System", f"{stats.get('total_energy', 0):.2f}")
        
        with col2:
            st.metric("Total Credits in System", f"{stats.get('total_credits', 0):.2f}")
        
        with col3:
            st.metric("Number of Users", stats.get('user_count', 0))
        
        if 'most_active_user' in stats:
            st.subheader("Most Active User")
            active_user = sim.get_user_balance(stats['most_active_user']['user_id'])
            if active_user:
                st.info(f"""
                User: {active_user['name']} ({active_user['user_id']})
                Energy Balance: {active_user['energy_balance']:.2f} units
                Credit Balance: {active_user['credit_balance']:.2f} credits
                Number of Transactions: {stats['most_active_user']['transaction_count']}
                """)