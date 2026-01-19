import React, { useState, useEffect } from 'react';

const Voting = () => {
  const [proposals, setProposals] = useState([]);
  const [newProposal, setNewProposal] = useState({
    title: '',
    description: '',
    asset_symbol: '',
    target_amount: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchProposals();
  }, []);

  const fetchProposals = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch('http://localhost:8000/api/voting/proposals');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Убеждаемся, что data - массив
      if (Array.isArray(data)) {
        setProposals(data);
      } else {
        console.warn('Expected array but got:', data);
        setProposals([]);
      }
    } catch (error) {
      console.error('Error fetching proposals:', error);
      setError('Failed to load proposals');
      // Mock data for demo
      setProposals([
        {
          id: 1,
          title: "Tech Growth Fund",
          description: "Investment in emerging tech companies",
          asset_symbol: "TECH",
          target_amount: 50000,
          status: "voting"
        },
        {
          id: 2,
          title: "Green Energy Portfolio",
          description: "Sustainable energy investments",
          asset_symbol: "GREEN", 
          target_amount: 75000,
          status: "voting"
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const createProposal = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      const response = await fetch('http://localhost:8000/api/voting/proposals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...newProposal,
          proposer_id: 1,
          target_amount: parseFloat(newProposal.target_amount)
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      setNewProposal({ title: '', description: '', asset_symbol: '', target_amount: '' });
      fetchProposals();
      alert('Proposal created successfully!');
    } catch (error) {
      console.error('Error creating proposal:', error);
      setError('Failed to create proposal');
    }
  };

  const castVote = async (proposalId, voteType) => {
    setError('');
    
    try {
      const response = await fetch('http://localhost:8000/api/voting/vote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 1,
          proposal_id: proposalId,
          vote_type: voteType
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      fetchProposals();
      alert('Vote cast successfully!');
    } catch (error) {
      console.error('Error casting vote:', error);
      setError('Failed to cast vote');
    }
  };

  // Убедимся, что proposals всегда массив
  const safeProposals = Array.isArray(proposals) ? proposals : [];

  return (
    <div className="voting-container">
      <h2>🐝 Collective Voting</h2>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      <div className="proposal-form">
        <h3>Create New Proposal</h3>
        <form onSubmit={createProposal}>
          <input
            type="text"
            placeholder="Title"
            value={newProposal.title}
            onChange={(e) => setNewProposal({...newProposal, title: e.target.value})}
            required
          />
          <textarea
            placeholder="Description"
            value={newProposal.description}
            onChange={(e) => setNewProposal({...newProposal, description: e.target.value})}
            required
          />
          <input
            type="text"
            placeholder="Asset Symbol"
            value={newProposal.asset_symbol}
            onChange={(e) => setNewProposal({...newProposal, asset_symbol: e.target.value})}
            required
          />
          <input
            type="number"
            placeholder="Target Amount"
            value={newProposal.target_amount}
            onChange={(e) => setNewProposal({...newProposal, target_amount: e.target.value})}
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Creating...' : 'Submit Proposal'}
          </button>
        </form>
      </div>

      <div className="proposals-list">
        <h3>Active Proposals</h3>
        
        {loading && <div className="loading">Loading proposals...</div>}
        
        {!loading && safeProposals.length === 0 && (
          <div className="no-proposals">
            <p>No active proposals yet. Be the first to create one!</p>
          </div>
        )}
        
        {safeProposals.map(proposal => (
          <div key={proposal.id} className="proposal-card">
            <h4>{proposal.title}</h4>
            <p>{proposal.description}</p>
            <div className="proposal-meta">
              <span>Asset: {proposal.asset_symbol}</span>
              <span>Target: ${proposal.target_amount}</span>
              <span>Status: {proposal.status}</span>
            </div>
            <div className="voting-buttons">
              <button 
                className="vote-for"
                onClick={() => castVote(proposal.id, 'for')}
                disabled={loading}
              >
                👍 For
              </button>
              <button 
                className="vote-against"
                onClick={() => castVote(proposal.id, 'against')}
                disabled={loading}
              >
                👎 Against
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Voting;