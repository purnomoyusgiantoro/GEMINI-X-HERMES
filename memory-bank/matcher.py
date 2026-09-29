"""
Fuzzy matching engine for error solutions.
"""
import difflib
import re
from typing import List, Dict, Any, Optional, Tuple
try:
    from .bank import ErrorMemoryBank, ErrorCategory
except (ImportError, ValueError):
    try:
        from bank import ErrorMemoryBank, ErrorCategory
    except (ImportError, ModuleNotFoundError):
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        from bank import ErrorMemoryBank, ErrorCategory

class ErrorMatcher:
    """Fuzzy matching engine for the Error Memory Bank."""
    
    def __init__(self, bank: ErrorMemoryBank):
        self.bank = bank

    def _normalize(self, text: str) -> str:
        """Normalizes text by lowercasing, stripping paths, and stripping line numbers."""
        text = text.lower()
        # Remove file paths
        text = re.sub(r'(/|\\)[\w\.-]+(/|\\)[\w\.-]+', '<path>', text)
        text = re.sub(r'[a-z]:\\(?:[\w\.\-]+\\)*[\w\.\-]+', '<path>', text) # windows paths
        # Remove line numbers
        text = re.sub(r'line \d+', 'line <num>', text)
        text = re.sub(r':\d+:', ':<num>:', text)
        return text.strip()

    def find_similar(self, error_text: str, threshold: float = 0.6) -> List[Tuple[Dict[str, Any], float]]:
        """Finds similar errors in the bank above a similarity threshold."""
        norm_query = self._normalize(error_text)
        results = []
        
        for error in self.bank.errors:
            norm_sig = self._normalize(error["error_signature"])
            ratio = difflib.SequenceMatcher(None, norm_query, norm_sig).ratio()
            if ratio >= threshold:
                results.append((error, ratio))
                
        # Sort by similarity ratio descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def suggest_solution(self, error_text: str) -> Optional[Tuple[Dict[str, Any], float]]:
        """Returns the best matching solution with its confidence/similarity score."""
        matches = self.find_similar(error_text)
        if matches:
            return matches[0]
        return None

if __name__ == "__main__":
    db_path = Path("test_matcher_errors.json")
    bank = ErrorMemoryBank(db_path)
    
    # Add some sample errors
    bank.add_error(
        category=ErrorCategory.RUNTIME,
        error_signature="TypeError: Cannot read properties of undefined (reading 'length')",
        root_cause="State array was not initialized",
        solution="Initialize state with an empty array or use optional chaining."
    )
    bank.add_error(
        category=ErrorCategory.SYNTAX,
        error_signature="SyntaxError: unexpected EOF while parsing",
        root_cause="Missing closing parenthesis",
        solution="Check for missing brackets or parentheses."
    )
    
    matcher = ErrorMatcher(bank)
    
    test_error = "TypeError: Cannot read properties of undefined (reading 'length') at Object.render (app.js:42:15)"
    print(f"Testing with error:\\n{test_error}\\n")
    
    suggestion = matcher.suggest_solution(test_error)
    if suggestion:
        error_data, score = suggestion
        print(f"Match found! Score: {score:.2f}")
        print(f"Solution: {error_data['solution']}")
    else:
        print("No match found.")
        
    # Cleanup
    if db_path.exists():
        db_path.unlink()
