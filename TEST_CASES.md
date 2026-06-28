# Test Cases and Sample Data for Plagiarism Checker

This document provides comprehensive test cases, sample data, and expected outputs to help AI agents implement and verify the plagiarism checker functionality with precision.

## 1. Sample PDF Documents for Testing

### Test Case 1: Original Document (0% Similarity Expected)
**Filename**: `original_research.pdf`
**Content**: 
```
The Impact of Climate Change on Agricultural Productivity in Southeast Asia

Abstract
This study examines the relationship between climate variability and agricultural productivity across Southeast Asian nations from 2000 to 2020. Using panel data analysis, we find that temperature increases beyond optimal thresholds significantly reduce rice and maize yields, while precipitation changes show mixed effects depending on seasonal timing and irrigation access.

Introduction
Climate change poses significant threats to global food security, particularly in developing regions where agriculture remains a primary livelihood source. Southeast Asia, with its large agrarian populations and vulnerability to climate extremes, represents a critical region for understanding these dynamics...

Methodology
We employ a panel fixed-effects approach using country-level annual data from the World Bank's World Development Indicators and FAO's STAT database. Our sample includes 10 Southeast Asian countries...

Results
The results indicate that a 1°C increase in average growing season temperature above the optimal threshold of 25°C is associated with a 8.3% decrease in rice yields and a 6.7% decrease in maize yields...

Conclusion
Our findings suggest that climate adaptation strategies focused on developing heat-tolerant crop varieties and improving irrigation infrastructure could mitigate substantial productivity losses...
```

### Test Case 2: Lightly Plagiarized Document (20-30% Similarity Expected)
**Filename**: `light_plagiarism.pdf`
**Content**: 
```
The Impact of Climate Change on Agricultural Productivity in Southeast Asia

Abstract
This study examines how climate variability affects agricultural productivity across Southeast Asian nations from 2000 to 2020. Using panel data analysis, we find that temperature increases beyond optimal levels significantly reduce rice and maize yields, while precipitation changes show varying effects depending on seasonal timing and irrigation access.

Introduction
As noted by Smith et al. (2019), climate change poses significant threats to global food security, particularly in developing regions where agriculture remains a primary livelihood source. Southeast Asia, with its large agrarian populations and vulnerability to climate extremes, represents a critical region for understanding these dynamics...

Methodology
Similar to Jones and Lee (2021), we employ a panel fixed-effects approach using country-level annual data from the World Bank's World Development Indicators and FAO's STAT database. Our sample includes 10 Southeast Asian countries covering the period 2000-2020...

Results
Our analysis shows that a 1°C increase in average growing season temperature above the optimal threshold of 25°C correlates with approximately an 8% decrease in rice yields and a 7% decrease in maize yields, consistent with findings by Watanabe et al. (2020)...

Conclusion
These results imply that climate adaptation strategies focusing on developing heat-tolerant crop varieties and improving irrigation infrastructure could help mitigate substantial productivity losses in the region...
```
*Note: Contains paraphrased content with proper attribution to some sources but still contains significant unoriginal phrasing.*

### Test Case 3: Moderately Plagiarized Document (40-50% Similarity Expected)
**Filename**: `moderate_plagiarism.pdf`
**Content**: 
```
Climate Change Effects on Southeast Asian Agriculture

Abstract
This research looks at how climate change affects farming in Southeast Asia from 2000-2020. Using data analysis methods, we found that higher temperatures hurt rice and corn growth, while rain changes have mixed effects.

Introduction
Climate change is a big problem for food around the world, especially in poor farming areas. Southeast Asia has many farmers and is very sensitive to weather changes, making it important to study this area.

Methods
We looked at country data for 10 Southeast Asian nations from 2000 to 2020, getting information from World Bank and FAO databases.

Results
When it gets 1°C hotter than the best temperature for growing (25°C), rice production goes down by about 8% and corn production by about 7%.

Conclusion
To reduce crop losses from heat, we should develop better crop varieties and improve watering systems...
```
*Note: Significant paraphrasing with minimal original structure, similar to patchwriting.*

