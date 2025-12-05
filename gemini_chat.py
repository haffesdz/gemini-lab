import streamlit as st
import google.generativeai as genai
import PyPDF2
import io
from typing import List, Optional

# Configure the Gemini API with your API key
GEMINI_API_KEY = "AIzaSyBU1dEUZy75TIi-0BdcR0GwIZcYvEvTGIM"
genai.configure(api_key=GEMINI_API_KEY)

def extract_text_from_pdf(uploaded_file) -> Optional[str]:
    """Extract text from an uploaded PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

def main():
    st.title("💬 Gemini Chat with PDF")
    st.write("Upload a PDF and chat with Google's Gemini AI about its content")
    
    # Initialize session state for PDF content if it doesn't exist
    if "pdf_content" not in st.session_state:
        st.session_state.pdf_content = None
    
    # File uploader
    uploaded_file = st.sidebar.file_uploader("Upload a PDF file", type=["pdf"])
    
    # Process uploaded PDF
    if uploaded_file is not None:
        with st.spinner("Reading PDF..."):
            st.session_state.pdf_content = extract_text_from_pdf(uploaded_file)
            if st.session_state.pdf_content:
                st.sidebar.success("PDF processed successfully!")
                # Show a preview of the first 500 characters
                st.sidebar.caption("PDF Preview:")
                st.sidebar.text(st.session_state.pdf_content[:500] + "..." if len(st.session_state.pdf_content) > 500 else st.session_state.pdf_content)
    elif st.session_state.pdf_content is None:
        st.sidebar.info("Upload a PDF to chat about its content")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What would you like to know?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Initialize the Gemini model
                    model = genai.GenerativeModel('models/gemini-2.5-flash-lite')
                    
                    # Prepare the prompt with PDF context if available
                    full_prompt = prompt
                    if st.session_state.pdf_content:
                        full_prompt = f"Context from PDF:\n{st.session_state.pdf_content[:15000]}\n\nQuestion: {prompt}"
                    
                    # Generate response
                    response = model.generate_content(full_prompt)
                    
                    # Display the response
                    st.markdown(response.text)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
