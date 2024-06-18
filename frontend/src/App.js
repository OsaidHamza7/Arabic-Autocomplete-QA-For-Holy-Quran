import React, { useState } from "react";
import "./App.css";

import SearchBar from "./Component/SearchBar";
import questions from "./Data.json";
import popularQuestions from "./popular_questions.json";

function App() {
    const [activeIndex, setActiveIndex] = useState(null);  // State to track the active question

    const toggleQuestion = index => {
        // Toggle active question to expand/collapse answers
        setActiveIndex(activeIndex === index ? null : index);
    };

    return (
      <div className="App">
        <SearchBar  placeholder="ابحث هنا ..." data={questions} />
        <h2>الأسئلة الشائعة</h2>
        <div className="popular-questions-container">
          <ul className="popular-questions">
            {popularQuestions.map((question, index) => (
              <li key={index} className="question">
              {question.q}
              <p className="popular-answer">{question.a}</p>
              </li>
            ))}
          </ul>
        </div>
      </div>
    );
}

export default App;
