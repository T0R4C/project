# API Response Samples for Plagiarism Checker

This document contains sample responses from academic APIs that the plagiarism checker integrates with. These samples help AI agents understand the expected data structure when implementing API integrations.

## 1. Semantic Scholar API Response Sample

### Endpoint
```
GET https://api.semanticscholar.org/graph/v1/paper/search
```

### Query Parameters
```
?query=machine learning algorithms&limit=3&fields=title,abstract,venue,year,citationCount,authors
```

### Successful Response (HTTP 200)
```json
{
  "total": 125430,
  "offset": 0,
  "data": [
    {
      "paperId": "649def34f8be52c8b66281af98ae884c09aef38b",
      "title": "A Few Useful Things to Know about Machine Learning",
      "venue": "Communications of the ACM",
      "year": 2012,
      "citationCount": 10457,
      "abstract": "Machine learning systems are rapidly becoming an integral part of modern life. From web search to content filtering on social networks, recommendations of products and friends, to diagnosing diseases and predicting stock market trends, machine learning algorithms are being used to make decisions that impact our daily lives. This article presents twelve key lessons that machine learning researchers and practitioners should know. These lessons include pitfalls to avoid, important issues to focus on, and answers to common questions.",
      "authors": [
        {
          "authorId": "1863554",
          "name": "Pedro Domingos"
        }
      ]
    },
    {
      "paperId": "1598619111b2b4250ea8e54543f2624c8b7d35f4",
      "title": "Deep Learning",
      "venue": "Nature",
      "year": 2015,
      "citationCount": 41082,
      "abstract": "Deep learning allows computational models that are composed of multiple processing layers to learn representations of data with multiple levels of abstraction. These methods have dramatically improved the state-of-the-art in speech recognition, visual object recognition, object detection and many other domains such as drug discovery and genomics. Deep learning discovers intricate structure in large data sets by using the backpropagation algorithm to indicate how a machine should change its internal parameters that are used to compute the representation in each layer from the representation in the previous layer. We summarize recent advances in deep learning.",
      "authors": [
        {
          "authorId": "1787901",
          "name": "Yoshua Bengio"
        },
        {
          "authorId": "1572788",
          "name": "Yann LeCun"
        },
        {
          "authorId": "194940",
          "name": "Geoffrey Hinton"
        }
      ]
    },
    {
      "paperId": "941e6d25a7f3b8c9c3b1a6f7e8d9c0b1a2f3e4d5",
      "title": "Understanding the Difficulty of Training Deep Feedforward Neural Networks",
      "venue": "International Conference on Artificial Intelligence and Statistics",
      "year": 2010,
      "citationCount": 8765,
      "abstract": "Training deep neural networks is difficult due to the vanishing/exploding gradient problem. We propose a simple initialization scheme that addresses this issue and leads to much faster convergence. Our initialization draws weights from a Gaussian distribution with zero mean and a variance that depends on the number of fan-in and fan-out connections in each layer.",
      "authors": [
        {
          "authorId": "1234567",
          "name": "Xavier Glorot"
        },
        {
          "authorId": "2345678",
          "name": "Yoshua Bengio"
        }
      ]
    }
  ],
  "next": null
}
```

### Error Responses

#### Rate Limit Exceeded (HTTP 429)
```json
{
  "error": {
    "code": 429,
    "message": "Rate limit exceeded. Please try again later.",
    "type": "TooManyRequestsError"
  }
}
```

#### Invalid Request (HTTP 400)
```json
{
  "error": {
    "code": 400,
    "message": "Missing required parameter: query",
    "type": "BadRequestError"
  }
}
```

#### Server Error (HTTP 500)
```json
{
  "error": {
    "code": 500,
    "message": "Internal server error",
    "type": "InternalServerError"
  }
}
```

## 2. Sinta API Response Sample (Indonesian)

*Note: Sinta API documentation is limited; this is based on typical Indonesian government academic portal APIs*

