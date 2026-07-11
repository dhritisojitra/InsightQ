import { useState } from "react";
import { GraduationCap, RefreshCw, CheckCircle2, XCircle, ChevronDown, ChevronUp } from "lucide-react";
import { mcqApi } from "../api/client";
import "./MCQPanel.css";

export default function MCQPanel({ docId }) {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [numQ, setNumQ] = useState(5);
  const [difficulty, setDifficulty] = useState("medium");
  const [selected, setSelected] = useState({}); // {qIndex: "A"}
  const [revealed, setRevealed] = useState({}); // {qIndex: true}
  const [expanded, setExpanded] = useState({});

  const generate = async () => {
    setLoading(true);
    setError("");
    setSelected({});
    setRevealed({});
    setExpanded({});
    try {
      const { data } = await mcqApi.generate(docId, numQ, difficulty);
      setQuestions(data.questions || []);
    } catch (err) {
      setError(err.message || "Failed to generate MCQs");
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (qIdx, label) => {
    if (revealed[qIdx]) return;
    setSelected((prev) => ({ ...prev, [qIdx]: label }));
  };

  const handleReveal = (qIdx) => {
    setRevealed((prev) => ({ ...prev, [qIdx]: true }));
  };

  const toggleExpand = (qIdx) => {
    setExpanded((prev) => ({ ...prev, [qIdx]: !prev[qIdx] }));
  };

  const score = Object.entries(revealed).filter(
    ([qi]) => selected[qi] === questions[Number(qi)]?.correct_answer
  ).length;

  return (
    <div className="mcq-panel">
      {/* Controls */}
      <div className="mcq-controls">
        <div className="mcq-controls-left">
          <GraduationCap size={18} className="mcq-icon" />
          <h3>MCQ Generator</h3>
        </div>
        <div className="mcq-controls-right">
          <select
            className="mcq-select"
            value={numQ}
            onChange={(e) => setNumQ(Number(e.target.value))}
            id="mcq-num-select"
          >
            {[3, 5, 8, 10].map((n) => (
              <option key={n} value={n}>{n} questions</option>
            ))}
          </select>
          <select
            className="mcq-select"
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
            id="mcq-difficulty-select"
          >
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
          <button
            className="btn btn-primary btn-sm"
            onClick={generate}
            disabled={loading}
            id="mcq-generate-btn"
          >
            <RefreshCw size={14} className={loading ? "spin" : ""} />
            {loading ? "Generating…" : questions.length > 0 ? "Regenerate" : "Generate"}
          </button>
        </div>
      </div>

      {/* Score (when answers revealed) */}
      {Object.keys(revealed).length > 0 && (
        <div className="mcq-score animate-fadeIn">
          <CheckCircle2 size={16} />
          Score: {score} / {Object.keys(revealed).length} correct
        </div>
      )}

      {error && <p className="mcq-error">{error}</p>}

      {loading && (
        <div className="mcq-loading">
          {[1, 2, 3].map((i) => (
            <div key={i} className="mcq-skeleton">
              <div className="skeleton" style={{ height: 20, width: "70%", marginBottom: 12 }} />
              {[1, 2, 3, 4].map((j) => (
                <div key={j} className="skeleton" style={{ height: 40, marginBottom: 8, borderRadius: 8 }} />
              ))}
            </div>
          ))}
        </div>
      )}

      {/* Questions */}
      {!loading && questions.length > 0 && (
        <div className="mcq-list stagger-children">
          {questions.map((q, qi) => {
            const isRevealed = revealed[qi];
            const userAnswer = selected[qi];
            const isExpanded = expanded[qi];

            return (
              <div key={qi} className="mcq-card glass-card animate-fadeIn">
                <div className="mcq-question-header" onClick={() => toggleExpand(qi)}>
                  <span className="mcq-q-num">Q{qi + 1}</span>
                  <p className="mcq-question-text">{q.question}</p>
                  {q.source_page && (
                    <span className="badge badge-cyan">p.{q.source_page}</span>
                  )}
                  {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </div>

                {isExpanded && (
                  <div className="mcq-options animate-fadeIn">
                    {q.options.map((opt) => {
                      const isCorrect = opt.label === q.correct_answer;
                      const isSelected = userAnswer === opt.label;
                      let cls = "mcq-option";
                      if (isRevealed) {
                        if (isCorrect) cls += " correct";
                        else if (isSelected && !isCorrect) cls += " wrong";
                      } else if (isSelected) {
                        cls += " selected";
                      }

                      return (
                        <button
                          key={opt.label}
                          className={cls}
                          onClick={() => handleSelect(qi, opt.label)}
                          disabled={isRevealed}
                        >
                          <span className="mcq-option-label">{opt.label}</span>
                          <span className="mcq-option-text">{opt.text}</span>
                          {isRevealed && isCorrect && <CheckCircle2 size={16} className="mcq-icon-correct" />}
                          {isRevealed && isSelected && !isCorrect && <XCircle size={16} className="mcq-icon-wrong" />}
                        </button>
                      );
                    })}

                    {!isRevealed ? (
                      <button
                        className="btn btn-secondary btn-sm mcq-reveal-btn"
                        onClick={() => handleReveal(qi)}
                        disabled={!userAnswer}
                      >
                        Check Answer
                      </button>
                    ) : (
                      <div className="mcq-explanation animate-fadeIn">
                        <strong>Explanation:</strong> {q.explanation}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {!loading && questions.length === 0 && !error && (
        <div className="mcq-empty">
          <GraduationCap size={32} />
          <p>Click Generate to create multiple-choice questions from this document.</p>
        </div>
      )}
    </div>
  );
}
