# Unit Test Specifications for Plagiarism Checker

This document specifies the unit testing approach, frameworks, and detailed test cases for each module of the plagiarism checker. AI agents should follow these specifications when implementing tests to ensure code quality and reliability.

## Testing Strategy

### 1. Testing Framework
- **Primary Framework**: `pytest` (Python)
- **Mocking Library**: `unittest.mock` or `pytest-mock`
- **Coverage Tool**: `pytest-cov`
- **Test Discovery**: Standard pytest discovery (`test_*.py` or `*_test.py` files)

### 2. Test Organization
```
tests/
├── __init__.py
├── test_pdf_extractor.py
├── test_preprocessor.py
├── test_chunker.py
├── test_api_client.py
├── test_similarity.py
├── test_report_generator.py
└── conftest.py          # Shared fixtures and configuration
```

### 3. Test Naming Conventions
- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>` or `Test<Functionality>`
- Test methods: `test_<description_of_what_is_tested>`
- Use descriptive names that explain the scenario and expected outcome

### 4. Test Structure (AAA Pattern)
Each test should follow Arrange-Act-Assert:
1. **Arrange**: Set up preconditions and inputs
2. **Act**: Execute the function or method under test
3. **Assert**: Verify the expected outcomes

### 5. Coverage Goals
- **Target**: >90% line coverage for core modules
- **Critical Path**: 100% coverage for security-sensitive and data flow code
- **Exclusions**: Simple getters/setters, UI code (tested via integration/E2E)

## Module-Specific Test Specifications

### 1. PDF Extractor Module (`utils/pdf_extractor.py`)

#### Functions to Test
- `extract_text_from_pdf(file_stream) -> str`

#### Test Cases

| Test Case ID | Description | Input | Expected Output | Notes |
|--------------|-------------|-------|-----------------|-------|
| PE001 | Extract text from simple PDF | Valid PDF stream with text | Extracted text string | Basic functionality |
| PE002 | Handle empty PDF | Empty PDF stream | Empty string | Edge case |
| PE003 | Handle PDF with only images | Image-only PDF | Empty string or minimal text | OCR not implemented in MVP |
| PE004 | Preserve paragraph breaks | PDF with paragraphs | Text with `\n\n` separators | Formatting preservation |
| PE005 | Handle special characters | PDF with Unicode | Correctly decoded text | UTF-8 handling |
| PE006 | Reject non-PDF file | Non-PDF stream | Exception or empty string | Error handling |
| PE007 | Handle corrupted PDF | Damaged PDF stream | Graceful error handling | Robustness |
| PE008 | Close PDF resource | Any PDF | No resource leaks | Resource management |
| PE009 | Handle password-protected PDF | Encrypted PDF | Appropriate error | Security consideration |
| PE010 | Extract from multi-column PDF | Multi-column PDF | Logical reading order | Layout preservation |

#### Mocking Strategy
- Use `unittest.mock.patch` to mock `fitz.open()` 
- Return mock document objects with predefined `get_text()` returns
- Test both successful and error scenarios

#### Sample Test Structure
```python
def test_extract_text_from_pdf_success(mocker):
    # Arrange
    mock_doc = mocker.Mock()
    mock_doc.__enter__.return_value = mock_doc
    mock_doc.__exit__.return_value = None
    mock_doc.get_text.side_effect = ["Page 1 text\n", "Page 2 text\n"]
    
    mock_fitz_open = mocker.patch('fitz.open', return_value=mock_doc)
    fake_stream = io.BytesIO(b"fake pdf content")
    
    # Act
    result = extract_text_from_pdf(fake_stream)
    
    # Assert
    assert result == "Page 1 text\nPage 2 text\n"
    mock_fitz_open.assert_called_once_with(stream=fake_stream, filetype="pdf")
    assert mock_doc.get_text.call_count == 2
