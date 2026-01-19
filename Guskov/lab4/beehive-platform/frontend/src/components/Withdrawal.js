import React, { useState, useEffect } from 'react';

const Withdrawal = () => {
  const [withdrawalAmount, setWithdrawalAmount] = useState('');
  const [requests, setRequests] = useState([]);
  const [userApprovals, setUserApprovals] = useState([]);

  useEffect(() => {
    fetchWithdrawalRequests();
    fetchUserApprovals();
  }, []);

  const fetchWithdrawalRequests = async () => {
    // Mock data
    setRequests([
      {
        id: 1,
        amount: 1000,
        status: 'pending',
        approval_count: 1,
        required_approvals: 3,
        created_at: '2024-01-20T10:00:00'
      }
    ]);
  };

  const fetchUserApprovals = async () => {
    // Mock data
    setUserApprovals([
      {
        id: 2,
        user_id: 3,
        amount: 500,
        created_at: '2024-01-20T09:00:00'
      }
    ]);
  };

  const requestWithdrawal = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/api/withdrawals/request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 1,
          amount: parseFloat(withdrawalAmount)
        })
      });
      
      if (response.ok) {
        setWithdrawalAmount('');
        fetchWithdrawalRequests();
        alert('Withdrawal request submitted! Waiting for hive approval.');
      }
    } catch (error) {
      console.error('Error requesting withdrawal:', error);
    }
  };

  const approveWithdrawal = async (requestId) => {
    try {
      await fetch(`http://localhost:8000/api/withdrawals/approve/${requestId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          approver_id: 1
        })
      });
      
      fetchUserApprovals();
      alert('Withdrawal approved!');
    } catch (error) {
      console.error('Error approving withdrawal:', error);
    }
  };

  return (
    <div className="withdrawal-container">
      <h2>💰 Withdrawal System</h2>
      
      <div className="withdrawal-form">
        <h3>Request Withdrawal</h3>
        <form onSubmit={requestWithdrawal}>
          <input
            type="number"
            placeholder="Amount to withdraw"
            value={withdrawalAmount}
            onChange={(e) => setWithdrawalAmount(e.target.value)}
            required
          />
          <button type="submit">Request Withdrawal</button>
        </form>
        <p><small>Note: Withdrawals require approval from 3 random hive members</small></p>
      </div>

      <div className="pending-requests">
        <h3>Your Withdrawal Requests</h3>
        <div className="requests-list">
          {requests.map(request => (
            <div key={request.id} className="request-card">
              <div>
                <strong>${request.amount}</strong>
                <div>Status: {request.status}</div>
                <div>Approvals: {request.approval_count}/{request.required_approvals}</div>
              </div>
              <div className={`request-status status-${request.status}`}>
                {request.status.toUpperCase()}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="approval-requests">
        <h3>Requests Needing Your Approval</h3>
        <div className="requests-list">
          {userApprovals.map(approval => (
            <div key={approval.id} className="request-card">
              <div>
                <strong>User #{approval.user_id}</strong>
                <div>Amount: ${approval.amount}</div>
                <small>Requested: {new Date(approval.created_at).toLocaleDateString()}</small>
              </div>
              <button 
                className="vote-for"
                onClick={() => approveWithdrawal(approval.id)}
              >
                Approve
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Withdrawal;