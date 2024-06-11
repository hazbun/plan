import json
import requests
import re

# Define your Todoist API token
TODOIST_API_TOKEN = '916fbd9c0c13bbc8484cf0cde5843fa2716e0890'

# Function to read the assignments from the JS file
def read_assignments_from_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        
    # Extract JSON-like structure from the JS file content
    assignments_json_str = re.search(r'assignments\s*=\s*({.*});', content, re.DOTALL).group(1)
    assignments = json.loads(assignments_json_str)
    
    return assignments
# Function to get all sections from a Todoist project
def get_todoist_sections(project_id):
    response = requests.get(
        f"https://api.todoist.com/rest/v2/sections?project_id={project_id}",headers={"Authorization": f"Bearer {TODOIST_API_TOKEN}"})
    return response.json()

# Function to create a new section in Todoist
def create_todoist_section(project_id, section_name):
    response = requests.post(
        "https://api.todoist.com/rest/v2/sections",
        json={"name": section_name, "project_id": project_id},
        headers={"Authorization": f"Bearer {TODOIST_API_TOKEN}"}
    )
    return response.json()

# Function to get all tasks from a Todoist project
def get_todoist_tasks(project_id):
    response = requests.get(
        f"https://api.todoist.com/rest/v2/tasks?project_id={project_id}",
        headers={"Authorization": f"Bearer {TODOIST_API_TOKEN}"}
    )
    return response.json()

# Function to create a new task in Todoist
def create_todoist_task(content, project_id, section_id, due_date, url):
    response = requests.post(
        "https://api.todoist.com/rest/v2/tasks",
        json={
            "content": content,
            "project_id": project_id,
            "section_id": section_id,
            "due_string": due_date,
            "description": url
        },
        headers={"Authorization": f"Bearer {TODOIST_API_TOKEN}"}
    )
    return response.json()

# Main integration logic
def main():
    project_id = '2301873247' 

    # Read assignments from file
    file_path = 'data/assignments.js'
    assignments = read_assignments_from_file(file_path)

    # Get existing sections and tasks
    existing_sections = get_todoist_sections(project_id)
    existing_tasks = get_todoist_tasks(project_id)
    
    # Create a set of existing section names
    existing_section_names = {section['name'] for section in existing_sections}

    # Create a set of existing task names
    existing_task_names = {task['content'] for task in existing_tasks}
    print(existing_task_names)

    # Iterate over courses and assignments
    for course, course_assignments in assignments.items():
        course = course[10:16]
        # Check if section exists for the course, if not, create it
        if course not in existing_section_names:
            create_todoist_section(project_id, course)
            existing_sections = get_todoist_sections(project_id)  # Update sections
            existing_section_names = {section['name'] for section in existing_sections}

        # Get the section ID for the course
        section_id = next((section['id'] for section in existing_sections if section['name'] == course), None)

        # Iterate over assignments
        for assignment in course_assignments:
            if not assignment['submitted']:
                task_name = assignment['title']
                # Check if the task already exists, if not, create it
                if task_name not in existing_task_names:
                    create_todoist_task(task_name, project_id, section_id, assignment['dueDate'], assignment['link'])

if __name__ == "__main__":
    main()
