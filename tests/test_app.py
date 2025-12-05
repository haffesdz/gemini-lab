import pytest
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the app
sys.path.append(str(Path(__file__).parent.parent))

import gemini_chat
import streamlit as st
from unittest.mock import patch, MagicMock

# Test 1: Test if the app initializes correctly
def test_app_initialization():
    """Test that the app initializes with the correct title and session state."""
    with patch('streamlit.title') as mock_title, \
         patch('streamlit.write') as mock_write:
        gemini_chat.main()
        
        # Check if the title was set correctly
        mock_title.assert_called_once()
        args, _ = mock_title.call_args
        assert "Gemini Chat with PDF" in args[0]
        
        # Check if the initial message was written
        assert mock_write.call_count >= 1

# Test 2: Test PDF upload and processing
def test_pdf_processing():
    """Test that PDF files can be uploaded and processed."""
    # Create a mock PDF file
    test_pdf = MagicMock()
    test_pdf.name = "test.pdf"
    test_pdf.getvalue.return_value = b"%PDF-1.4\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/MediaBox[0 0 612 792]/Contents 5 0 R>>\nendobj\n4 0 obj\n<</Type/Font/BaseFont/Helvetica/Subtype/Type1>>\nendobj\n5 0 obj\n<</Length 44>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Hello, World!) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000015 00000 n \n0000000069 00000 n \n0000000122 00000 n \n0000000252 00000 n \n0000000179 00000 n \ntrailer\n<</Size 6/Root 1 0 R>>\nstartxref\n320\n%%EOF"
    
    with patch('streamlit.sidebar.file_uploader', return_value=test_pdf), \
         patch('PyPDF2.PdfReader') as mock_pdf_reader, \
         patch('streamlit.spinner'), \
         patch('streamlit.sidebar.success'):
        
        # Mock the PDF reader
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Test PDF content"
        mock_pdf_reader.return_value.pages = [mock_page]
        
        # Initialize the app
        gemini_chat.main()
        
        # Check if the PDF was processed
        assert 'pdf_content' in st.session_state
        assert st.session_state.pdf_content == "Test PDF content\n"

# Test 3: Test chat message handling
def test_chat_message_handling():
    """Test that chat messages are handled correctly."""
    with patch('streamlit.chat_input', return_value="Hello, AI!"), \
         patch('streamlit.chat_message'), \
         patch('streamlit.markdown'), \
         patch('google.generativeai.GenerativeModel') as mock_model, \
         patch('streamlit.spinner'):
        
        # Mock the model response
        mock_response = MagicMock()
        mock_response.text = "Hello! How can I help you today?"
        mock_model.return_value.generate_content.return_value = mock_response
        
        # Initialize the app
        gemini_chat.main()
        
        # Check if the model was called with the right prompt
        mock_model.return_value.generate_content.assert_called_once()

# Test 4: Test error handling for invalid PDF
def test_invalid_pdf_handling():
    """Test that the app handles invalid PDFs gracefully."""
    test_pdf = MagicMock()
    test_pdf.name = "invalid.pdf"
    test_pdf.getvalue.return_value = b"Not a PDF"
    
    with patch('streamlit.sidebar.file_uploader', return_value=test_pdf), \
         patch('PyPDF2.PdfReader', side_effect=Exception("Invalid PDF")), \
         patch('streamlit.error') as mock_error:
        
        # Initialize the app
        gemini_chat.main()
        
        # Check if the error was handled
        assert mock_error.called
        assert "Error reading PDF" in str(mock_error.call_args[0][0])

# Test 5: Test session state management
def test_session_state_management():
    """Test that the session state is managed correctly."""
    # First test with no messages
    with patch('streamlit.chat_input', return_value=None):
        gemini_chat.main()
        assert 'messages' in st.session_state
        assert len(st.session_state.messages) == 0
    
    # Then test adding a message
    with patch('streamlit.chat_input', return_value="Test message"), \
         patch('streamlit.chat_message'), \
         patch('streamlit.markdown'), \
         patch('google.generativeai.GenerativeModel') as mock_model, \
         patch('streamlit.spinner'):
        
        # Mock the model response
        mock_response = MagicMock()
        mock_response.text = "Test response"
        mock_model.return_value.generate_content.return_value = mock_response
        
        # Initialize the app
        gemini_chat.main()
        
        # Check that the message was added to the session state
        assert len(st.session_state.messages) == 2  # User message + AI response
        assert st.session_state.messages[0]["content"] == "Test message"
        assert st.session_state.messages[1]["content"] == "Test response"
