from fpdf import FPDF
import streamlit as st

# Initialize conversation as a session state variable
if "conversation" not in st.session_state:
    st.session_state.conversation = []

def export_to_pdf(conversation):
    """Export conversation to downloadable PDF"""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for idx, conv in enumerate(conversation):
        pdf.multi_cell(0, 10, f"Q{idx + 1}: {conv['question']}")
        pdf.multi_cell(0, 10, f"A{idx + 1}: {conv['answer']}")
        pdf.ln()

    # Correct: Get PDF output as bytes
    pdf_output = pdf.output(dest='S').encode('latin1')

    # Streamlit download button
    st.download_button(
        label="📄 Download Q&A PDF",
        data=pdf_output,
        file_name="qa_conversation.pdf",
        mime="application/pdf"
    )

def export_to_text(conversation):
    """Export conversation to downloadable text file"""
    text_content = ""
    for idx, conv in enumerate(conversation):
        text_content += f"Q{idx + 1}: {conv['question']}\n"
        text_content += f"A{idx + 1}: {conv['answer']}\n\n"

    st.download_button(
        label="📝 Download Q&A Text",
        data=text_content,
        file_name="qa_conversation.txt",
        mime="text/plain"
    )

# Handle new question and answer input
question = st.text_input("Ask a question:")
answer = st.text_input("Provide an answer:")

if st.button("Add Conversation"):
    if question and answer:
        st.session_state.conversation.append({
            "question": question,
            "answer": answer
        })
        st.success("Conversation added!")

# Example: Export buttons
export_to_pdf(st.session_state.conversation)
export_to_text(st.session_state.conversation)

# Optionally clear the conversation after export (if needed)
if st.button("Clear Conversation"):
    st.session_state.conversation = []
