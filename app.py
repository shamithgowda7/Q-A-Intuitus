import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
from backend.document_loader import save_uploaded_file, extract_text_from_pdf, extract_text_from_html
from backend.rag_pipeline import build_and_persist_vectorstore, load_vectorstore_and_qa
from backend.mindmap_generator import generate_mindmap_outline, generate_study_mindmap
from frontend.components import render_answer
import graphviz

# Load environment variables
load_dotenv()

# Get the API key and configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# Configure Gemini with API key
genai.configure(api_key=api_key)

# Check if API key is properly configured
gemini_configured = True

def plot_mindmap(node):
    """Convert mindmap outline to graphviz visualization"""
    try:
        dot = graphviz.Digraph()
        dot.attr(rankdir='TB')  # Top to bottom layout
        dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue')
        dot.attr('edge', color='gray')
        
        def add_nodes_edges(parent, child, level=0):
            # Create unique node IDs
            parent_id = f"{parent}_{level}"
            child_id = f"{child['topic']}_{level+1}"
            
            # Add child node
            dot.node(child_id, child['topic'])
            
            # Add edge from parent to child
            if level > 0:
                dot.edge(parent_id, child_id)
            
            # Recursively add grandchildren
            for grandchild in child.get("children", []):
                add_nodes_edges(child_id, grandchild, level+1)
        
        # Add root node
        root_id = f"{node['topic']}_0"
        dot.node(root_id, node['topic'])
        
        # Add children
        for child in node.get("children", []):
            add_nodes_edges(root_id, child, 1)
        
        return dot
    except Exception as e:
        st.error(f"Graphviz error: {e}")
        return None

def display_mindmap_text(node, level=0):
    """Display mindmap as hierarchical text when graphviz is not available"""
    indent = "  " * level
    result = f"{indent}📌 {node['topic']}\n"
    
    for child in node.get("children", []):
        result += display_mindmap_text(child, level + 1)
    
    return result

st.set_page_config(page_title="Intuitas AI", layout="wide")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'vectorstore_loaded' not in st.session_state:
    st.session_state.vectorstore_loaded = False
if 'current_document' not in st.session_state:
    st.session_state.current_document = None

# =====================
# CUSTOM CSS
# =====================
dark_css = """
<style>
body {
    background-color: #1e1e1e;
    color: white;
}
</style>
"""

# =====================
# SIDEBAR - Folders & Previous Chats
# =====================
st.sidebar.title("📂 Folders")
st.sidebar.button("➕ New Folder")

with st.sidebar.expander("📁 General (1)", expanded=False):
    st.write("Previous Chats")
    # Placeholder for previous chat items
    st.write("• Chat 1")
    st.write("• Chat 2")

# =====================
# TOP BAR
# =====================
col1, col2, col3 = st.columns([2, 6, 3])

with col1:
    st.markdown("### **Intuitas AI** 🔍 Analyzer")

with col2:
    mode = st.radio(
        "Mode selection",
        ["Study", "Chat", "Summary"],
        horizontal=True,
        label_visibility="collapsed",
    )

with col3:
    dark_mode = st.toggle("🌙 Dark Mode")
    st.button("⚙️ Settings")
    st.button("👤 Profile")

# Apply dark mode
if dark_mode:
    st.markdown(dark_css, unsafe_allow_html=True)

# =====================
# API KEY VALIDATION
# =====================
if not gemini_configured:
    st.error("⚠️ Gemini API Key not configured! Please update your .env file with a valid GEMINI_API_KEY")
    st.stop()
else:
    st.success("✅ Gemini API Key configured")

# =====================
# MAIN CONTENT AREA
# =====================
st.title(f"{mode} Mode")