```

### 2. Preprocessor Module (`utils/preprocessor.py`)

#### Functions to Test
- `clean_text(text: str) -> str`
- `remove_bibliography(text: str, exclude_refs: bool = False) -> str`
- `remove_headers_footers(text: str) -> str` (if implemented)
- `remove_page_numbers(text: str) -> str` (if implemented)

#### Test Cases

| Test Case ID | Description | Input | Expected Output | Notes |
|--------------|-------------|-------|-----------------|-------|
| PR001 | Clean text with extra spaces | `"  Hello   World  "` | `"Hello World"` | Whitespace normalization |
| PR002 | Clean text with newlines | `"Line 1\n\n\nLine 2"` | `"Line 1\n\nLine 2"` | Excessive newline reduction |
| PR003 | Clean text with tabs | `"Hello\t\tWorld"` | `"Hello World"` | Tab to space conversion |
| PR004 | Keep single spaces | `"Hello World"` | `"Hello World"` | No over-cleaning |
| PR005 | Handle empty string | `""` | `""` | Edge case |
| PR006 | Handle only whitespace | `"   \n\t  "` | `""` | Complete whitespace removal |
| PR007 | Remove bibliography (enabled) | Text + `\nReferences\n[1] Ref` | Text only (ref removed) | Basic functionality |
| PR008 | Keep bibliography (disabled) | Text + `\nReferences\n[1] Ref` | Text + refs intact | Flag respect |
| PR009 | Handle various biblio headers | `"DAFTAR PUSTAKA\n..."` | Content before header | Multiple language support |
| PR010 | Handle numbered ref patterns | Text + `\n1. First ref\n2. Second` | Text only | Regex pattern matching |
| PR011 | Not remove similar headings | `"Introduction\nReferences to methods..."` | Full text preserved | Context awareness |
| PR012 | Handle no bibliography | Plain text | Same text | No false positives |
| PR013 | Remove headers/footers | Repeated header/footer text | Content only | If implemented |
| PR014 | Remove page numbers | `"...\n12\n..."` | Content without numbers | If implemented |
| PR015 | Combine preprocessing steps | Raw text | Cleaned, de-headed, de-bibliographed text | Integration |

#### Special Considerations
- Bibliography detection should be robust but not over-aggressive
- Test with various academic paper formats (IEEE, ACM, APA, etc.)
- Consider false positives (e.g., "References" in actual content)

### 3. Chunker Module (`utils/chunker.py`)

#### Functions to Test
- `sentence_tokenize(text: str) -> List[str]`
- `create_chunks(sentences: List[str], chunk_size: int = 4) -> List[str]`
- `create_overlapping_chunks(sentences: List[str], chunk_size: int, overlap: int) -> List[str]` (if implemented)

#### Test Cases

| Test Case ID | Description | Input | Expected Output | Notes |
|--------------|-------------|-------|-----------------|-------|
| CH001 | Tokenize simple sentences | `"A. B. C."` | `["A.", "B.", "C."]` | Basic sentence splitting |
| CH002 | Handle abbreviations | `"Mr. Smith went to the U.S. He saw Dr. Jones."` | `["Mr. Smith went to the U.S.", "He saw Dr. Jones."]` | Abbreviation awareness |
| CH003 | Handle decimals | `"Price is $3.99. It's a good deal."` | `["Price is $3.99.", "It's a good deal."]` | Decimal point handling |
| CH004 | Handle ellipsis | `"Wait... what happened? I'm confused!"` | `["Wait...", "what happened?", "I'm confused!"]` | Ellipsis treatment |
| CH005 | Handle quotes | `'He said, "Hello." Then left.'` | `['He said, "Hello."', "Then left."]` | Quote handling |
| CH006 | Empty string input | `""` | `[]` | Edge case |
| CH007 | Single sentence | `"One sentence."` | `["One sentence."]` | Minimum input |
| CH008 | No punctuation | `"One two three"` | `["One two three"]` | Fallback behavior |
| CH009 | Create chunks size 2 | `["S1","S2","S3","S4"]` | `["S1 S2", "S3 S4"]` | Basic chunking |
| CH010 | Create chunks size 3 | `["S1","S2","S3","S4","S5"]` | `["S1 S2 S3", "S4 S5"]` | With remainder |
| CH011 | Chunk size 1 | `["A","B","C"]` | `["A","B","C"]` | Each sentence separate |
| CH012 | Chunk size > list | `["A","B"]` with size 5 | `["A B"]` | Handle overflow |
| CH013 | Empty sentence list | `[]` | `[]` | Edge case |
| CH014 | Preserve original spacing | `["Sentence one.  ", "  Sentence two."]` | `"Sentence one.   Sentence two."` | Spacing handling |
| CH015 | Handle very long sentences | `["Very long sentence with many words..."]` | Same as input | No splitting within sentence |

#### Special Considerations
- Use NLTK's Punkt tokenizer which is pre-trained
- Test with multilingual text if applicable
- Verify sentence boundary detection accuracy

### 4. API Client Module (`utils/api_client.py`)

#### Functions to Test
- `search_academic_sources(query: str, limit: int = 3) -> List[Dict]`
- `fetch_paper_abstract(paper_id: str) -> Optional[str]` (if implemented)
- `rate_limit_handler()` or similar (if implemented)

#### Test Cases

| Test Case ID | Description | Input | Expected Output | Notes |
|--------------|-------------|-------|-----------------|-------|
| API001 | Successful API call | `"machine learning"` | List of paper dicts | Mock successful response |
| API002 | Empty query | `""` | Empty list or appropriate response | Edge case |
| API003 | Very long query | `"a" * 1000` | Handled gracefully | Input limits |
| API004 | Special characters in query | `"machine-learning: AI's future?"` | Properly encoded/query | Special char handling |
| API005 | API returns no results | Mock empty response | Empty list | Zero results handling |
| API006 | Network timeout | Simulate timeout | Retry mechanism or error | Error handling |
| API007 | API rate limit (429) | Simulate 429 response | Backoff/retry or error | Rate limit handling |
| API008 | Server error (500) | Simulate 500 response | Error handling | Server error handling |
| API009 | Invalid JSON response | Malformed JSON | Graceful error handling | Response validation |
| API010 | Missing expected fields | Partial JSON | Handle missing data | Data validation |
| API011 | Respect limit parameter | Query with limit=1 | Return max 1 item | Parameter enforcement |
| API012 | Cache hit scenario | Repeated query | Return cached result | If caching implemented |
| API013 | Cache miss scenario | New query | Fetch from API | If caching implemented |
| API014 | Proper URL encoding | Query with spaces | Correctly encoded URL | HTTP compliance |
| API015 | Timeout configuration | Valid timeout setting | Used in request | Config respect |

#### Mocking Strategy
- Mock `requests.get()` calls
- Return predefined `Response` objects with specific status codes and JSON
- Test success, various error codes, timeouts, and connection errors

#### Sample Test Structure
```python
def test_search_academic_services_success(mocker):
    # Arrange
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "total": 2,
        "data": [
            {"paperId": "1", "title": "Paper 1", "abstract": "Abstract 1"},
            {"paperId": "2", "title": "Paper 2", "abstract": "Abstract 2"}
        ]
    }
    mock_get = mocker.patch('requests.get', return_value=mock_response)
    
    # Act
    results = search_academic_sources("test query", limit=2)
    
    # Assert
    assert len(results) == 2
    assert results[0]["title"] == "Paper 1"
    assert results[1]["paperId"] == "2"
    mock_get.assert_called_once()
    # Check that params were passed correctly
    args, kwargs = mock_get.call_args
    assert kwargs['params']['query'] == "test query"
    assert kwargs['params']['limit'] == 2
