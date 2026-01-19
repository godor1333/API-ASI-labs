import React, { useState, useEffect } from 'react';

const InvestmentMap = () => {
  const [decisions, setDecisions] = useState([]);

  useEffect(() => {
    fetchInvestmentDecisions();
  }, []);

  const fetchInvestmentDecisions = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/investments/decisions');
      const data = await response.json();
      setDecisions(data);
    } catch (error) {
      console.error('Error fetching decisions:', error);
      // Mock data for demonstration
      setDecisions([
        {
          id: 1,
          title: "Tech Growth Fund",
          asset: "TECH",
          amount: 50000,
          timestamp: "2024-01-15T10:30:00",
          consensus_ratio: 0.85
        },
        {
          id: 2,
          title: "Green Energy Portfolio",
          asset: "GREEN",
          amount: 75000,
          timestamp: "2024-01-10T14:20:00",
          consensus_ratio: 0.92
        }
      ]);
    }
  };

  return (
    <div className="map-container">
      <h2>🗺️ Investment Decisions Map</h2>
      <p>Visualization of collective investment decisions made by the hive</p>
      
      <div className="decisions-grid">
        {decisions.map(decision => (
          <div key={decision.id} className="decision-card">
            <h4>{decision.title}</h4>
            <div className="decision-meta">
              <span><strong>Asset:</strong> {decision.asset}</span>
              <span><strong>Amount:</strong> ${decision.amount.toLocaleString()}</span>
              <span><strong>Consensus:</strong> {(decision.consensus_ratio * 100).toFixed(1)}%</span>
              <span><strong>Date:</strong> {new Date(decision.timestamp).toLocaleDateString()}</span>
            </div>
          </div>
        ))}
      </div>

      {decisions.length === 0 && (
        <div className="no-decisions">
          <p>No investment decisions have been made yet. Start the first proposal!</p>
        </div>
      )}
    </div>
  );
};

export default InvestmentMap;