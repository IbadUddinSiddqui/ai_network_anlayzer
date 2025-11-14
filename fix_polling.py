"""
Simple script to fix the polling section in frontend/app.py
Run this to remove the fetch button and simplify timeout message.
"""

# Read the file
with open('frontend/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the fetch button section
old_section_start = '                # Final poll for results if not already retrieved'
old_section_end = '                                    st.error(f"Failed to fetch results: {str(e)}")'

new_section = '''                # If timed out after 5 minutes
                if 'test_results' not in st.session_state:
                    st.error("❌ Test timed out after 5 minutes.")
                    st.info("💡 The test may still be running. Use the sidebar 'Refresh Results' button to check later.")'''

# Find the section
start_idx = content.find(old_section_start)
if start_idx != -1:
    end_idx = content.find(old_section_end, start_idx)
    if end_idx != -1:
        end_idx += len(old_section_end)
        # Replace
        content = content[:start_idx] + new_section + content[end_idx:]
        
        # Write back
        with open('frontend/app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed! Removed fetch button and simplified timeout message.")
        print("The UI will now wait up to 5 minutes for results.")
        print("If timeout occurs, user can use sidebar refresh button.")
    else:
        print("❌ Could not find end of section")
else:
    print("❌ Could not find start of section")