### Endpoint (Hypothetical)
```
GET https://sinta.kemdikbud.go.id/api/v1/search
```

### Query Parameters
```
?query=teknologi pendidikan&limit=5
```

### Successful Response (HTTP 200)
```json
{
  "status": "success",
  "data": {
    "total_results": 842,
    "items": [
      {
        "id": "SINTA000123456",
        "title": "Integrasi Teknologi Informasi dalam Pembelajaran di Sekolah Dasar",
        "authors": [
          "Dr. Budi Santoso, M.Pd.",
          "Dra. Ana Widiasih, M.Pd."
        ],
        "journal": "Jurnal Pendidikan Dasar",
        "volume": "15",
        "issue": "2",
        "pages": "145-160",
        "year": "2023",
        "abstract": "Penelitian ini bertujuan untuk menganalisis efektivitas integrasi teknologi informasi dalam proses pembelajaran di sekolah dasar. Metode penelitian menggunakan pendekatan kuantitatif dengan desain eksperimen...",
        "doi": "10.1234/jpd.2023.15.2.145",
        "url": "https://jurnal.kemdikbud.go.id/index.php/JPD/article/view/12345"
      },
      {
        "id": "SINTA000234567",
        "title": "Penggunaan Media Pembelajaran Berbasis Android untuk Meningkatkan Minat Belajar Siswa SMA",
        "authors": [
          "Prof. Dr. Citra Dewi, M.Kom."
        ],
        "journal": "Jurnal Teknologi Pendidikan",
        "volume": "8",
        "issue": "1",
        "pages": "33-48",
        "year": "2022",
        "abstract": "Studi ini mengembangkan media pembelajaran berbasis Android untuk mata pelajaran Matematika di tingkat Sekolah Menengah Atas. Hasil pengujian menunjukkan bahwa media yang dikembangkan berhasil meningkatkan minat belajar siswa...",
        "issn": "2089-XXXX",
        "url": "https://jurnal.kemdikbud.go.id/index.php/JTP/article/view/23456"
      }
    ]
  },
  "message": "Data retrieved successfully"
}
```

### Error Responses

#### Not Found (HTTP 404)
```json
{
  "status": "error",
  "message": "No results found for the given query",
  "data": null
}
```

#### Service Unavailable (HTTP 503)
```json
{
  "status": "error",
  "message": "Service temporarily unavailable. Please try again later.",
  "data": null
}
```

## 3. Garuda API Response Sample (Indonesian)

*Note: Based on Garuda Portal (Garuda Rujukan Digital) API patterns*

### Endpoint (Hypothetical)
```
GET https://garuda.kemdikbud.go.id/api/v1/articles/search
```

### Query Parameters
```
?keyword=artificial intelligence&limit=4
```

### Successful Response (HTTP 200)
```json
{
  "status": "ok",
  "result": [
    {
      "id": "GARUDA000987654",
      "title": "Ethical Considerations in Artificial Intelligence for Healthcare Applications",
      "author": "Dr. Rina Marlina, Sp.M(K)",
      "affiliation": "Universitas Indonesia",
      "publication_name": "Jurnal Kedokteran dan Farmasi Indonesia",
      "publication_year": "2023",
      "volume": "10",
      "number": "1",
      "pages": "78-92",
      "abstract": "The rapid development of artificial intelligence (AI) in healthcare brings significant benefits but also raises ethical concerns. This paper discusses key ethical issues including privacy, bias, accountability, and transparency in AI healthcare applications...",
      "language": "English",
      "access_type": "open_access",
      "download_url": "https://garuda.kemdikbud.go.id/article/download/GARUDA000987654.pdf",
      "doi": "10.1234/jkfi.2023.10.1.78"
    },
    {
      "id": "GARUDA000876543",
      "title": "Analisis Sentimen Terhadap Kebijakan Publik Menggunakan Algoritma Machine Learning",
      "author": "Tim Pengembang: Ahmad Fauzi, S.Kom., M.Kom.",
      "affiliation": "Institut Teknologi Bandung",
      "publication_name": "Jurnal Informatika",
      "publication_year": "2022",
      "volume": "12",
      "number": "3",
      "pages": "201-215",
      "abstract": "Penelitian ini membandingkan kinerja berbagai algoritma machine learning dalam tugas analisis sentimen terhadap kebijakan publik dari data media sosial. Algoritma yang dievaluasi meliputi Naive Bayes, Support Vector Machine, Random Forest, dan Neural Network...",
      "language": "Indonesian",
      "access_type": "open_access",
      "download_url": "https://garuda.kemdikbud.go.id/article/download/GARUDA000876543.pdf"
    }
  ],
  "total": 56,
  "message": "Success"
}
```