### Test Case 4: Heavily Plagiarized Document (70-85% Similarity Expected)
**Filename**: `heavy_plagiarism.pdf`
**Content**: 
```
The Impact of Climate Change on Agricultural Productivity in Southeast Asia

Abstract
This study examines the relationship between climate variability and agricultural productivity across Southeast Asian nations from 2000 to 2020. Using panel data analysis, we find that temperature increases beyond optimal thresholds significantly reduce rice and maize yields, while precipitation changes show mixed effects depending on seasonal timing and irrigation access.

Introduction
Climate change poses significant threats to global food security, particularly in developing regions where agriculture remains a primary livelihood source. Southeast Asia, with its large agrarian populations and vulnerability to climate extremes, represents a critical region for understanding these dynamics.

Methodology
We employ a panel fixed-effects approach using country-level annual data from the World Bank's World Development Indicators and FAO's STAT database. Our sample includes 10 Southeast Asian countries...

Results
The results indicate that a 1°C increase in average growing season temperature above the optimal threshold of 25°C is associated with a 8.3% decrease in rice yields and a 6.7% decrease in maize yields...

Conclusion
Our findings suggest that climate adaptation strategies focused on developing heat-tolerant crop varieties and improving irrigation infrastructure could mitigate substantial productivity losses...
```
*Note: Nearly verbatim copying with only minor word changes.*

### Test Case 5: Complete Plagiarism (95-100% Similarity Expected)
**Filename**: `complete_plagiarism.pdf`
**Content**: 
```
The Impact of Climate Change on Agricultural Productivity in Southeast Asia

Abstract
This study examines the relationship between climate variability and agricultural productivity across Southeast Asian nations from 2000 to 2020. Using panel data analysis, we find that temperature increases beyond optimal thresholds significantly reduce rice and maize yields, while precipitation changes show mixed effects depending on seasonal timing and irrigation access.

Introduction
Climate change poses significant threats to global food security, particularly in developing regions where agriculture remains a primary livelihood source. Southeast Asia, with its large agrarian populations and vulnerability to climate extremes, represents a critical region for understanding these dynamics.

Methodology
We employ a panel fixed-effects approach using country-level annual data from the World Bank's World Development Indicators and FAO's STAT database. Our sample includes 10 Southeast Asian countries...

Results
The results indicate that a 1°C increase in average growing season temperature above the optimal threshold of 25°C is associated with a 8.3% decrease in rice yields and a 6.7% decrease in maize yields...

Conclusion
Our findings suggest that climate adaptation strategies focused on developing heat-tolerant crop varieties and improving irrigation infrastructure could mitigate substantial productivity losses...
```
*Note: Exact copy of original text.*

## 2. Unit Test Cases for Individual Components

### PDF Extractor Tests
**File**: `tests/test_pdf_extractor.py`

```python
import unittest
import io
from utils.pdf_extractor import extract_text_from_pdf

class TestPDFExtractor(unittest.TestCase):
    
    def test_extract_text_from_simple_pdf(self):
        # Create a simple PDF in memory (would use reportlab or similar in real test)
        # For demo, we'll mock or use a small fixture
        pass
    
    def test_extract_text_returns_string(self):
        # Given a valid PDF file stream
        pdf_stream = self.get_sample_pdf_stream()
        # When extracting text
        text = extract_text_from_pdf(pdf_stream)
        # Then it should return a string
        self.assertIsInstance(text, str)
    
    def test_extract_text_handles_empty_pdf(self):
        # Given an empty PDF
        empty_pdf = self.get_empty_pdf_stream()
        # When extracting text
        text = extract_text_from_pdf(empty_pdf)
        # Then it should return empty string
        self.assertEqual(text.strip(), "")
    
    def test_extract_text_preserves_structure(self):
        # Given a PDF with known structure
        pdf_stream = self.get_structured_pdf_stream()
        # When extracting text
        text = extract_text_from_pdf(pdf_stream)
        # Then it should contain expected sections
        self.assertIn("Abstract", text)
        self.assertIn("Introduction", text)
        self.assertIn("Conclusion", text)
```

### Preprocessor Tests
**File**: `tests/test_preprocessor.py`

