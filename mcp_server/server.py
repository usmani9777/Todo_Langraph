# from mcp.server.fastmcp import FastMCP
# import asyncio
# import datetime

# mcp = FastMCP("todo manager")

# @mcp.tool()
# def add_todo_item(item: str)->str:

#     """
#     Adds a new todo item to the list.
#     Args:
#         item (str): The todo item to add.
#     Returns:
#         str: A confirmation message.
#     """
#     with open("todo_list.txt", "a") as f:
#         f.write(item + "\n")
#     return f"Added todo item: {item}"

# @mcp.tool()
# def get_todo_list()->str:
#     """
#     Docstring for get_todo_list
    
#     :return: Description
#     :rtype: str
#     """
#     with open("todo_list.txt", "r") as f:
#         return f.read()

# @mcp.tool()
# def get_time()->str:
#     """
#     Docstring for get_time
    
#     :return: Description
#     :rtype: str
#     """
    
#     return datetime.datetime.now().isoformat()  


# @mcp.tool()
# def delete_todo_item(item: str)->str:
#     """
#     Docstring for delete_todo_item
    
#     :param item: Description
#     :type item: str
#     :return: Description
#     :rtype: str
#     """
#     with open("todo_list.txt", "r") as f:
#         items = f.readlines()
    
#     with open("todo_list.txt", "w") as f:
#         for i in items:
#             if i.strip() != item:
#                 f.write(i)
    
#     return f"Deleted todo item: {item}" 

# if __name__ == "__main__":
#     mcp.run(transport="sse")


from mcp.server.fastmcp import FastMCP
import datetime
import os

mcp = FastMCP("todo_manager")
TODO_FILE = "todo_list.txt"

# Ensure file exists so get_todo_list doesn't crash
if not os.path.exists(TODO_FILE):
    with open(TODO_FILE, "w") as f:
        f.write("")

@mcp.tool()
def add_todo_item(item: str) -> str:
    """Adds a new task to the todo list. Use this whenever the user wants to remember something."""
    with open(TODO_FILE, "a") as f:
        f.write(item + "\n")
    return f"Successfully added: {item}"

@mcp.tool()
def get_todo_list() -> str:
    """Retrieves all current tasks in the todo list. Use this to see what needs to be done."""
    with open(TODO_FILE, "r") as f:
        content = f.read()
    return content if content else "The list is currently empty."

@mcp.tool()
def get_time() -> str:
    """Returns the current system time. Use this to calculate how long tasks have been pending."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@mcp.tool()
def delete_todo_item(item: str) -> str:
    """Removes a specific task from the list. The 'item' must match the text in the list exactly."""
    if not os.path.exists(TODO_FILE):
        return "List is empty."
    
    with open(TODO_FILE, "r") as f:
        items = f.readlines()
    
    new_items = [i for i in items if i.strip() != item.strip()]
    
    with open(TODO_FILE, "w") as f:
        for i in new_items:
            f.write(i)
    
    return f"Deleted: {item}"

if __name__ == "__main__":
    print("this mcp server")
    # Change to "stdio" if running locally via a bridge, 
    # or keep "sse" if running as a standalone web server.
    mcp.run(transport="sse")