## 4. Expected Internal Data Structures

### Academic Source Object (Used Internally)
```javascript
{
  "paperId": "string",           // Unique identifier (Semantic Scholar) or local ID
  "title": "string",             // Paper/article title
  "authors": ["string"],         // Array of author names
  "venue": "string",             // Journal/conference name
  "year": "number",              // Publication year
  "abstract": "string",          // Abstract text
  "citationCount": "number",     // Number of citations (optional)
  "url": "string",               // Link to full text (if available)
  "doi": "string",               // DOI identifier (optional)
  "similarity": "number"         // Similarity score with input chunk (0-1)
}
```

### Chunk Result Object
```javascript
{
  "chunk": "string",             // Text chunk from input document
  "score": "number",             // Similarity score (0-1)
  "source": { /* Academic Source Object */ },
  "position": {                  // Position in original text (for highlighting)
    start: "number", 
                                 //   end: "number"
  }
}
```

### Final Report Object
```javascript
{
  "similarity_percentage": "number",  // Overall similarity (0-100)
  "matched_sources": [                // Unique sources sorted by similarity
    {
      "title": "string",
      "authors": ["string"],
      "venue": "string",
      "year": "number",
      "similarity": "number"          // Highest similarity score from this source
    }
  ],
  "processed_chunks": "number",       // Total chunks analyzed
  "high_similarity_chunks": "number", // Chunks above threshold (e.g., >0.7)
  "processing_time_ms": "number",     // Time taken for analysis
  "excluded_bibliography": "boolean"  // Whether bibliography was excluded
}
```

## 5. API Integration Notes for AI Agents

### Semantic Scholar Specifics
- **Base URL**: `https://api.semanticscholar.org/graph/v1`
- **Rate Limits**: ~100 requests per 5 minutes for free tier
- **Authentication**: No API key required for basic search (but recommended for higher limits)
- **Recommended Fields**: `title,abstract,venue,year,citationCount,authors,url,doi`
- **Query Best Practices**:
  - Use chunks of 2-4 sentences (not single words or very long paragraphs)
  - Remove special characters and extra whitespace
  - Consider removing stop words for very common terms
- **Caching Strategy**: Cache responses by query hash for 10-30 minutes

### Error Handling Patterns
1. **Network Errors**: Retry with exponential backoff (max 3 attempts)
2. **Rate Limits (429)**: Show user-friendly message, suggest trying again later
3. **Empty Results**: Try broader query or reduce specificity
4. **Malformed Responses**: Validate JSON structure before processing
5. **Timeouts**: Set reasonable timeout (10-15 seconds), show loading state

### Data Validation Requirements
- Always check for null/undefined fields before accessing
- Sanitize HTML if displaying abstracts/titles in UI (though we're using similarity scores)
- Validate year is reasonable (e.g., 1900-2030)
- Ensure similarity scores are floats between 0 and 1
- Deduplicate sources by paperId before displaying results

These samples should provide AI agents with concrete examples to implement robust API integrations that handle various response formats and error conditions gracefully.