```

### 5. Similarity Module (`utils/similarity.py`)

#### Functions to Test
- `compute_similarity(text1: str, text2: str) -> float`
- `find_best_match(chunk: str, sources: List[Dict]) -> Tuple[float, Optional[Dict]]`
- `compute_tfidf_matrix(texts: List[str]) -> Tuple[np.ndarray, TfidfVectorizer]` (if exposed)

#### Test Cases

| Test Case ID | Description | Input | Expected Output | Notes |
|--------------|-------------|-------|-----------------|-------|
| SIM001 | Identical texts | `("hello", "hello")` | `1.0` | Perfect match |
| SIM002 | Completely different | `("cat", "dog")` | Low value (<0.3) | No overlap |
| SIM003 | Empty string | `("", "hello")` | `0.0` | Edge case |
| SIM004 | Both empty | `("", "")` | `0.0` or `1.0` depending on impl | Edge case |
| SIM005 | Partial overlap | `("the cat sat", "the dog sat")` | Medium value (~0.5) | Shared words |
| SIM006 | Substring | `("hello world", "world")` | High value | Containment |
| SIM007 | Case sensitivity | `("Hello", "hello")` | High value (TF-IDF norm) | Case folding |
| SIM008 | Whitespace differences | `("hello  world", "hello world")` | High value | Whitespace normalization |
| SIM009 | Punctuation differences | `("hello, world!", "hello world")` | High value | Punctuation handling |
| SIM010 | Very long texts | Two long paragraphs | Reasonable score | Performance |
| SIM011 | Find best match - clear winner | Chunk + 3 sources (0.2, 0.8, 0.5) | `(0.8, source2)` | Correct selection |
| SIM012 | Find best match - tie | Chunk + 2 sources (both 0.7) | `(0.7, first_occurrence)` | Tie-breaking |
| SIM013 | Find best match - empty sources | Chunk + `[]` | `(0.0, None)` | Edge case |
| SIM014 | Find best match - None source | Chunk + `[{"text": ""}]` | `(score, source)` | Handle empty source text |
| SIM015 | Batch processing efficiency | List of 10 texts | Consistent results | If batch function exists |

#### Special Considerations
- TF-IDF is sensitive to corpus - tests should use consistent vectorizer fitting
- Consider testing with known vectors for deterministic results
- Test edge cases that could cause division by zero in cosine similarity

#### Sample Test Structure
```python
def test_compute_similarity_identical():
    # Arrange
    text = "The quick brown fox jumps over the lazy dog"
    
    # Act
    similarity = compute_similarity(text, text)
    
    # Assert
    assert abs(similarity - 1.0) < 1e-10  # Account for floating point