```python
import unittest
from utils.preprocessor import clean_text, remove_bibliography

class TestPreprocessor(unittest.TestCase):
    
    def test_clean_text_removes_extra_whitespace(self):
        # Given text with extra whitespace
        dirty_text = "  This   is    a   test  \n\n  with  spaces  "
        # When cleaning
        clean = clean_text(dirty_text)
        # Then it should normalize whitespace
        self.assertEqual(clean, "This is a test with spaces")
    
    def test_remove_bibliography_when_flag_false(self):
        # Given text with bibliography section
        text_with_refs = "Main content here.\n\nReferences\n1. Smith, J. (2020). Paper.\n2. Doe, A. (2021). Another paper."
        # When not excluding references
        result = remove_bibliography(text_with_refs, exclude_refs=False)
        # Then references should remain
        self.assertIn("References", result)
        self.assertIn("Smith, J. (2020)", result)
    
    def test_remove_bibliography_when_flag_true(self):
        # Given text with bibliography section
        text_with_refs = "Main content here.\n\nReferences\n1. Smith, J. (2020). Paper.\n2. Doe, A. (2021). Another paper."
        # When excluding references
        result = remove_bibliography(text_with_refs, exclude_refs=True)
        # Then references should be removed
        self.assertNotIn("References", result)
        self.assertNotIn("Smith, J. (2020)", result)
        self.assertEqual(result.strip(), "Main content here.")
    
    def test_remove_bibliography_handles_various_formats(self):
        # Test different bibliography formats
        test_cases = [
            ("DAFTAR PUSTAKA\n1. Reference", "DAFTAR PUSTAKA"),
            ("Bibliography\n[1] Author, Title.", "Bibliography"),
            ("REFERENCES\n- Author et al., Journal, 2020.", "REFERENCES")
        ]
        
        for text, header in test_cases:
            with self.subTest(header=header):
                result = remove_bibliography(text + "\n\nContent after", exclude_refs=True)
                self.assertNotIn(header, result)
                self.assertIn("Content after", result)
```

### Chunker Tests
**File**: `tests/test_chunker.py`

```python
import unittest
from utils.chunker import sentence_tokenize, create_chunks

class TestChunker(unittest.TestCase):
    
    def test_sentence_tokenize_basic(self):
        # Given simple text
        text = "Hello world. How are you? I am fine."
        # When tokenizing
        sentences = sentence_tokenize(text)
        # Then we should get three sentences
        self.assertEqual(len(sentences), 3)
        self.assertEqual(sentences[0], "Hello world.")
        self.assertEqual(sentences[1], "How are you?")
        self.assertEqual(sentences[2], "I am fine.")
    
    def test_sentence_tokenize_handles_abbreviations(self):
        # Given text with abbreviations
        text = "Dr. Smith went to the U.S.A. He saw Mrs. Johnson."
        # When tokenizing
        sentences = sentence_tokenize(text)
        # Then we should get two sentences (not split on abbreviations)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(sentences[0], "Dr. Smith went to the U.S.A.")
        self.assertEqual(sentences[1], "He saw Mrs. Johnson.")
    
    def test_create_chunks_groups_sentences(self):
        # Given list of sentences
        sentences = ["Sentence one.", "Sentence two.", "Sentence three.", "Sentence four."]
        # When creating chunks of size 2
        chunks = create_chunks(sentences, chunk_size=2)
        # Then we should get two chunks
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0], "Sentence one. Sentence two.")
        self.assertEqual(chunks[1], "Sentence three. Sentence four.")
    
    def test_create_chunks_handles_remainder(self):
        # Given 5 sentences and chunk size of 2
        sentences = ["S1.", "S2.", "S3.", "S4.", "S5."]
        # When creating chunks
        chunks = create_chunks(sentences, chunk_size=2)
        # Then we should get 3 chunks (2, 2, 1)
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0], "S1. S2.")
        self.assertEqual(chunks[1], "S3. S4.")
        self.assertEqual(chunks[2], "S5.")
```

### Similarity Tests
**File**: `tests/test_similarity.py`

