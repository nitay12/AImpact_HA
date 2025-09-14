"""
Gradio Chat Interface for Regulatory RAG System.
Hebrew-aware chatbot for Israeli business regulatory compliance.
Now with conversational business information gathering.
"""

import gradio as gr
import os
import json
from typing import List, Dict, Any, Tuple, Optional
from dotenv import load_dotenv
from rag_system import RegulatoryRAGSystem
from generator import RegulatoryGenerator
from data_processor import RegulatoryDataProcessor
from business_profiler import BusinessProfiler

# Load environment variables
load_dotenv()


class RegulatoryChat:
    """Main chat application for regulatory compliance assistance."""

    def __init__(self):
        self.rag_system = RegulatoryRAGSystem()
        self.generator = RegulatoryGenerator()
        self.conversation_history = []
        self.business_profiler = BusinessProfiler()
        self.session_started = False

        # Initialize system
        self._initialize_system()

    def _initialize_system(self):
        """Initialize the RAG system and load/build index."""
        try:
            # Try to load existing index
            if not self.rag_system.load_index():
                # Build index if not found
                data_file = "data.json"
                if os.path.exists(data_file):
                    print("Building RAG index from data.json...")
                    self.rag_system.build_index(data_file)
                else:
                    raise FileNotFoundError(f"Data file {data_file} not found")

            print("RAG system initialized successfully!")

        except Exception as e:
            print(f"Error initializing system: {e}")
            raise

    def chat(
        self,
        message: str,
        history: List[List[str]]
    ) -> Tuple[str, List[List[str]]]:
        """
        Main chat function with conversational business profiling.

        Args:
            message: User message
            history: Chat history from Gradio

        Returns:
            Tuple of (response, updated_history)
        """
        if not message.strip():
            return "", history

        # Handle first interaction - send welcome message
        if not self.session_started:
            self.session_started = True
            welcome_msg = self.business_profiler.generate_welcome_message()
            first_question = self.business_profiler.get_next_question()
            full_response = f"{welcome_msg}\n\n{first_question}"
            history.append([message, full_response])
            return "", history

        try:
            # Extract business information from user message
            extracted_info = self.business_profiler.update_business_info(message)

            # Check if we need more information
            if not self.business_profiler.business_info.is_complete:
                next_question = self.business_profiler.get_next_question()

                if extracted_info:
                    # Acknowledge what was extracted
                    ack_parts = []
                    if "business_type" in extracted_info:
                        ack_parts.append(f"✓ סוג עסק: {extracted_info['business_type']}")
                    if "seating_capacity" in extracted_info:
                        ack_parts.append(f"✓ מקומות ישיבה: {extracted_info['seating_capacity']}")
                    if "size_sqm" in extracted_info:
                        ack_parts.append(f"✓ שטח: {extracted_info['size_sqm']} מ\"ר")

                    acknowledgment = "תודה! הבנתי:\n" + "\n".join(ack_parts)

                    if next_question:
                        response = f"{acknowledgment}\n\n{next_question}"
                    else:
                        response = f"{acknowledgment}\n\n{self.business_profiler.generate_summary_message()}"
                else:
                    # Didn't extract info, ask again or provide help
                    missing = self.business_profiler.get_missing_info_summary()
                    if next_question:
                        response = f"לא הצלחתי להבין את המידע. {next_question}"
                    else:
                        response = f"אני עדיין צריך לדעת: {', '.join(missing)}"

                history.append([message, response])
                return "", history

            else:
                # Business profile is complete - handle regulatory queries
                business_profile = self.business_profiler.get_business_profile_dict()

                # Check if this is the first complete profile message
                if extracted_info and not any("מעולה! אספתי את המידע" in msg[1] for msg in history):
                    summary_response = self.business_profiler.generate_summary_message()
                    history.append([message, summary_response])
                    return "", history

                # Handle regulatory queries
                results = self.rag_system.hybrid_search(
                    query=message,
                    business_profile=business_profile,
                    k=5
                )

                # Convert Gradio history to OpenAI format
                openai_history = []
                for user_msg, assistant_msg in history:
                    openai_history.extend([
                        {"role": "user", "content": user_msg},
                        {"role": "assistant", "content": assistant_msg}
                    ])

                # Generate response
                response = self.generator.generate_response(
                    query=message,
                    retrieved_chunks=results,
                    business_profile=business_profile,
                    conversation_history=openai_history
                )

                history.append([message, response])
                return "", history

        except Exception as e:
            error_msg = f"מצטער, אירעה שגיאה: {str(e)}"
            history.append([message, error_msg])
            return "", history

    def generate_compliance_report(self) -> str:
        """Generate a comprehensive compliance report based on collected business profile."""
        if not self.business_profiler.business_info.is_complete:
            missing = self.business_profiler.get_missing_info_summary()
            return f"לא ניתן ליצור דוח - חסרים פרטים: {', '.join(missing)}\n\nאנא השלם את המידע בשיחה תחילה."

        business_profile = self.business_profiler.get_business_profile_dict()

        try:
            # Get all applicable regulations
            processor = RegulatoryDataProcessor("")
            processor.chunks = self.rag_system.chunks

            applicable_regulations = processor.get_applicable_regulations(business_profile)

            # Generate report
            report = self.generator.generate_compliance_report(
                business_profile, applicable_regulations
            )

            return report

        except Exception as e:
            return f"מצטער, אירעה שגיאה ביצירת הדוח: {str(e)}"

    def upload_new_data(self, file) -> str:
        """Handle new regulatory data upload."""
        if file is None:
            return "לא נבחר קובץ"

        try:
            # Read uploaded file
            with open(file.name, 'r', encoding='utf-8') as f:
                new_data = json.load(f)

            # Validate data structure
            if not isinstance(new_data, list):
                return "פורמט קובץ שגוי - נדרשת רשימה של רגולציות"

            # Rebuild index with new data
            self.rag_system.build_index(file.name)

            return f"הועלו בהצלחה {len(new_data)} רגולציות חדשות"

        except Exception as e:
            return f"שגיאה בהעלאת הקובץ: {str(e)}"

    def get_system_stats(self) -> str:
        """Get system statistics."""
        try:
            total_chunks = len(self.rag_system.chunks)

            categories = {}
            authorities = {}

            for chunk in self.rag_system.chunks:
                categories[chunk.category] = categories.get(chunk.category, 0) + 1
                authorities[chunk.source_authority] = authorities.get(chunk.source_authority, 0) + 1

            stats = [
                f"**סה\"כ רגולציות במערכת:** {total_chunks}",
                "",
                "**התפלגות לפי קטגוריות:**"
            ]

            for category, count in categories.items():
                stats.append(f"• {category}: {count}")

            stats.extend([
                "",
                "**התפלגות לפי רשויות:**"
            ])

            for authority, count in authorities.items():
                stats.append(f"• {authority}: {count}")

            return "\n".join(stats)

        except Exception as e:
            return f"שגיאה בקבלת סטטיסטיקות: {str(e)}"


