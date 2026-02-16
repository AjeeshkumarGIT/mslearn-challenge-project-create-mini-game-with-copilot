import React, { useState } from 'react';
import './RockPaperScissors.css';

const choices = ['rock', 'paper', 'scissors'];

function getResult(p1, p2) {
  if (p1 === p2) return 'Tie!';
  if (
    (p1 === 'rock' && p2 === 'scissors') ||
    (p1 === 'scissors' && p2 === 'paper') ||
    (p1 === 'paper' && p2 === 'rock')
  ) {
    return 'You win!';
  }
  return 'You lose!';
}

export default function RockPaperScissors() {
  const [playerChoice, setPlayerChoice] = useState('');
  const [computerChoice, setComputerChoice] = useState('');
  const [result, setResult] = useState('');
  const [score, setScore] = useState(0);
  const [round, setRound] = useState(1);

  const handleChoice = (choice) => {
    const compChoice = choices[Math.floor(Math.random() * 3)];
    setPlayerChoice(choice);
    setComputerChoice(compChoice);
    const res = getResult(choice, compChoice);
    setResult(res);
    setRound(r => r + 1);
    if (res === 'You win!') setScore(s => s + 1);
  };

  const handleReset = () => {
    setPlayerChoice('');
    setComputerChoice('');
    setResult('');
    setScore(0);
    setRound(1);
  };

  return (
    <div className="rps-container">
      <h1>Rock Paper Scissors</h1>
      <div className="score">Score: {score} | Round: {round}</div>
      <div className="choices">
        {choices.map(choice => (
          <button key={choice} onClick={() => handleChoice(choice)}>{choice.charAt(0).toUpperCase() + choice.slice(1)}</button>
        ))}
      </div>
      {result && (
        <div className="result">
          <p>You chose: <strong>{playerChoice}</strong></p>
          <p>Computer chose: <strong>{computerChoice}</strong></p>
          <h2>{result}</h2>
        </div>
      )}
      <button className="reset-btn" onClick={handleReset}>Reset</button>
    </div>
  );
}