```python
import unittest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.similarity import compute_similarity, find_best_match

class TestSimilarity(unittest.TestCase):
    
    def test_compute_similarity_identical_texts(self):
        # Given identical texts
        text1 = "The quick brown fox jumps over the lazy dog."
        text2 = "The quick brown fox jumps over the lazy dog."
        # When computing similarity
        similarity = compute_similarity(text1, text2)
        # Then it should be 1.0 (or very close)
        self.assertAlmostEqual(similarity, 1.0, places=5)
    
    def test_compute_similarity_completely_different(self):
        # Given completely different texts
        text1 = "The quick brown fox jumps over the lazy dog."
        text2 = "Quantum computing uses qubits to perform complex calculations."
        # When computing similarity
        similarity = compute_similarity(text1, text2)
        # Then it should be low (but not necessarily 0 due to TF-IDF)
        self.assertLess(similarity, 0.3)
    
    def test_compute_similarity_partial_overlap(self):
        # Given texts with some overlap
        text1 = "The quick brown fox jumps over the lazy dog."
        text2 = "A quick brown animal jumps over a sleeping canine."
        # When computing similarity
        similarity = compute_similarity(text1, text2)
        # Then it should be moderate
        self.assertGreater(similarity, 0.3)
        self.assertLess(similarity, 0.8)
    
    def test_find_best_match_returns_highest(self):
        # Given a chunk and multiple sources
        chunk = "Machine learning algorithms require large datasets for training."
        sources = [
            {"text": "Deep learning models need lots of data to learn effectively.", "title": "Deep Learning Basics"},
            {"text": "Cooking recipes require fresh ingredients and careful preparation.", "title": "Cooking Guide"},
            {"text": "Training machine learning models necessitates substantial amounts of data.", "title": "ML Training Guide"}
        ]
        # When finding best match
        score, best_source = find_best_match(chunk, sources)
        # Then it should return the third source (highest similarity)
        self.assertEqual(best_source["title"], "ML Training Guide")
        self.assertGreater(score, 0.5)  # Should be reasonably high
    
    def test_find_best_match_handles_empty_sources(self):
        # Given a chunk and empty sources list
        chunk = "Some text to match."
        sources = []
        # When finding best match
        score, best_source = find_best_match(chunk, sources)
        # Then it should return zero score and None source
        self.assertEqual(score, 0.0)
        self.assertIsNone(best_source)
```

### Report Generator Tests
**File**: `tests/test_report_generator.py`

```python
import unittest
from utils.report_generator import aggregate_similarities

class TestReportGenerator(unittest.TestCase):
    
    def test_aggregate_similarities_empty_list(self):
        # Given empty chunk results
        chunk_results = []
        # When aggregating
        overall_score, sources = aggregate_similarities(chunk_results)
        # Then score should be 0 and sources empty
        self.assertEqual(overall_score, 0.0)
        self.assertEqual(sources, [])
    
    def test_aggregate_similarities_single_chunk(self):
        # Given one chunk result
        chunk_results = [{
            "chunk": "This is a test chunk.",
            "score": 0.75,
            "source": {
                "title": "Test Source",
                "venue": "Test Journal",
                "year": 2023,
                "similarity": 0.75
            }
        }]
        # When aggregating
        overall_score, sources = aggregate_similarities(chunk_results)
        # Then score should be 75% and one source
        self.assertAlmostEqual(overall_score, 75.0, places=1)
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]["title"], "Test Source")
    
    def test_aggregate_similarities_multiple_chunks_average(self):
        # Given multiple chunk results
        chunk_results = [
            {"chunk": "Chunk 1", "score": 0.8, "source": {"title": "Source A", "similarity": 0.8}},
            {"chunk": "Chunk 2", "score": 0.6, "source": {"title": "Source B", "similarity": 0.6}},
            {"chunk": "Chunk 3", "score": 0.9, "source": {"title": "Source A", "similarity": 0.9}}  # Same source as first
        ]
        # When aggregating
        overall_score, sources = aggregate_similarities(chunk_results)
        # Then score should be average of (0.8, 0.6, 0.9) = 0.7667 -> 76.67%
        self.assertAlmostEqual(overall_score, 76.67, places=1)
        # And we should have 2 unique sources (Source A appears twice but counted once)
        self.assertEqual(len(sources), 2)
        # Source A should have the higher similarity (0.9)
        source_a = next(s for s in sources if s["title"] == "Source A")
        self.assertEqual(source_a["similarity"], 0.9)
    
    def test_aggregate_similarities_sorts_by_similarity_desc(self):
        # Given chunk results with different scores
        chunk_results = [
            {"chunk": "C1", "score": 0.3, "source": {"title": "Low Score", "similarity": 0.3}},
            {"chunk": "C2", "score": 0.9, "source": {"title": "High Score", "similarity": 0.9}},
            {"chunk": "C3", "score": 0.5, "source": {"title": "Medium Score", "similarity": 0.5}}
        ]
        # When aggregating
        _, sources = aggregate_similarities(chunk_results)
        # Then sources should be sorted by similarity descending
        self.assertEqual(sources[0]["title"], "High Score")
        self.assertEqual(sources[1]["title"], "Medium Score")
        self.assertEqual(sources[2]["title"], "Low Score")
```