# --- CHAT MODE ---
if mode == "Chat":
    st.write("General purpose chat + document assistance.")
    
    # Chat interface
    chat_container = st.container()
    
    # Display chat messages
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("💬 Ask me anything..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    if st.session_state.vectorstore_loaded:
                        # Use RAG pipeline if document is loaded
                        qa = load_vectorstore_and_qa(persist_dir="data/processed/vectorstore")
                        answer, sources = qa.run_with_sources(prompt)
                        st.markdown(answer)
                        
                        # Show sources in expander
                        with st.expander("📚 Sources"):
                            for i, source in enumerate(sources):
                                st.write(f"Source {i+1}: {source}")
                    else:
                        # Use direct Gemini for general chat
                        model = genai.GenerativeModel("models/gemini-1.5-flash")
                        response = model.generate_content(prompt)
                        answer = response.text
                        st.markdown(answer)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.session_state.messages.append({"role": "assistant", "content": f"Sorry, I encountered an error: {str(e)}"})

    st.subheader("Tools")
    colA, colB, colC = st.columns(3)
    with colA:
        if st.button("📝 Note Maker"):
            st.info("Note Maker feature coming soon!")
    with colB:
        if st.button("🧩 Clustering"):
            st.info("Clustering feature coming soon!")
    with colC:
        if st.button("🤔 Suggestive Prompts"):
            st.info("Suggestive Prompts feature coming soon!")

# --- STUDY MODE ---
elif mode == "Study":
    st.write("Tools to assist your studies.")
    tab1, tab2, tab3 = st.tabs(["Q&A", "Flashcards", "Mindmaps"])

    with tab1:
        st.subheader("📚 Study Q&A")
        
        if study_question := st.text_area("Ask a Question", placeholder="Enter your study question..."):
            if st.button("Get Answer"):
                with st.spinner("Generating study answer..."):
                    try:
                        model = genai.GenerativeModel("models/gemini-1.5-flash")
                        
                        # Enhanced prompt for study mode
                        study_prompt = f"""
                        You are a helpful study assistant. Please provide a comprehensive, educational answer to this study question:
                        
                        {study_question}
                        
                        Please structure your answer with:
                        1. A clear explanation
                        2. Key points to remember
                        3. Examples if applicable
                        4. Study tips related to this topic
                        
                        Make it educational and easy to understand for learning purposes.
                        """
                        
                        response = model.generate_content(study_prompt)
                        answer = response.text
                        st.markdown("**Study Answer:**")
                        st.markdown(answer)
                        
                    except Exception as e:
                        st.error(f"Error generating answer: {str(e)}")

    with tab2:
        st.text_input("Flashcard Term")
        st.text_area("Definition")
        st.button("Add Flashcard")
        st.write("📚 Flashcards will appear here.")

    with tab3:
        st.text_area("Mindmap Topic", placeholder="Enter main topic...")
        st.button("Generate Mindmap")
        st.write("🧠 Mindmap visualization placeholder")

# --- SUMMARY MODE ---
elif mode == "Summary":
    st.write("Document summarization and analysis tools.")
    tab1, tab2, tab3 = st.tabs(["Document Upload", "Summary Generation", "Key Insights"])

    with tab1:
        st.subheader("📄 Document Upload for Summarization")
        
        # Document upload
        uploaded_file = st.file_uploader("Upload Document for Summarization", type=["pdf", "html", "md", "txt"])
        
        if uploaded_file:
            try:
                # Save uploaded file
                save_path = save_uploaded_file(uploaded_file, dest_folder="data/uploads")
                st.success(f"✅ Document saved: {uploaded_file.name}")
                
                # Extract text based on file type
                if uploaded_file.type == "application/pdf" or uploaded_file.name.endswith('.pdf'):
                    text = extract_text_from_pdf(save_path)
                else:
                    text = extract_text_from_html(save_path)
                
                # Show extracted text preview
                with st.expander("📖 Extracted Text Preview"):
                    st.text_area("Text Content", value=text[:2000] + "..." if len(text) > 2000 else text, height=300)
                
                # Process document button
                if st.button("🔍 Process Document for Summarization"):
                    with st.spinner("Processing document..."):
                        try:
                            # Build vectorstore
                            vs_path = build_and_persist_vectorstore([text], persist_dir="data/processed/vectorstore")
                            st.session_state.vectorstore_loaded = True
                            st.session_state.current_document = uploaded_file.name
                            st.success("✅ Document processed successfully! Ready for summarization.")
                        except Exception as e:
                            st.error(f"Error processing document: {str(e)}")
                
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")

    with tab2:
        st.subheader("📝 Summary Generation")
        
        if st.session_state.vectorstore_loaded and st.session_state.current_document:
            st.write(f"**Document:** {st.session_state.current_document}")
            
            # Summary options
            summary_type = st.selectbox(
                "Choose summary type:",
                ["Executive Summary", "Key Points", "Detailed Summary", "Bullet Points"]
            )
            
            if st.button("📄 Generate Summary"):
                with st.spinner("Generating summary..."):
                    try:
                        model = genai.GenerativeModel("models/gemini-1.5-flash")
                        
                        # Get document content for summarization
                        qa = load_vectorstore_and_qa(persist_dir="data/processed/vectorstore")
                        docs = qa.retriever.invoke("summary")
                        full_text = "\n\n".join([doc.page_content for doc in docs])
                        
                        # Create summary prompt based on type
                        if summary_type == "Executive Summary":
                            prompt = f"Create a concise executive summary of the following document:\n\n{full_text}"
                        elif summary_type == "Key Points":
                            prompt = f"Extract the key points from the following document:\n\n{full_text}"
                        elif summary_type == "Detailed Summary":
                            prompt = f"Create a detailed summary of the following document:\n\n{full_text}"
                        else:  # Bullet Points
                            prompt = f"Summarize the following document in bullet points:\n\n{full_text}"
                        
                        response = model.generate_content(prompt)
                        summary = response.text
                        
                        st.markdown("**Generated Summary:**")
                        st.markdown(summary)
                        
                    except Exception as e:
                        st.error(f"Error generating summary: {str(e)}")
        else:
            st.info("Please upload and process a document first to generate summaries.")

    with tab3:
        st.subheader("🔍 Key Insights")
        
        if st.session_state.vectorstore_loaded and st.session_state.current_document:
            st.write(f"**Document:** {st.session_state.current_document}")
            
            if st.button("💡 Extract Key Insights"):
                with st.spinner("Extracting insights..."):
                    try:
                        model = genai.GenerativeModel("models/gemini-1.5-flash")
                        
                        # Get document content
                        qa = load_vectorstore_and_qa(persist_dir="data/processed/vectorstore")
                        docs = qa.retriever.invoke("insights")
                        full_text = "\n\n".join([doc.page_content for doc in docs])
                        
                        prompt = f"""
                        Analyze the following document and extract key insights, important findings, and notable information:
                        
                        {full_text}
                        
                        Please provide:
                        1. Main themes and topics
                        2. Key findings or conclusions
                        3. Important statistics or data points
                        4. Notable quotes or statements
                        5. Action items or recommendations (if any)
                        """
                        
                        response = model.generate_content(prompt)
                        insights = response.text
                        
                        st.markdown("**Key Insights:**")
                        st.markdown(insights)
                        
                    except Exception as e:
                        st.error(f"Error extracting insights: {str(e)}")
        else:
            st.info("Please upload and process a document first to extract insights.")

# --- STUDY MODE (Additional Study Features) ---
elif mode == "Study":
    st.write("Advanced study tools and learning assistance.")
    tab1, tab2, tab3 = st.tabs(["Study Q&A", "Flashcards", "Mindmaps"])

    with tab1:
        st.subheader("📚 Study Q&A")
        
        if study_question := st.text_area("Ask a Question", placeholder="Enter your study question..."):
            if st.button("Get Answer"):
                with st.spinner("Generating study answer..."):
                    try:
                        model = genai.GenerativeModel("models/gemini-1.5-flash")
                        
                        # Enhanced prompt for study mode
                        study_prompt = f"""
                        You are a helpful study assistant. Please provide a comprehensive, educational answer to this study question:
                        
                        {study_question}
                        
                        Please structure your answer with:
                        1. A clear explanation
                        2. Key points to remember
                        3. Examples if applicable
                        4. Study tips related to this topic
                        
                        Make it educational and easy to understand for learning purposes.
                        """
                        
                        response = model.generate_content(study_prompt)
                        answer = response.text
                        st.markdown("**Study Answer:**")
                        st.markdown(answer)
                        
                    except Exception as e:
                        st.error(f"Error generating answer: {str(e)}")

    with tab2:
        st.subheader("📚 Flashcards")
        st.text_input("Flashcard Term")
        st.text_area("Definition")
        if st.button("Add Flashcard"):
            st.info("Flashcard feature coming soon!")
        st.write("📚 Flashcards will appear here.")

    with tab3:
        st.subheader("🧠 Mindmaps")
        
        if st.session_state.vectorstore_loaded and st.session_state.current_document:
            st.write("Generate a mindmap from your uploaded document:")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("🧠 Generate Document Mindmap", type="primary"):
                    with st.spinner("Generating mindmap from document..."):
                        try:
                            # Get document content
                            qa = load_vectorstore_and_qa(persist_dir="data/processed/vectorstore")
                            docs = qa.retriever.invoke("mindmap")
                            full_text = "\n\n".join([doc.page_content for doc in docs])
                            
                            # Generate mindmap outline
                            outline = generate_mindmap_outline(full_text)
                            
                            # Store in session state
                            st.session_state.mindmap_outline = outline
                            st.success("✅ Mindmap generated successfully!")
                            
                        except Exception as e:
                            st.error(f"Error generating mindmap: {str(e)}")
            
            with col2:
                if st.button("📚 Generate Study Mindmap", type="secondary"):
                    with st.spinner("Generating study-focused mindmap..."):
                        try:
                            # Get document content
                            qa = load_vectorstore_and_qa(persist_dir="data/processed/vectorstore")
                            docs = qa.retriever.invoke("study")
                            full_text = "\n\n".join([doc.page_content for doc in docs])
                            
                            # Generate study mindmap outline
                            outline = generate_study_mindmap(full_text)
                            
                            # Store in session state
                            st.session_state.mindmap_outline = outline
                            st.success("✅ Study mindmap generated successfully!")
                            
                        except Exception as e:
                            st.error(f"Error generating study mindmap: {str(e)}")
            
            # Display mindmap if available
            if 'mindmap_outline' in st.session_state:
                st.subheader("📊 Mindmap Visualization")
                
                # Try to create graphviz mindmap
                mindmap = plot_mindmap(st.session_state.mindmap_outline)
                
                if mindmap is not None:
                    try:
                        # Display graphviz chart
                        st.graphviz_chart(mindmap)
                        st.success("✅ Interactive mindmap displayed above!")
                    except Exception as e:
                        st.warning(f"⚠️ Graphviz rendering failed: {str(e)}")
                        st.info("💡 **Tip:** Install Graphviz software for visual mindmaps. Download from: https://graphviz.org/download/")
                        
                        # Fallback to text display
                        st.subheader("📝 Text-based Mindmap")
                        text_mindmap = display_mindmap_text(st.session_state.mindmap_outline)
                        st.text(text_mindmap)
                else:
                    # Fallback to text display
                    st.subheader("📝 Text-based Mindmap")
                    text_mindmap = display_mindmap_text(st.session_state.mindmap_outline)
                    st.text(text_mindmap)
                    
                    st.info("💡 **Tip:** Install Graphviz software for visual mindmaps. Download from: https://graphviz.org/download/")
                
                # Show raw outline in expander
                with st.expander("📋 View Mindmap Structure (JSON)"):
                    st.json(st.session_state.mindmap_outline)
        else:
            st.info("📄 Please upload and process a document first to generate mindmaps.")
            st.write("""
            **How to use Mindmaps:**
            1. Upload a document in Summary mode
            2. Process the document for summarization
            3. Switch to Study mode
            4. Go to the Mindmaps tab
            5. Click "Generate Document Mindmap" or "Generate Study Mindmap"
            """)

# =====================
# SUGGESTIVE PROMPTS
# =====================
st.subheader("💡 Suggestive Prompts")

# Different suggestions based on mode and document status
if mode == "Summary" and st.session_state.vectorstore_loaded:
    suggestions = [
        "Summarize the main points of this document",
        "What are the key findings?",
        "Generate an executive summary",
        "Extract key insights",
        "Create bullet points"
    ]
elif mode == "Study":
    suggestions = [
        "Explain this concept in simple terms",
        "What are the key points to remember?",
        "Give me examples of this topic",
        "How can I apply this knowledge?",
        "What are common misconceptions?"
    ]
else:  # Chat mode
    suggestions = [
        "Help me understand this topic",
        "What are the main points?",
        "Can you explain this simply?",
        "What should I focus on?",
        "Give me a quick summary"
    ]

# Create columns for suggestions
cols = st.columns(len(suggestions))
for i, suggestion in enumerate(suggestions):
    with cols[i]:
        if st.button(suggestion, key=f"suggestion_{i}"):
            # Add suggestion to chat input
            st.session_state.suggested_prompt = suggestion
            st.rerun()

# Handle suggested prompts
if 'suggested_prompt' in st.session_state:
    if mode == "Chat":
        # Add to chat
        st.session_state.messages.append({"role": "user", "content": st.session_state.suggested_prompt})
        del st.session_state.suggested_prompt
        st.rerun()
    elif mode == "Summary" and st.session_state.vectorstore_loaded:
        # Process with RAG for summarization
        try:
            qa = load_vectorstore_and_qa(persist_dir="data/processed/vectorstore")
            answer, sources = qa.run_with_sources(st.session_state.suggested_prompt)
            st.markdown("**Answer:**")
            st.markdown(answer)
            del st.session_state.suggested_prompt
        except Exception as e:
            st.error(f"Error: {str(e)}")
            del st.session_state.suggested_prompt
    elif mode == "Study":
        # Process with study-focused prompts
        try:
            model = genai.GenerativeModel("models/gemini-1.5-flash")
            study_prompt = f"""
            You are a helpful study assistant. Please provide a comprehensive, educational answer to this study question:
            
            {st.session_state.suggested_prompt}
            
            Please structure your answer with:
            1. A clear explanation
            2. Key points to remember
            3. Examples if applicable
            4. Study tips related to this topic
            
            Make it educational and easy to understand for learning purposes.
            """
            response = model.generate_content(study_prompt)
            st.markdown("**Study Answer:**")
            st.markdown(response.text)
            del st.session_state.suggested_prompt
        except Exception as e:
            st.error(f"Error: {str(e)}")
            del st.session_state.suggested_prompt