def test_compute_similarity_orthogonal(mocker):
    # Arrange - Mock vectorizer to produce known vectors
    # This approach makes test deterministic regardless of actual TF-IDF values
    text1 = "apple banana cherry"
    text2 = "dog elephant frog"
    
    # Act
    similarity = compute_similarity(text1, text2)
    
    # Assert - Should be very low since no shared terms
    assert similarity < 0.1
```

### 6. Report Generator Module (`utils/report_generator.py`)

#### Functions to Test
- `aggregate_similarities(chunk_results: List[Dict]) -> Tuple[float, List[Dict]]`
- `format_sources_for_display(sources: List[Dict]) -> List[Dict]` (if implemented)
- `generate_highlighted_text(original_text: str, chunk_scores: List[Tuple[str, float, Tuple[int, int]]]) -> str` (if implemented)

#### Test Cases

| Test Case ID | Description | Input | Expected Output | Notes |
|--------------|-------------|-------|-----------------|-------|
| RG001 | Empty input | `[]` | `(0.0, [])` | Base case |
| RG002 | Single chunk | `[{"chunk": "text", "score": 0.5, "source": {"title": "A"}}]` | `(50.0, [{"title": "A", "similarity": 0.5}])` | Percentage conversion |
| RG003 | Multiple chunks same source | Two chunks with score 0.6, same source | `(60.0, [one_source_with_sim_0.6])` | Deduplication |
| RG004 | Multiple chunks different sources | Chunks: (0.8, SourceA), (0.4, SourceB) | `(60.0, [A(0.8), B(0.4)])` | Average calculation |
| RG005 | Zero scores | Three chunks with score 0.0 | `(0.0, [])` | No matches |
| RG006 | Perfect scores | Two chunks with score 1.0 | `(100.0, [source(1.0)])` | Cap at 100% |
| RG007 | Scores over 1.0 (impossible but test) | Score 1.2 | `(100.0, [source(1.0)])` | Should clamp or handle |
| RG008 | Sorting by similarity | Scores: 0.3 (C), 0.9 (A), 0.6 (B) | Order: A(0.9), B(0.6), C(0.3) | Descending sort |
| RG009 | Source deduplication | Three chunks: two from Source A (0.7,0.9), one from B (0.5) | Two sources: A(0.9), B(0.5) | Keep highest score per source |
| RG010 | Missing source field | Chunk with score but no source | Should handle gracefully | Data validation |
| RG011 | None source | Similar to missing source | Skip or handle | Null safety |
| RG012 | Empty chunk text | `[{"chunk": "", "score": 0.5, "source": {...}}]` | Should include in average | Empty but scored |
| RG013 | Large number of chunks | 1000 chunks with random scores | Correct average and dedup | Performance |
| RG014 | Very small scores | Many 0.001 scores | Small but non-zero percentage | Precision |
| RG015 | Mixed language chunks | Should still work | Language agnostic | Unicode handling |

#### Special Considerations
- Ensure floating point precision doesn't cause incorrect totals
- Handle case where all scores are zero
- Maintain source metadata properly during deduplication

#### Sample Test Structure
```python
def test_aggregate_similarities_deduplication():
    # Arrange
    chunk_results = [
        {
            "chunk": "First chunk about topic A",
            "score": 0.7,
            "source": {"paperId": "1", "title": "Paper A", "similarity": 0.7}
        },
        {
            "chunk": "Second chunk about topic A (different wording)",
            "score": 0.9,
            "source": {"paperId": "1", "title": "Paper A", "similarity": 0.9}  # Same paper
        },
        {
            "chunk": "Chunk about topic B",
            "score": 0.5,
            "source": {"paperId": "2", "title": "Paper B", "similarity": 0.5}
        }
    ]
    
    # Act
    overall_score, sources = aggregate_similarities(chunk_results)
    
    # Assert
    # Average of (0.7, 0.9, 0.5) = 0.7 -> 70.0%
    assert abs(overall_score - 70.0) < 0.01
    
    # Should have 2 unique sources
    assert len(sources) == 2
    
    # Find source A and verify it has the higher score (0.9)
    source_a = next(s for s in sources if s["title"] == "Paper A")
    assert source_a["similarity"] == 0.9
    
    # Source B should have score 0.5
    source_b = next(s for s in sources if s["title"] == "Paper B")
    assert source_b["similarity"] == 0.5