## 3. Integration Test Scenarios

### Test Scenario 1: End-to-End Original Document
**Steps**:
1. Upload `original_research.pdf` (Test Case 1)
2. Process with bibliography exclusion enabled
3. Expected Results:
   - Similarity percentage: 0-15% (allowing for common phrases)
   - Matched sources: 0-3 low-relevance matches (<0.3 similarity)
   - Processing time: <10 seconds for typical PDF size
   - No false positives on core research content

### Test Scenario 2: End-to-End Light Plagiarism
**Steps**:
1. Upload `light_plagiarism.pdf` (Test Case 2)
2. Process with bibliography exclusion enabled
3. Expected Results:
   - Similarity percentage: 20-35%
   - Matched sources: 2-5 medium-relevance matches (0.3-0.6 similarity)
   - At least one match should be to the original source material
   - Highlighted text should show paraphrased sections

### Test Scenario 3: End-to-End Heavy Plagiarism
**Steps**:
1. Upload `heavy_plagiarism.pdf` (Test Case 4)
2. Process with bibliography exclusion enabled
3. Expected Results:
   - Similarity percentage: 70-85%
   - Matched sources: 1-3 high-relevance matches (>0.6 similarity)
   - Primary match should be to the original source with >0.8 similarity
   - Most of the document should be highlighted

### Test Scenario 4: Bibliography Exclusion Toggle
**Steps**:
1. Upload `heavy_plagiarism.pdf` (Test Case 4)
2. Process twice:
   a. With bibliography exclusion OFF
   b. With bibliography exclusion ON
3. Expected Results:
   - With OFF: Similarity percentage slightly higher (bibliography matches included)
   - With ON: Similarity percentage slightly lower (bibliography excluded)
   - Difference should be 5-15% depending on bibliography size

### Test Scenario 5: Empty/Nearly Empty Document
**Steps**:
1. Upload PDF with only title and author (minimal content)
2. Process normally
3. Expected Results:
   - Similarity percentage: 0-10% (mostly noise/matches to common academic phrases)
   - System should handle gracefully without errors
   - Should indicate insufficient content for meaningful analysis if appropriate

### Test Scenario 6: Very Large Document (Performance)
**Steps**:
1. Generate or obtain PDF with 50+ pages of academic content
2. Process normally
3. Expected Results:
   - Processing time should scale reasonably (<60 seconds for 50 pages)
   - Memory usage should remain stable
   - System should provide progress feedback if implemented
   - No timeouts or crashes

## 4. Edge Case Test Data

### Edge Case 1: PDF with Complex Layout
**Filename**: `complex_layout.pdf`
**Features**:
- Two-column layout
- Mixed English/Indonesian text
- Tables with numerical data
- Figures with captions
- Footnotes and endnotes
**Test**: Verify text extraction maintains readable order (not mixing columns)

### Edge Case 2: PDF with Non-Embedded Fonts
**Filename**: `non_embedded_fonts.pdf`
**Features**:
- Uses standard PDF fonts (Times, Helvetica)
- Some custom fonts not embedded
**Test**: Verify text extraction works despite font substitution

### Edge Case 3: Scanned PDF (Image Only)
**Filename**: `scanned_document.pdf`
**Features**:
- Actual scanned pages (images of text)
- No selectable text layer
**Test**: Verify system handles gracefully (should extract little/no text and report appropriately)

