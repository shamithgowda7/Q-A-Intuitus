# backend/mindmap_generator.py
import json
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables and configure Gemini
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# Configure Gemini with API key
genai.configure(api_key=api_key)

def generate_mindmap_outline(text, model="models/gemini-1.5-flash"):
    """
    Generate a mindmap outline from document text using Gemini API
    Returns a hierarchical JSON structure with "topic" and "children"
    """
    try:
        # Initialize Gemini model
        llm = genai.GenerativeModel(model)
        
        # Create prompt for mindmap generation
        prompt = f"""
        Analyze the following document and create a mindmap outline.
        Use a hierarchical JSON structure with "topic" and "children".
        The structure should be:
        {{
            "topic": "Main Topic",
            "children": [
                {{
                    "topic": "Subtopic 1",
                    "children": [
                        {{
                            "topic": "Detail 1",
                            "children": []
                        }}
                    ]
                }},
                {{
                    "topic": "Subtopic 2", 
                    "children": []
                }}
            ]
        }}

        Document:
        {text[:4000]}  # Keep to safe token limit
        
        Return ONLY the JSON structure, no additional text or explanations.
        """
        
        response = llm.generate_content(prompt)
        
        # Try to parse the JSON response
        try:
            # Clean the response text to extract JSON
            response_text = response.text.strip()
            
            # Remove any markdown formatting if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            outline = json.loads(response_text)
            
            # Validate the structure
            if not isinstance(outline, dict) or "topic" not in outline:
                raise ValueError("Invalid JSON structure")
                
            return outline
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {e}")
            print(f"Raw response: {response.text}")
            
            # Fallback: create a simple structure
            return {
                "topic": "Document Analysis",
                "children": [
                    {
                        "topic": "Key Points",
                        "children": [
                            {
                                "topic": response.text[:100] + "...",
                                "children": []
                            }
                        ]
                    }
                ]
            }
            
    except Exception as e:
        print(f"Error generating mindmap: {e}")
        # Return a fallback structure
        return {
            "topic": "Document",
            "children": [
                {
                    "topic": "Analysis Error",
                    "children": [
                        {
                            "topic": f"Could not generate mindmap: {str(e)}",
                            "children": []
                        }
                    ]
                }
            ]
        }

def generate_study_mindmap(text, model="models/gemini-1.5-flash"):
    """
    Generate a study-focused mindmap outline from document text
    """
    try:
        llm = genai.GenerativeModel(model)
        
        prompt = f"""
        Analyze the following document and create a study-focused mindmap outline.
        Structure it for learning and memorization with clear topics, subtopics, and key concepts.
        Use this JSON format:
        {{
            "topic": "Main Subject",
            "children": [
                {{
                    "topic": "Chapter/Topic 1",
                    "children": [
                        {{
                            "topic": "Key Concept 1",
                            "children": [
                                {{
                                    "topic": "Important Detail",
                                    "children": []
                                }}
                            ]
                        }}
                    ]
                }}
            ]
        }}

        Document:
        {text[:4000]}
        
        Focus on:
        - Main themes and topics
        - Key concepts and definitions
        - Important relationships
        - Study points and takeaways
        
        Return ONLY the JSON structure.
        """
        
        response = llm.generate_content(prompt)
        
        try:
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
                
            outline = json.loads(response_text)
            
            if not isinstance(outline, dict) or "topic" not in outline:
                raise ValueError("Invalid JSON structure")
                
            return outline
            
        except json.JSONDecodeError:
            return {
                "topic": "Study Guide",
                "children": [
                    {
                        "topic": "Key Learning Points",
                        "children": [
                            {
                                "topic": response.text[:100] + "...",
                                "children": []
                            }
                        ]
                    }
                ]
            }
            
    except Exception as e:
        return {
            "topic": "Study Document",
            "children": [
                {
                    "topic": "Error",
                    "children": [
                        {
                            "topic": f"Could not generate study mindmap: {str(e)}",
                            "children": []
                        }
                    ]
                }
            ]
        }