```

### 7. Flask Application Tests (`app.py` or similar)

#### Functions/Endpoints to Test
- `GET /` - Main page
- `POST /check` - File upload and processing
- Error handlers (404, 500, etc.)

#### Test Cases

| Test Case ID | Description | Input | Expected Output | Notes |
|--------------|-------------|-------|-----------------|-------|
| APP001 | GET home page returns form | None | 200 OK, HTML with upload form | Basic routing |
| APP002 | POST without file | Empty form | 400 Bad Request, error message | Validation |
| APP003 | POST with non-PDF file | .txt file | 400 Bad Request, error | File type validation |
| APP004 | POST with valid PDF | Small PDF | 200 OK, JSON results | Success case |
| APP005 | POST with large PDF | Oversized PDF | 413 Payload Too Large or error | Size limits |
| APP006 | POST with bibliography flag | PDF + excludeRefs=true | Processed with exclusion | Flag handling |
| APP007 | POST without bibliography flag | PDF + excludeRefs=false | Processed without exclusion | Flag handling |
| APP008 | Internal error during processing | Simulate exception | 500 Internal Server Error | Error handling |
| APP009 | Timeout during API call | Simulate slow API | Appropriate timeout handling | Resilience |
| APP010 | Valid JSON response structure | Successful processing | JSON with expected keys | Contract testing |
| APP011 | Empty PDF processing | Blank PDF | Handle gracefully | Edge case |
| APP012 | Malformed PDF processing | Corrupted PDF | Error message | Robustness |
| APP013 | Concurrent request handling | Multiple simultaneous | Proper queuing/processing | If applicable |
| APP014 | Session isolation | User A then User B | No cross-contamination | State isolation |
| APP015 | Language/locale in response | Any request | Correct language if i18n | Localization |

#### Testing Strategy
- Use Flask's `test_client()` for request simulation
- Mock external dependencies (PDF processing, API calls)
- Test both success and error paths
- Validate JSON schema of responses
- Test file upload handling specifically

#### Sample Test Structure
```python
def test_upload_success(client, mocker):
    # Arrange
    # Mock the processing pipeline to return predictable results
    mock_process = mocker.patch('app.process_pdf_for_plagiarism')
    mock_process.return_value = {
        'similarity_percentage': 25.0,
        'matched_sources': [],
        'processing_time_ms': 1000
    }
    
    # Create a dummy PDF file
    data = {
        'pdfFile': (io.BytesIO(b'fake pdf content'), 'test.pdf'),
        'excludeRefs': 'on'
    }
    
    # Act
    response = client.post('/check', data=data, content_type='multipart/form-data')
    
    # Assert
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['similarity_percentage'] == 25.0
    assert json_data['success'] == True
    mock_process.assert_called_once()