### Edge Case 4: PDF with Special Characters
**Filename**: `special_characters.pdf`
**Features**:
- Mathematical symbols (α, β, ∑, ∫)
- Accented characters (é, ñ, ü)
- Em dashes, en dashes, smart quotes
**Test**: Verify proper Unicode handling in similarity comparison

### Edge Case 5: Very Short Document
**Filename**: `abstract_only.pdf`
**Features**:
- Only contains abstract (100-200 words)
- No introduction, methods, etc.
**Test**: Verify system works with minimal content (may have higher variance in similarity)

### Edge Case 6: Document with Extensive Bibliography
**Filename**: `heavy_bibliography.pdf`
**Features**:
- 5 pages of content
- 15 pages of bibliography (100+ references)
**Test**: Verify bibliography exclusion works effectively and significantly reduces false matches

## 5. Expected Performance Benchmarks

| Document Size | Pages | Expected Processing Time | Notes |
|---------------|-------|--------------------------|-------|
| Small (<500KB) | 1-5 | 2-5 seconds | Typical assignment |
| Medium (500KB-2MB) | 5-20 | 5-15 seconds | Thesis chapter |
| Large (2-5MB) | 20-50 | 15-30 seconds | Full thesis/dissertation |
| Very Large (>5MB) | 50+ | 30-60+ seconds | May require pagination/chunking |

**Memory Usage**:
- Should remain under 256MB for typical documents
- Peak usage during PDF processing and vectorization
- Should release memory after each request

**API Rate Limit Handling**:
- Semantic Scholar: ~100 requests/5 minutes
- With caching: Effective rate can be much higher for repeated phrases
- Fallback: Increase chunk size or reduce API calls when nearing limits

## 6. Accuracy Validation Benchmarks

These are expected ranges based on algorithm design - actual results may vary based on implementation quality:

| Test Case Type | Similarity Range | Precision Target | Recall Target |
|----------------|------------------|------------------|---------------|
| Original Work | 0-15% | >90% (few false positives) | N/A |
| Light Plagiarism | 20-35% | >80% | >75% |
| Moderate Plagiarism | 40-55% | >85% | >80% |
| Heavy Plagiarism | 70-85% | >90% | >85% |
| Complete Plagiarism | 95-100% | >95% | >90% |

**Definitions**:
- Precision: % of flagged content that is actually plagiarized
- Recall: % of actual plagiarized content that is flagged

## 7. Security Test Cases

### Test: File Type Validation
**Steps**:
1. Attempt to upload `.exe` file renamed as `.pdf`
2. Attempt to upload `.pdf` file with malicious script embedded
3. Expected: System should reject non-PDF files and sanitize/validate PDF content

### Test: File Size Limits
**Steps**:
1. Attempt to upload 50MB PDF
2. Expected: System should reject or handle gracefully with appropriate error message

### Test: Path Traversal
**Steps**:
1. Attempt to upload file with path like `../../../etc/passwd` in filename
2. Expected: System should sanitize filename and prevent directory traversal

### Test: XXE (XML External Entity) Protection
**Steps**:
1. Attempt to upload PDF with XXE payload
2. Expected: PDF parser should be configured to prevent XXE attacks

## 8. Usability Test Scenarios

### Test: Clear User Feedback
**Scenarios**:
1. Upload initiated → Show loading indicator
2. Processing → Show progress/status updates
3. Success → Show results clearly with visual hierarchy
4. Error → Show actionable error message

### Test: Mobile Responsiveness
**Checks**:
1. Form usable on small screens
2. Results readable without horizontal scrolling
3. Touch targets adequately sized
4. Load times acceptable on mobile networks

### Test: Accessibility Basics
**Checks**:
1. Form labels associated with inputs
2. Sufficient color contrast
3. Keyboard navigable
4. ARIA labels for dynamic content where appropriate

## 9. Sample Expected Output Format

When the system processes a document successfully, it should return JSON in this format:

