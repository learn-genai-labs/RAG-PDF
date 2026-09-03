import hashlib

import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

st.set_page_config(
    page_title="PDF RAG Assistant",
    page_icon="📄",
    layout="centered"
)

st.title("📄 PDF RAG Assistant")

st.write(
    "Upload a PDF document and ask questions based on its contents."
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "processed_file_hash" not in st.session_state:
    st.session_state.processed_file_hash = None


# --------------------------------------------------
# PDF UPLOAD
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload your PDF",
    type=["pdf"]
)


if uploaded_file is not None:

    st.success(f"PDF uploaded successfully: {uploaded_file.name}")

    # Read uploaded file bytes
    file_bytes = uploaded_file.getvalue()

    # Create a unique hash for the actual file contents
    current_file_hash = hashlib.md5(file_bytes).hexdigest()

    # Process only if this exact PDF has not already been processed
    if st.session_state.processed_file_hash != current_file_hash:

        try:
            uploaded_file.seek(0)

            pdf_reader = PdfReader(uploaded_file)

            pdf_text = ""

            for page in pdf_reader.pages:

                page_text = page.extract_text()

                if page_text:
                    pdf_text += page_text + "\n"

            # --------------------------------------------------
            # HANDLE PDF WITH NO READABLE TEXT
            # --------------------------------------------------

            if not pdf_text.strip():

                st.session_state.vectorstore = None
                st.session_state.processed_file_hash = None

                st.error(
                    "No readable text was found in this PDF. "
                    "The PDF may contain scanned images instead of selectable text."
                )

            else:

                st.success("PDF text extracted successfully.")

                st.write(
                    f"Number of pages: {len(pdf_reader.pages)}"
                )

                # --------------------------------------------------
                # TEXT CHUNKING
                # --------------------------------------------------

                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200
                )

                chunks = text_splitter.split_text(pdf_text)

                st.write(
                    f"Number of chunks created: {len(chunks)}"
                )

                # --------------------------------------------------
                # EMBEDDINGS
                # --------------------------------------------------

                embeddings = OpenAIEmbeddings(
                    model="text-embedding-3-small"
                )

                # --------------------------------------------------
                # FAISS VECTOR DATABASE
                # --------------------------------------------------

                with st.spinner(
                    "Creating embeddings and building FAISS database..."
                ):

                    vectorstore = FAISS.from_texts(
                        texts=chunks,
                        embedding=embeddings
                    )

                # Save FAISS and PDF identity
                st.session_state.vectorstore = vectorstore
                st.session_state.processed_file_hash = current_file_hash

                st.success(
                    "FAISS vector database is ready."
                )

        except Exception as e:

            st.session_state.vectorstore = None
            st.session_state.processed_file_hash = None

            st.error(
                f"Unable to process the PDF: {e}"
            )

    else:

        st.success(
            "FAISS vector database is already ready for this PDF."
        )


# --------------------------------------------------
# QUESTION / RAG SECTION
# --------------------------------------------------

if (
    uploaded_file is not None
    and st.session_state.vectorstore is not None
):

    st.divider()

    st.subheader("Ask a question")

    question = st.text_input(
        "Enter a question about your PDF"
    )

    if question:

        # --------------------------------------------------
        # RETRIEVER
        # --------------------------------------------------

        retriever = st.session_state.vectorstore.as_retriever(
            search_kwargs={"k": 5}
        )

        with st.spinner("Searching the PDF..."):

            retrieved_docs = retriever.invoke(question)

        # Combine retrieved chunks into context
        context = "\n\n".join(
            doc.page_content for doc in retrieved_docs
        )

        # --------------------------------------------------
        # OPENAI CHAT MODEL
        # --------------------------------------------------

        llm = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0
        )

        # --------------------------------------------------
        # GROUNDED RAG PROMPT
        # --------------------------------------------------

        prompt = ChatPromptTemplate.from_template(
            """
You are a helpful assistant answering questions
about an uploaded PDF.

Use only the context provided below to answer
the user's question.

If the answer is not present in the context, say:
"I could not find that information in the uploaded PDF."

Do not invent or assume information.

Context:
{context}

Question:
{question}

Answer:
"""
        )

        chain = prompt | llm

        # --------------------------------------------------
        # GENERATE ANSWER
        # --------------------------------------------------

        with st.spinner(
            "Generating answer..."
        ):

            response = chain.invoke(
                {
                    "context": context,
                    "question": question
                }
            )

        # --------------------------------------------------
        # DISPLAY ANSWER
        # --------------------------------------------------

        st.subheader("Answer")

        st.write(response.content)

        # --------------------------------------------------
        # OPTIONAL RETRIEVAL VIEW
        # --------------------------------------------------

        with st.expander(
            "View retrieved PDF chunks"
        ):

            for i, doc in enumerate(
                retrieved_docs,
                start=1
            ):

                st.markdown(
                    f"### Chunk {i}"
                )

                st.write(
                    doc.page_content
                )


elif uploaded_file is None:

    st.info(
        "Please upload a PDF to begin."
    )