```

### 8. Test Configuration and Fixtures

#### conftest.py Contents
```python
import pytest
import io
from unittest.mock import Mock

@pytest.fixture
def sample_pdf_bytes():
    """Return bytes of a minimal valid PDF for testing"""
    # This would be actual PDF bytes or a mock
    return b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT\n70 720 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000053 00000 n \n0000000102 00000 n \n0000000179 00000 n \ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n285\n%%EOF"

@pytest.fixture
def mock_fitz_document(mocker):
    """Mock a fitz document with controllable page text"""
    mock_doc = mocker.Mock()
    mock_page = mocker.Mock()
    mock_page.get_text.return_value = "Sample page text\n"
    mock_doc.__iter__.return_value = [mock_page]
    mock_doc.__len__.return_value = 1
    return mock_doc

@pytest.fixture
def mock_api_response(mocker):
    """Mock a successful API response"""
    def _make_response(data=None, status_code=200):
        response = mocker.Mock()
        response.status_code = status_code
        response.json.return_value = data or {
            "total": len(data) if data else 0,
            "data": data or []
        }
        return response
    return _make_response

@pytest.fixture
def client():
    """Flask test client fixture"""
    from app import app
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client
```

### 9. Continuous Integration Integration

#### pytest configuration (`pytest.ini` or `pyproject.toml`)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --strict-markers
    --cov=utils
    --cov-report=term-missing
    --cov-report=html:htmlcov
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

#### Makefile or script for running tests
```makefile
test:
	pytest tests/

test-unit:
	pytest tests/ -m unit

test-integration:
	pytest tests/ -m integration

test-coverage:
	pytest --cov=utils --cov-report=html

test-fast:
	pytest -m "not slow"
```

### 10. Test Data Management

#### Fixtures for Test Data
- **PDF Samples**: Keep minimal PDF bytes in fixtures or use `pytest`-`tmpdir` with generated PDFs
- **API Responses**: Store sample JSON responses in `tests/fixtures/api_responses/`
- **Expected Outputs**: Keep expected text transformations in fixtures
- **Edge Case Documents**: Maintain a small set of problematic PDFs for regression testing

#### External Test Data Sources
For more comprehensive testing, consider:
- PDF files from [PDF Association test suite](https://www.pdfa.org/)
- Academic paper samples from open access repositories
- Corpus datasets for similarity testing (like MSR Paraphrase Corpus)

### 11. Best Practices for AI Agents Implementing Tests

1. **Start Simple**: Begin with happy path tests before edge cases
2. **Test One Thing Per Test**: Each test should verify a single concept
3. **Use Descriptive Names**: Test names should read like specifications
4. **Keep Tests Independent**: No test should depend on another's state
5. **Mock External Dependencies**: Never make real API calls in unit tests
6. **Test Error Conditions**: Validate that errors are handled properly
7. **Check Boundary Conditions**: Test min/max values, empty inputs, etc.
8. **Maintain Test Speed**: Avoid slow operations in unit tests
9. **Update Tests When Code Changes**: Keep tests in sync with implementation
10. **Aim for Meaningful Coverage**: Focus on complex logic, not just line counts

### 12. Sample Complete Test File

Here's what a complete test file for the preprocessor might look like:

```python
"""
Unit tests for the text preprocessor module.
Tests cover text cleaning, bibliography removal, and header/footer processing.
"""