```json
{
  "success": true,
  "processing_time_ms": 4520,
  "similarity_percentage": 72.5,
  "matched_sources": [
    {
      "title": "The Impact of Climate Change on Agricultural Productivity in Southeast Asia",
      "authors": ["Dr. Maria Santos", "Prof. John Lee"],
      "venue": "Journal of Agricultural Science",
      "year": 2022,
      "similarity": 0.89,
      "matched_count": 12
    },
    {
      "title": "Climate Adaptation Strategies for Southeast Asian Farmers",
      "authors": ["ASEAN Agricultural Research Center"],
      "venue": "Food Security Journal",
      "year": 2021,
      "similarity": 0.45,
      "matched_count": 3
    }
  ],
  "processed_chunks": 45,
  "high_similarity_chunks": 18,
  "excluded_bibliography": true,
  "highlighted_text": "<p>This study examines the relationship between <mark>climate variability and agricultural productivity</mark> across Southeast Asian nations from 2000 to 2020. Using panel data analysis, we find that <mark>temperature increases beyond optimal thresholds significantly reduce rice and maize yields</mark>, while precipitation changes show mixed effects depending on seasonal timing and irrigation access.</p><p>Climate change poses significant threats to global food security, particularly in developing regions where agriculture remains a primary livelihood source. Southeast Asia, with its <mark>large agrarian populations and vulnerability to climate extremes</mark>, represents a critical region for understanding these dynamics.</p>",
  "error": null
}
```

## 10. Troubleshooting Guide for AI Agents

### Common Issues and Solutions

**Issue**: Low similarity scores for obviously plagiarized content
**Solutions**:
1. Check chunk size - too small may lose context, too large may reduce precision
2. Verify preprocessing is removing headers/footers correctly
3. Confirm API is returning relevant results (check raw responses)
4. Try different similarity threshold for highlighting
5. Consider using bigrams/trigrams in TF-IDF instead of just unigrams

**Issue**: High similarity scores for original content
**Solutions**:
1. Check if bibliography exclusion is working
2. Verify common phrases aren't being flagged (consider increasing threshold)
3. Check if temporary files from previous runs are contaminating results
4. Ensure stop words are being filtered appropriately

**Issue**: API rate limit errors
**Solutions**:
1. Implement response caching (cache by query hash)
2. Increase chunk size to reduce number of queries
3. Add exponential backoff retry mechanism
4. Consider implementing a request queue for batch processing

**Issue**: Poor text extraction from PDF
**Solutions**:
1. Try different PDF libraries (PyMuPDF vs pdfminer vs pdfplumber)
2. Preprocess PDF to remove images/complex elements if only text needed
3. For scanned documents, integrate OCR as fallback (Tesseract)
4. Log extraction issues for difficult PDF formats

**Issue**: Memory leaks or high memory usage
**Solutions**:
1. Explicitly close PDF document objects after extraction
2. Clear large temporary objects after use
3. Consider streaming processing for very large documents
4. Monitor memory usage during testing with tools like memory_profiler

### Debugging Tips for AI Agents
1. **Log intermediate steps**: Save extracted text, chunks, API responses, similarity scores
2. **Use small test cases**: Start with single sentences to isolate issues
3. **Visualize intermediates**: Create debug views showing chunking, matches, etc.
4. **Compare against known baselines**: Use the test cases in this document as reference
5. **Check environment differences**: Ensure dependencies match between dev/test/prod

## 11. Continuous Integration Checklist

Before considering a feature complete, verify:

### Unit Tests
- [ ] All unit tests pass (>90% coverage recommended)
- [ ] Edge cases covered (empty inputs, null values, boundary conditions)
- [ ] Mock external dependencies appropriately

### Integration Tests
- [ ] End-to-end flow works with sample documents
- [ ] API integrations handle success/failure cases
- [ ] Data flows correctly between components

### Manual Testing
- [ ] Test with all sample documents from TEST_CASES.md
- [ ] Verify UI responsiveness and clarity
- [ ] Check error handling and user feedback
- [ ] Validate bibliography exclusion works
- [ ] Test highlighting accuracy

### Performance Testing
- [ ] Verify processing times meet benchmarks
- [ ] Confirm memory usage stays within limits
- [ ] Test with maximum expected file size

### Security Testing
- [ ] Validate file type checking
- [ ] Test file size limits
- [ ] Verify no path traversal vulnerabilities
- [ ] Check for XXE/XXS protection

This comprehensive test suite and sample data should enable AI agents to implement the plagiarism checker with high precision and confidence in correctness.