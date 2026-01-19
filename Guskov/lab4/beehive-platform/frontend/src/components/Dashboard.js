import React, { useState, useEffect } from 'react';

const Dashboard = () => {
  const [userStats, setUserStats] = useState({
    bee_rating: 0,
    voting_weight: 0,
    total_contribution: 0,
    proposals_count: 0
  });

  useEffect(() => {
    fetchUserStats();
  }, []);

  const fetchUserStats = async () => {
    // Mock data for demo
    setUserStats({
      bee_rating: 2.5,
      voting_weight: 1.5,
      total_contribution: 15000,
      proposals_count: 3
    });
  };

  return (
    <div className="dashboard-container">
      <h2>🐝 Your Hive Dashboard</h2>
      
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Bee Rating</h3>
          <div className="value">{userStats.bee_rating} ⭐</div>
        </div>
        <div className="stat-card">
          <h3>Voting Weight</h3>
          <div className="value">{userStats.voting_weight}</div>
        </div>
        <div className="stat-card">
          <h3>Total Contribution</h3>
          <div className="value">${userStats.total_contribution}</div>
        </div>
        <div className="stat-card">
          <h3>Proposals Made</h3>
          <div className="value">{userStats.proposals_count}</div>
        </div>
      </div>

      <div className="hive-activity">
        <h3>Recent Hive Activity</h3>
        <div className="activity-list">
          <div className="activity-item">
            <span>✅ Proposal "Tech Investment" reached consensus</span>
            <small>2 hours ago</small>
          </div>
          <div className="activity-item">
            <span>🗳️ New vote started for "Real Estate Fund"</span>
            <small>5 hours ago</small>
          </div>
          <div className="activity-item">
            <span>👥 Your withdrawal request needs 2 more approvals</span>
            <small>1 day ago</small>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;