import pytest
from utils.preprocessor import clean_text, remove_bibliography

class TestCleanText:
    """Tests for the clean_text function."""
    
    def test_basic_whitespace_normalization(self):
        """Test that multiple spaces are reduced to single spaces."""
        assert clean_text("Hello   World") == "Hello World"
    
    def test_tab_and_newline_handling(self):
        """Test that tabs and newlines are converted to spaces."""
        assert clean_text("Hello\t\tWorld\n\nTest") == "Hello World Test"
    
    def test_leading_trailing_whitespace_removal(self):
        """Test that leading and trailing whitespace is stripped."""
        assert clean_text("  Hello World  ") == "Hello World"
    
    def test_empty_string(self):
        """Test that empty string returns empty string."""
        assert clean_text("") == ""
    
    def test_only_whitespace(self):
        """Test that string with only whitespace returns empty string."""
        assert clean_text("   \n\t  ") == ""

class TestRemoveBibliography:
    """Tests for the remove_bibliography function."""
    
    def test_removes_bibliography_when_enabled(self):
        """Test that bibliography section is removed when flag is True."""
        text = "Main content here.\n\nReferences\n1. Smith, J. (2020). Paper.\n2. Doe, A. (2021). Another."
        result = remove_bibliography(text, exclude_refs=True)
        assert "References" not in result
        assert "Smith, J. (2020)" not in result
        assert result.strip() == "Main content here."
    
    def test_keeps_bibliography_when_disabled(self):
        """Test that bibliography section is kept when flag is False."""
        text = "Main content here.\n\nReferences\n1. Smith, J. (2020). Paper."
        result = remove_bibliography(text, exclude_refs=False)
        assert "References" in result
        assert "Smith, J. (2020)" in result
        assert "Main content here." in result
    
    @pytest.mark.parametrize("header", [
        "REFERENCES",
        "BIBLIOGRAPHY", 
        "DAFTAR PUSTAKA",
        "文献献上"  # Japanese for references
    ])
    def test_handles_various_bibliography_headers(self, header):
        """Test that different bibliography headers are recognized."""
        text = f"Content before.\n\n{header}\n[1] Reference one.\n[2] Reference two."
        result = remove_bibliography(text, exclude_refs=True)
        assert header not in result
        assert "Reference one" not in result
        assert "Reference two" not in result
        assert "Content before." in result
    
    def test_does_not_remove_false_positives(self):
        """Test that similar text in content is not removed."""
        text = "The references section of this paper discusses methodology. "
        text += "We references previous work throughout. "
        text += "In conclusion, our references are thorough."
        result = remove_bibliography(text, exclude_refs=True)
        # Should keep all text since "references" appears in context, not as header
        assert "references" in result.lower()
        assert result == text  # Should be unchanged
    
    def test_handles_multiple_blank_lines(self):
        """Test proper handling of spacing around bibliography."""
        text = "Before.\n\n\n\nREFERENCES\n\n[1] Ref\n\n\nAfter."
        result = remove_bibliography(text, exclude_refs=True)
        assert "Before." in result
        assert "After." in result
        assert "REFERENCES" not in result
```

This comprehensive test specification provides AI agents with clear guidelines for implementing thorough, maintainable unit tests that will ensure the reliability and correctness of the plagiarism checker implementation.