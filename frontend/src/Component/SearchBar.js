import React, { useState, useEffect, useRef } from "react";
import './SearchBar.css'; // Ensure your CSS file is correctly imported
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faClock, faTimes } from '@fortawesome/free-solid-svg-icons'; // Import the clock icon

function SearchBar({ placeholder, data }) {
    const [filteredData, setFilteredData] = useState([]);
    const [wordEntered, setWordEntered] = useState("");
    const [selectedAnswer, setSelectedAnswer] = useState("");
    const [searchHistory, setSearchHistory] = useState([]);
    const [isListVisible, setIsListVisible] = useState(false);

    useEffect(() => {
        console.log(searchHistory);
    }, [searchHistory]);

    const searchBarRef = useRef(null);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (searchBarRef.current && !searchBarRef.current.contains(event.target)) {
                setIsListVisible(false);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    const handleFilter = (event) => {
        const searchWord = event.target.value;
        setWordEntered(searchWord);
        setSelectedAnswer(""); // Clear the selected answer when typing starts

        if (searchWord === "") {
            setFilteredData(searchHistory);
        } else {
            const newFilter = data.filter((value) => {
                return value.q.toLowerCase().includes(searchWord.toLowerCase());
            });
            setFilteredData(newFilter);
        }
        setIsListVisible(true); // Ensure list is visible when typing

    };

    const handleClick = (question, answer) => {
        console.log("clicked");
        setWordEntered(question);
        setSelectedAnswer(answer);
        setFilteredData([]);
        setSearchHistory((prevHistory) => {
            const updatedHistory = [{ q: question, a: answer }, ...prevHistory.filter((item) => item.q !== question)];
            return updatedHistory.slice(0, 10); // Keep only the latest 10 searches
        });
        console.log(searchHistory);
    };

    const handleSearch = (event) => {
        console.log("searched");
        event.preventDefault();
        const newFilter = data.filter((value) => {
            return value.q.toLowerCase().includes(wordEntered.toLowerCase());
        });
        setFilteredData(newFilter);
    };
    const handleRemoveHistoryItem = (question) => {
        setSearchHistory((prevHistory) => prevHistory.filter(item => item.q !== question));
    };

    return (
        <div className="row d-flex justify-content-center">
            <div className="col-md-6" ref={searchBarRef}>
                <form className="form" onSubmit={handleSearch}>
                    <button type="submit" className="search-button">
                        <i className="fa fa-search"></i>
                    </button>

                    <input
                        type="text"
                        placeholder={placeholder}
                        className="form-control form-input"
                        value={wordEntered}
                        onChange={handleFilter}
                        onFocus={() => {
                            if (wordEntered === "") {
                                setFilteredData(searchHistory);
                                setIsListVisible(true);
                            }
                        }}

                    />

                    {wordEntered && (
                        <button type="button" className="clear-button" onClick={() => {
                            setWordEntered("");
                            setSelectedAnswer("");
                            setFilteredData(searchHistory);
                            setIsListVisible(true);
                        }}>
                            <i className="fa fa-times"></i>
                        </button>
                    )}

                </form>
                {isListVisible && filteredData.length !== 0 && (
    <div className="dataResult">
        {filteredData.slice(0, 15).map((value, index) => (
            <div className={`list border-bottom d-flex justify-content-between align-items-center ${searchHistory.some(item => item.q === value.q) ? 'history-item' : ''}`} key={index}>
                <div onClick={() => handleClick(value.q, value.a)} className="d-flex flex-column ml-3" style={{ flexGrow: 1 }}>
                    <span>
                        {searchHistory.some(item => item.q === value.q) && (
                            <FontAwesomeIcon icon={faClock} />
                        )}
                        {value.q}
                    </span>
                </div>
                {searchHistory.some(item => item.q === value.q) && (
                    <button className="remove-button" onClick={() => handleRemoveHistoryItem(value.q)}>
                        <FontAwesomeIcon icon={faTimes} />
                    </button>
                )}
            </div>
        ))}
    </div>
)}

                {selectedAnswer && (
                    <div className="answer">
                        <h3>:الإجابة</h3>
                        <p>{selectedAnswer}</p>
                    </div>
                )}
            </div>
        </div>
    );
}

export default SearchBar;
