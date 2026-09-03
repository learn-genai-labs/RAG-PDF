# RAG PDF Assistant – Learning Mind Map

This presentation summarizes the RAG PDF Assistant built using **Python, LangChain, Streamlit, OpenAI, FAISS, and LangSmith**.

The 8 slides explain the complete RAG flow from uploading a PDF to retrieving relevant information and generating a grounded answer.


---

RAG PDF Assistant: Learning Mind Map

### Purpose
Provides a high-level overview of all the major components used in the RAG application.

### Concepts Covered
- PDF / Data Ingestion
- Streamlit
- Chunking
- Embeddings
- FAISS
- Retriever
- GPT-4.1-mini
- LangSmith
- LangChain

![Alt text](https://github.com/learn-genai-labs/RAG-PDF/blob/ad215a1bfd1ac685f7bbc36f1518b236190484cc/Assets/RAG_Components.png)

### What It Explains
RAG stands for **Retrieval-Augmented Generation**.

Instead of sending the entire PDF directly to the AI model, the application first retrieves the most relevant information from the PDF and then gives that information to the AI model to generate an answer.

### Easy Understanding
**RAG = Retrieve the right information first → Generate the answer second**

---

## The Big Picture

### Purpose
Explains the complete end-to-end RAG pipeline and separates it into two major phases.

![Alt text](https://github.com/learn-genai-labs/RAG-PDF/blob/ad215a1bfd1ac685f7bbc36f1518b236190484cc/Assets/Big_Picture.png)

### Phase 1 – Indexing

When the PDF is uploaded:

PDF → Extract Text → Chunk → Embed → FAISS

The purpose of this phase is to prepare the PDF so that its contents can be searched by meaning.

### Phase 2 – Question Answering

When the user asks a question:

Question → Question Embedding → FAISS → Retrieve Relevant Chunks → Context + Question → GPT-4.1-mini → Answer

### Key Learning
RAG does not normally send the complete document to the LLM.

It retrieves only the most relevant sections and gives those sections to the LLM as context.

---

## Operation #1: Embed the PDF

### Purpose
Explains what happens when the user uploads a PDF.

### Flow

PDF  
↓  
PyPDF extracts text  
↓  
LangChain splits the text into chunks  
↓  
OpenAI Embedding Model converts chunks into vectors  
↓  
FAISS stores/searches the vectors

![Alt text](https://github.com/learn-genai-labs/RAG-PDF/blob/ad215a1bfd1ac685f7bbc36f1518b236190484cc/Assets/Operation1_Embed_pdf.png)

### Embedding Model Used

`text-embedding-3-small`

### What Is an Embedding?
An embedding converts the meaning of text into a numerical vector.

Example:

Text:

`Step 2 - Create a virtual environment`

Conceptually becomes:

`[0.21, -0.48, 0.73, ...]`

The actual vector contains many numerical values.

### Why Is This Required?
FAISS performs similarity search using vectors rather than directly understanding normal English text.

LangChain also maintains the relationship between the vector and its original chunk text.

### Key Learning
**Operation #1 prepares the PDF knowledge for semantic search.**

---

## Operation #2: Embed the User Question

### Purpose
Explains what happens when the user asks a question.

Example question:

`What does Step 2 say?`

The question is also sent to the same OpenAI embedding model:

Question  
↓  
`text-embedding-3-small`  
↓  
Question Vector

FAISS then compares the question vector against the stored PDF chunk vectors.

### Example

FAISS may conceptually find:

- Chunk 1 → low similarity
- Chunk 2 → very high similarity
- Chunk 3 → medium similarity
- Chunk 4 → low similarity

The most similar chunks are selected.

In our application:

`k = 5`

means that the retriever requests the **top 5 relevant chunks**.

### Key Learning
The PDF chunks and the user question are embedded using the same embedding model so that their semantic meanings can be compared.

**Operation #2 finds the knowledge required to answer the user's question.**

---

## How GPT-4.1 Receives the Right Information

### Purpose
Explains the connection between FAISS retrieval and GPT-4.1-mini.

This is the most important RAG relationship.

### Flow

FAISS  
↓  
Relevant vectors identified  
↓  
LangChain Retriever  
↓  
Original PDF chunk text  
↓  
Context  
+  
Original User Question  
↓  
Prompt  
↓  
GPT-4.1-mini  
↓  
Final Answer

### Important Concept
GPT-4.1-mini does **not receive the vectors**.

Vectors are used only for finding the relevant information.

Once FAISS identifies the relevant vectors, the LangChain vector store/retriever returns the original text associated with those vectors.

Our Python code combines this retrieved text into:

`context`

The prompt then contains:

- Instructions
- Retrieved PDF context
- Original user question

GPT-4.1-mini reads this text and generates the final answer.

### Easy Memory

**FAISS finds → Retriever fetches → Prompt carries → GPT answers**

---

## Why OpenAI Is Used Twice

### Purpose
Explains why the RAG application needs both an OpenAI embedding model and an OpenAI chat model.

Both are accessed using the same:

`OPENAI_API_KEY`

but they perform completely different jobs.

### OpenAI Embedding Model

Model:

`text-embedding-3-small`

Purpose:

**SEARCH**

It is used for:

1. Converting PDF chunks into vectors.
2. Converting each user question into a vector.

These vectors allow FAISS to perform semantic similarity search.

### OpenAI Chat Model

Model:

`gpt-4.1-mini`

Purpose:

**ANSWER GENERATION**

It receives:

Retrieved PDF Context  
+  
Original User Question  
+  
Prompt Instructions

and generates a natural-language answer.

### Key Difference

| Embedding Model | Chat Model |
|---|---|
| Text → Numbers | Text → Answer |
| Used for search | Used for generation |
| Helps FAISS find information | Explains retrieved information |
| `text-embedding-3-small` | `gpt-4.1-mini` |

### Key Learning

**Embedding model = Find the information**

**GPT-4.1-mini = Explain the information**

The `OPENAI_API_KEY` is the credential that allows the application to access both OpenAI services.

---

## Supporting Concepts

### Purpose
Explains the additional components required to make the RAG application usable, secure, efficient, and observable.

### Streamlit
Provides the browser-based user interface.

Used for:
- PDF upload
- Processing status
- Question input
- Answer display
- Retrieved chunk display

### PyPDF
Reads the uploaded PDF and extracts readable text.

### LangChain
Connects and orchestrates the RAG components:

Text Splitter → Embeddings → FAISS → Retriever → Prompt → LLM

### Session State
Stores the prepared FAISS vector store during the Streamlit session.

This prevents the PDF embeddings and FAISS database from being unnecessarily rebuilt every time the user interacts with the app.

### File Hash
Creates a fingerprint of the uploaded PDF contents.

This helps distinguish between two different PDFs even if they have the same filename.

### `.env` and `.gitignore`
Keep API keys outside the Python source code and prevent secrets from being committed to GitHub.

### LangSmith
Provides tracing and observability.

It helps inspect:
- Inputs
- Outputs
- Model calls
- Execution flow
- Timing

This is useful when debugging incorrect or unexpected RAG answers.

### No-Readable-Text Check
If PyPDF cannot extract text, the application stops processing and informs the user instead of attempting to create embeddings from empty content.

---

## Final Memory Map

### Purpose
Summarizes the entire RAG application in one easy-to-remember flow.

### Complete Flow

📄 READ  
↓  
✂️ CHUNK  
↓  
🔢 EMBED  
↓  
🗄️ STORE  
↓  
🔎 RETRIEVE  
↓  
🤖 ANSWER  
↓  
👀 TRACE

### Phase 1 – Prepare Knowledge

PDF → Extract → Chunk → Embed → FAISS

This happens when the PDF is uploaded.

### Phase 2 – Find and Explain Knowledge

User Question  
↓  
Question Embedding  
↓  
FAISS Search  
↓  
Retriever  
↓  
Relevant Original PDF Chunks  
↓  
Context + Original Question  
↓  
GPT-4.1-mini  
↓  
Answer

### Final RAG Understanding

**Operation #1 = Prepare the knowledge**

PDF chunks are converted into embeddings and indexed in FAISS.

**Operation #2 = Find the knowledge**

The user's question is converted into an embedding and FAISS identifies the most relevant PDF chunks.

**Operation #3 = Explain the knowledge**

The retrieved original chunk text becomes the context. The context and original user question are placed into the prompt and sent to GPT-4.1-mini to generate the final answer.

---

# Key Takeaways

1. **RAG = Retrieve first, Generate second.**
2. **Embeddings convert meaning into vectors for semantic search.**
3. **FAISS finds the vectors most relevant to the user's question.**
4. **The Retriever returns the original text associated with those vectors.**
5. **GPT-4.1-mini receives text, not vectors.**
6. **Context = relevant PDF text retrieved from FAISS.**
7. **Original Question = the actual question typed by the user.**
8. **Context + Original Question + Instructions form the prompt sent to GPT-4.1-mini.**
9. **LangChain connects the RAG components, while LangSmith traces their execution.**
10. **The OpenAI Embedding Model performs the search-related representation; the OpenAI Chat Model generates the final answer.**

## Easy Memory Line

**PDF → Numbers → Store → Question → Numbers → Find Text → Context + Question → GPT → Answer**

Or:

**Prepare Knowledge → Find Knowledge → Explain Knowledge**