def create_gradio_interface():
    """Create and configure the Gradio interface."""
    chat_app = RegulatoryChat()

    # Custom CSS for Hebrew RTL support
    css = """
    .message.user p, .message.bot p {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .gradio-container {
        direction: rtl;
    }

    .message {
        direction: rtl !important;
    }

    textarea {
        direction: rtl;
        text-align: right;
    }

    .markdown-text {
        direction: rtl;
        text-align: right;
    }
    """

    with gr.Blocks(
        title="רגו-ביז - יועץ רגולטורי חכם",
        css=css,
        theme=gr.themes.Default(primary_hue="blue")
    ) as demo:

        gr.Markdown("""
        # רגו-ביז - יועץ רגולטורי חכם 🏢
        ### מערכת AI לייעוץ רגולטורי עבור עסקים בישראל

        המערכת תאסוף את פרטי העסק שלכם באמצעות שיחה טבעית בעברית,
        ולאחר מכן תספק הנחיות רגולטוריות מותאמות אישית.

        **פשוט התחילו בשיחה - המערכת תנחה אתכם! 💬**
        """, rtl=True)

        with gr.Row():
            with gr.Column(scale=2):
                # Chat Interface (now primary)
                gr.Markdown("### שיחה עם היועץ הרגולטורי", rtl=True)

                chatbot = gr.Chatbot(
                    height=500,
                    label="שיחה",
                    rtl=True,
                    placeholder="כאן תופיע השיחה עם היועץ הרגולטורי"
                )

                msg = gr.Textbox(
                    label="כתבו כאן...",
                    placeholder="התחילו בכתיבת 'שלום' או ספרו על העסק שלכם...",
                    rtl=True,
                    max_lines=3
                )

                with gr.Row():
                    send_btn = gr.Button("שלח", variant="primary", size="lg")
                    clear_btn = gr.Button("התחל שיחה חדשה", variant="secondary")

                # Business Profile Status
                gr.Markdown("### סטטוס מידע העסק", rtl=True)

                profile_status = gr.Markdown(
                    value="🔄 המערכת תאסוף את פרטי העסק בזמן השיחה",
                    rtl=True
                )

            with gr.Column(scale=1):
                # Compliance Report Section
                gr.Markdown("### דוח ציות מפורט", rtl=True)

                report_btn = gr.Button("צור דוח ציות", variant="secondary")

                report_output = gr.Markdown(
                    label="דוח ציות",
                    value="הדוח יהיה זמין לאחר שמידע העסק יושלם בשיחה",
                    rtl=True
                )

                # System Statistics
                gr.Markdown("### סטטיסטיקות מערכת", rtl=True)

                stats_btn = gr.Button("הצג סטטיסטיקות")

                stats_output = gr.Markdown(
                    label="נתוני מערכת",
                    value="לחץ להצגת סטטיסטיקות",
                    rtl=True
                )

                # Data Upload Section
                gr.Markdown("### העלאת נתונים חדשים", rtl=True)

                file_upload = gr.File(
                    label="בחר קובץ JSON עם רגולציות",
                    file_types=[".json"]
                )

                upload_btn = gr.Button("העלה נתונים")

                upload_status = gr.Textbox(
                    label="סטטוס העלאה",
                    interactive=False
                )

        # Event handlers
        def respond(message, history):
            return chat_app.chat(message, history)

        def clear_chat():
            chat_app.session_started = False
            chat_app.business_profiler.reset()
            return [], "🔄 המערכת תאסוף את פרטי העסק בזמן השיחה"

        def update_profile_status(history):
            """Update profile status display based on current business info"""
            if not chat_app.business_profiler.business_info.is_complete:
                missing = chat_app.business_profiler.get_missing_info_summary()
                return f"⏳ עדיין חסרים: {', '.join(missing)}"
            else:
                profile = chat_app.business_profiler.get_business_profile_dict()
                status_parts = ["✅ מידע העסק הושלם:"]
                if "business_type" in profile:
                    status_parts.append(f"• סוג עסק: {profile['business_type']}")
                if "seating_capacity" in profile:
                    status_parts.append(f"• מקומות ישיבה: {profile['seating_capacity']}")
                if "size_sqm" in profile:
                    status_parts.append(f"• שטח: {profile['size_sqm']} מ\"ר")
                return "\n".join(status_parts)

        # Chat event handlers
        msg_submit = msg.submit(respond, [msg, chatbot], [msg, chatbot])
        msg_submit.then(lambda h: update_profile_status(h), [chatbot], [profile_status])

        btn_click = send_btn.click(respond, [msg, chatbot], [msg, chatbot])
        btn_click.then(lambda h: update_profile_status(h), [chatbot], [profile_status])

        clear_btn.click(clear_chat, [], [chatbot, profile_status], queue=False)

        # Compliance report
        report_btn.click(
            chat_app.generate_compliance_report,
            [],
            report_output
        )

        # Statistics
        stats_btn.click(
            chat_app.get_system_stats,
            [],
            stats_output
        )

        # File upload
        upload_btn.click(
            chat_app.upload_new_data,
            file_upload,
            upload_status
        )

        # Footer
        gr.Markdown("""
        ---
        **הערות חשובות:**
        - המערכת מספקת הנחיות כלליות ואינה מהווה תחליף לייעוץ משפטי מקצועי
        - במקרה של ספק או אי-בהירות, מומלץ לפנות לרשויות המוסמכות
        - המערכת מבוססת על נתונים עדכניים ולא מתחייבת לכלול את כל השינויים הרגולטוריים
        """, rtl=True)

    return demo


def main():
    """Main function to run the Gradio app."""
    try:
        # Check for required environment variables
        if not os.getenv("OPENAI_API_KEY"):
            print("Warning: OPENAI_API_KEY not found in environment variables")
            print("Please set your OpenAI API key before running the application")

        # Create and launch the interface
        demo = create_gradio_interface()

        # Launch with specific settings for Gradio Spaces
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            debug=True
        )

    except Exception as e:
        print(f"Error launching application: {e}")
        raise


if __name__ == "__main__":
    main()